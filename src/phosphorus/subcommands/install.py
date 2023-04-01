import sys
import tomllib
from argparse import Namespace
from subprocess import run
from tempfile import NamedTemporaryFile
from warnings import warn

from phosphorus.lib.constants import hash_prefix
from phosphorus.lib.exceptions import PipError
from phosphorus.lib.markers import Marker
from phosphorus.lib.term import SGRParams, SGRString
from phosphorus.subcommands.base import BaseCommand
from phosphorus.subcommands.lock import LockCommand


class InstallCommand(BaseCommand):
    __slots__ = ("groups", "sync")

    def __init__(self, args: Namespace, /) -> None:
        super().__init__(args)
        self.sync = args.sync
        self.groups = self.get_groups(set(args.groups), set(args.exclude))

    def run(self) -> None:
        try:
            self.install()
        except RuntimeError as exc:
            print(f"❌ Installation failed: {exc}", file=sys.stderr)
            sys.exit(1)
        else:
            print("✅ Success: Installation finished successfully!")

    def install(self) -> None:
        if not self.groups:
            msg = "No remaining valid groups"
            raise RuntimeError(msg)

        if not self.meta.lockfile.exists():
            print("🔒 Lockfile not found, creating one...")
            LockCommand(
                Namespace(
                    enforce_pep440=True,
                    allow_pre_releases=False,
                    allow_dev_releases=False,
                    force=False,
                )
            ).run()

        with self.meta.lockfile.open("rb") as lockfile:
            lock = tomllib.load(lockfile)

        print("📦 Installing packages...")
        for lock_entry in lock["packages"]:
            marker = Marker.from_string(lock_entry.get("marker", ""))
            if not marker.evaluate():
                continue
            if not self.groups & set(lock_entry["groups"]):
                continue
            name = lock_entry["name"]
            version = lock_entry["version"]
            requirement = f"{name}=={version}"
            hashes = " ".join(
                f"{hash_prefix}{hashed_file}" for hashed_file in lock_entry["hashes"]
            )
            line = f"{requirement} {hashes}"
            with NamedTemporaryFile("w", delete=False) as tmp:
                tmp.write(f"{line}\n")
                print(
                    f"⏳ Installing {SGRString(name, params=[SGRParams.CYAN])} "
                    f"({SGRString(version, params=[SGRParams.BLUE_BRIGHT])})...",
                    end=" ",
                )
                output = run(  # noqa: PLW1510, S603
                    [  # noqa: S607
                        "pip",
                        "install",
                        "--no-deps",
                        "--no-input",
                        "-r",
                        tmp.name,
                    ],
                    capture_output=True,
                )
                if output.returncode == 0:
                    print("🗸")
                else:
                    print()
                    msg = f"Failed to install {requirement}"
                    raise PipError(msg)

    def get_groups(self, included: set[str], excluded: set[str]) -> set[str]:
        all_groups = {group.group for group in self.meta.requirement_groups}
        if included:
            if not included.issubset(all_groups):
                included &= all_groups
                msg = f"Unknown group(s) {included}, ignoring..."
                warn(msg, RuntimeWarning, stacklevel=3)
            return included
        if not excluded.issubset(all_groups):
            msg = f"Unknown group(s) {excluded - all_groups}, ignoring..."
            warn(msg, RuntimeWarning, stacklevel=3)
        return all_groups - excluded
