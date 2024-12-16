from __future__ import annotations

import sys
from argparse import Namespace
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING
from warnings import warn

from phosphorus.lib.constants import hash_prefix
from phosphorus.lib.markers import Marker
from phosphorus.lib.packages import Package
from phosphorus.lib.requirements import ResolvedRequirement
from phosphorus.lib.resolver import LockEntry
from phosphorus.lib.subprocess import uv_run
from phosphorus.lib.term import SGRParams, SGRString, write
from phosphorus.lib.versions import Version
from phosphorus.subcommands.base import BaseCommand
from phosphorus.subcommands.lock import LockCommand

if TYPE_CHECKING:
    from phosphorus.lib.types import PackageDiff


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
            write(["❌ Installation failed: ", exc], is_error=True)
            sys.exit(1)
        else:
            write(["✅ Success: Installation finished successfully!"])

    def install(self) -> None:
        if not self.groups:
            msg = "No remaining valid groups"
            raise RuntimeError(msg)

        if not self.meta.lockfile.exists():
            write(["🔒 Lockfile not found, creating one..."])
            LockCommand(
                Namespace(
                    verbosity=self.verbosity,
                    enforce_pep440=True,
                    allow_pre_releases=False,
                    allow_dev_releases=False,
                    force=False,
                )
            ).run()

        package_diff = self.get_package_diff()

        if package_diff["update"]:
            write(["📦 Installing packages..."])
        else:
            write(["📦 No packages to be updated, skipping..."])
        for old_package, lock_entry in package_diff["update"]:
            self.install_package(old_package, lock_entry)
        if self.sync:
            if package_diff["remove"]:
                write(["🧹 Removing packages..."])
            else:
                write(["🧹 No packages to be removed, skipping..."])
            for old_package in package_diff["remove"]:
                self.remove_package(old_package)
        self.install_self()

    def get_groups(self, included: set[str], excluded: set[str]) -> set[str]:
        all_groups = {group.group for group in self.meta.requirement_groups}
        if included:
            if not included.issubset(all_groups):
                msg = f"Unknown group(s) {included - all_groups}, ignoring..."
                warn(msg, RuntimeWarning, stacklevel=3)
            return included & all_groups
        if not excluded.issubset(all_groups):
            msg = f"Unknown group(s) {excluded - all_groups}, ignoring..."
            warn(msg, RuntimeWarning, stacklevel=3)
        return all_groups - excluded

    def get_package_diff(self) -> PackageDiff:
        write(["🔎 Looking for packages to install/remove/upgrade..."])

        output = uv_run(
            ["pip", "freeze", "--exclude-editable"], verbose=self.verbosity > 0
        )
        existing_venv = {
            resolved_requirement.package: resolved_requirement
            for requirement in output.stdout.decode().splitlines()
            if (resolved_requirement := ResolvedRequirement.from_string(requirement))
        }

        lock = self.meta.lockfile_content

        target_venv = {}
        for lock_entry in lock["packages"]:
            marker = Marker.from_string(lock_entry.get("marker", ""))
            if not marker.evaluate(verbose=self.verbosity > 0):
                continue
            if not self.groups & set(lock_entry["groups"]):
                continue
            package = Package(lock_entry["name"])
            entry = LockEntry(
                requirement=ResolvedRequirement(
                    package=package,
                    version=Version.from_string(lock_entry["version"]),
                    marker=marker,
                ),
                groups=tuple(lock_entry["groups"]),
                hashes=tuple(lock_entry["hashes"]),
            )
            target_venv[package] = entry

        update: set[tuple[ResolvedRequirement | None, LockEntry]] = set()
        remove = set()

        for package in existing_venv | target_venv:
            if package not in target_venv:
                remove.add(existing_venv[package])
            elif package not in existing_venv:
                update.add((None, target_venv[package]))
            else:
                existing = existing_venv[package]
                target = target_venv[package]
                if existing.version != target.requirement.version:
                    update.add((existing, target))

        return {"update": update, "remove": remove}

    def install_package(
        self, old_package: ResolvedRequirement | None, lock_entry: LockEntry
    ) -> None:
        package = lock_entry.requirement.package
        old_version = old_package.version if old_package else None
        new_version = lock_entry.requirement.version
        hashes = " ".join(
            f"{hash_prefix}{hashed_file}" for hashed_file in lock_entry.hashes
        )
        if not old_version:
            action = "Installing"
            version = str(new_version)
        elif old_version < new_version:
            action = "Upgrading"
            version = f"{old_version} → {new_version}"
        else:
            action = "Downgrading"
            version = f"{old_version} → {new_version}"
        write(
            [
                "⏳ ",
                action,
                " ",
                SGRString(str(package), params=[SGRParams.CYAN]),
                " (",
                SGRString(version, params=[SGRParams.BLUE_BRIGHT]),
                ")...",
            ],
            end=" ",
        )
        with NamedTemporaryFile("w", delete=False) as tmp:
            line = f"{package}=={new_version} {hashes}"
            tmp.write(f"{line}\n")
            tmp.seek(0)
            uv_run(
                ["pip", "install", "--no-deps", "--require-hashes", "-r", tmp.name],
                verbose=self.verbosity > 0,
            )
            write(["🗸"])

    def remove_package(self, old_package: ResolvedRequirement) -> None:
        package = old_package.package
        version = old_package.version
        write(
            [
                "⏳ Removing ",
                SGRString(str(package), params=[SGRParams.CYAN]),
                " (",
                SGRString(str(version), params=[SGRParams.BLUE_BRIGHT]),
                ")...",
            ],
            end=" ",
        )
        uv_run(["pip", "uninstall", package.name], verbose=self.verbosity > 0)
        write(["🗸"])

    def install_self(self) -> None:
        write(
            [
                "⏳ Installing ",
                SGRString(str(self.meta.package), params=[SGRParams.CYAN]),
                " (",
                SGRString(str(self.meta.version), params=[SGRParams.BLUE_BRIGHT]),
                ")...",
            ],
            end=" ",
        )
        uv_run(
            ["pip", "install", "--no-deps", "--editable", "."],
            verbose=self.verbosity > 0,
        )
        write(["🗸"])
