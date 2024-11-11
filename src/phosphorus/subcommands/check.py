from __future__ import annotations

import json
import sys
from typing import TYPE_CHECKING

from phosphorus._seven import TOMLDecodeError
from phosphorus.lib.packages import Package, VersionedPackage
from phosphorus.lib.pypi import get_version_info
from phosphorus.lib.subprocess import uv_run
from phosphorus.lib.versions import Version
from phosphorus.subcommands.base import BaseCommand

if TYPE_CHECKING:
    from argparse import Namespace

    from phosphorus.lib.types import InstalledVersions


class CheckCommand(BaseCommand):
    __slots__ = ("outdated", "lockfile")

    def __init__(self, _args: Namespace, /) -> None:
        super().__init__(_args)
        self.lockfile = _args.lockfile
        self.outdated = _args.outdated

    def run(self) -> None:
        if not self.outdated and not self.lockfile:
            print("❌ No check selected", file=sys.stderr)
            sys.exit(2)
        if self.outdated:
            self.check_outdated()
        if self.lockfile:
            try:
                self.check_lockfile()
            except RuntimeError as exc:
                print(f"❌ Lockfile check failed: {exc}", file=sys.stderr)
                sys.exit(1)
            else:
                print(
                    "✅ Success: Lockfile is valid and up-to-date with pyproject.toml"
                )

    def check_lockfile(self) -> None:
        try:
            p_hash = self.get_current_hash()
        except FileNotFoundError as exc:
            msg = "No lockfile found"
            raise RuntimeError(msg) from exc
        except (KeyError, TOMLDecodeError) as exc:
            msg = "Lockfile is invalid"
            raise RuntimeError(msg) from exc

        if p_hash != self.meta.p_hash:
            msg = "Hashes don't match"
            raise RuntimeError(msg)

    def check_outdated(self) -> None:
        pip_list = uv_run(
            ["pip", "list", "--exclude-editable", "--format=json"],
            verbose=self.verbosity > 0,
        )
        installed_packages: list[InstalledVersions] = [
            {
                "package": Package(package_info["name"]),
                "installed_version": Version.from_string(package_info["version"]),
            }
            for package_info in json.loads(pip_list.stdout)
        ]
        version_info = get_version_info(
            packages=[
                VersionedPackage(package_info["package"])
                for package_info in installed_packages
            ],
        )
        outdated: list[InstalledVersions] = []
        for package_info in installed_packages:
            versioned_package = VersionedPackage(package_info["package"])
            latest_version = version_info[versioned_package].version
            installed_version = package_info["installed_version"]
            if latest_version != installed_version:
                outdated.append(
                    {
                        "package": package_info["package"],
                        "installed_version": installed_version,
                        "latest_version": latest_version,
                    }
                )
        if outdated:
            self.print_outdated(outdated)
        else:
            print("✅ All installed packages are up-to-date!")

    @staticmethod
    def print_outdated(outdated: list[InstalledVersions]) -> None:
        header = ("Package", "Installed version", "Latest version")
        max_package = len(header[0])
        max_installed = len(header[1])
        max_latest = len(header[2])

        rows = []
        for outdated_package in reversed(outdated):
            package = outdated_package["package"].name
            max_package = max(max_package, len(package))
            installed_version = str(outdated_package["installed_version"])
            max_installed = max(max_installed, len(installed_version))
            latest_version = str(outdated_package["latest_version"])
            max_latest = max(max_latest, len(latest_version))
            rows.append((package, installed_version, latest_version))

        print(
            header[0].center(max_package),
            " ",
            header[1].center(max_installed),
            " ",
            header[2].center(max_latest),
        )
        print(
            "-" * max_package,
            " ",
            "-" * max_installed,
            " ",
            "-" * max_latest,
        )
        for row in reversed(rows):
            print(
                row[0].ljust(max_package),
                " ",
                row[1].rjust(max_installed),
                " ",
                row[2].rjust(max_latest),
            )
