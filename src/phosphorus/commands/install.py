from __future__ import annotations

from argparse import Namespace
from subprocess import run
from tempfile import NamedTemporaryFile
from warnings import warn

from phosphorus._seven import toml_parser
from phosphorus.commands.base import BaseCommand
from phosphorus.commands.lock import LockCommand
from phosphorus.lib.exceptions import PipError
from phosphorus.lib.markers import Marker


class InstallCommand(BaseCommand):
    __slots__ = [*BaseCommand.__slots__, "groups", "sync"]

    def __init__(self, args: Namespace, /):
        super().__init__(args)
        self.sync = args.sync
        self.groups = self.get_groups(set(args.groups), set(args.exclude))

    def __call__(self) -> None:
        if not self.groups:
            msg = "No remaining valid groups"
            raise RuntimeError(msg)

        if not self.meta.lockfile.exists():
            LockCommand(
                Namespace(
                    enforce_pep440=True,
                    allow_pre_releases=False,
                    allow_dev_releases=False,
                )
            )()

        with self.meta.lockfile.open("rb") as lockfile:
            lock = toml_parser(lockfile)

        requirements: list[str] = []
        for name, package_info in lock["packages"].items():
            marker = Marker.from_dict(package_info.get("marker", {"markers": []}))
            if not marker.evaluate():
                continue
            if not self.groups & set(package_info["groups"]):
                continue
            version = package_info["version"]
            requirement = f"{name}=={version}"
            hashes = " ".join(
                f"--hash={file['hash']}" for file in package_info["files"]
            )
            requirements.append(f"{requirement} {hashes}")

        with NamedTemporaryFile("w", delete=False) as tmp:
            for requirement in requirements:
                tmp.write(f"{requirement}\n")
            tmp.seek(0)
            output = run(["pip", "install", "--no-deps", "--no-input", "-r", tmp.name])
            if output.returncode != 0:
                msg = "Failed to install packages"
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
