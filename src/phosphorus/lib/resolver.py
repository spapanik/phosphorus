from __future__ import annotations

from dataclasses import dataclass
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING

from phosphorus._seven import remove_prefix
from phosphorus.lib.constants import hash_prefix
from phosphorus.lib.exceptions import ThirdPartyError
from phosphorus.lib.packages import Package
from phosphorus.lib.requirements import ResolvedRequirement
from phosphorus.lib.uv_runner import uv_run

if TYPE_CHECKING:
    from collections.abc import Iterator

    from phosphorus.lib.requirements import RequirementGroup
    from phosphorus.lib.types import ResolvedPackageInfo


@dataclass(frozen=True, order=True)  # TODO (py3.9): Use slots=True
class LockEntry:
    requirement: ResolvedRequirement
    groups: tuple[str, ...]
    hashes: tuple[str, ...]


class Resolver:
    __slots__ = (
        "requirement_groups",
        "enforce_pep440",
        "allow_pre_releases",
        "allow_dev_releases",
        "packages",
        "resolved_packages",
        "verbosity",
    )

    def __init__(
        self,
        requirement_groups: tuple[RequirementGroup, ...],
        *,
        verbosity: int,
        enforce_pep440: bool,
        allow_pre_releases: bool,
        allow_dev_releases: bool,
    ) -> None:
        self.requirement_groups = requirement_groups
        self.enforce_pep440 = enforce_pep440
        self.allow_pre_releases = allow_pre_releases
        self.allow_dev_releases = allow_dev_releases
        self.verbosity = verbosity
        self.packages = {
            requirement.package: requirement_group.group
            for requirement_group in self.requirement_groups
            for requirement in requirement_group.requirements
        }
        self.resolved_packages: dict[Package, ResolvedPackageInfo] = {}

    def resolve(self) -> list[LockEntry]:
        with NamedTemporaryFile("w", delete=False) as tmp:
            for group in self.requirement_groups:
                for requirement in group.requirements:
                    tmp.write(f"{requirement}\n")
            tmp.seek(0)
            output = uv_run(
                ["pip", "compile", "--generate-hashes", "--universal", tmp.name]
            )
            if output.returncode:
                if self.verbosity:
                    print(output.stderr.decode())
                command = "uv pip compile"
                raise ThirdPartyError(command)
            print("✅ Done!")

        for raw_package_info in self.split_resolution(output.stdout.decode()):
            self.preprocess(raw_package_info)

        return [
            self.get_lock_entry(resolved_package)
            for resolved_package in self.resolved_packages.values()
        ]

    @staticmethod
    def split_resolution(resolution: str) -> Iterator[list[str]]:
        lines: list[str] = []
        should_yield = False
        for line in resolution.splitlines():
            stripped = line.strip(" \\")
            if not stripped:
                pass
            elif stripped.startswith("#"):
                lines.append(stripped)
                should_yield = True
            else:
                if should_yield:
                    if lines:
                        if any(not line.startswith("#") for line in lines):
                            yield lines
                        lines = []
                    should_yield = False
                lines.append(stripped)
        if lines and any(not line.startswith("#") for line in lines):
            yield lines

    def preprocess(self, raw_package_info: list[str]) -> None:
        requirement = ResolvedRequirement.from_string(raw_package_info[0])
        parents = {
            Package(name=stripped)
            for line in raw_package_info
            if line.startswith("#")
            and (stripped := remove_prefix(line, "# via").lstrip(" #"))
            and not stripped.startswith("-r /tmp")
        }

        self.resolved_packages[requirement.package] = {
            "requirement": requirement,
            "hashes": tuple(
                file_hash[len(hash_prefix) :]
                for file_hash in raw_package_info[1:]
                if file_hash.startswith(hash_prefix)
            ),
            "parents": parents,
        }

    def get_lock_entry(self, resolved_package: ResolvedPackageInfo) -> LockEntry:
        group = self.packages.get(resolved_package["requirement"].package, "")
        groups = {group} if group else set()
        parents = resolved_package["parents"].copy()
        seen = set()
        while parents:
            parent = parents.pop()
            if parent in seen:
                continue
            seen.add(parent)
            if group := self.packages.get(parent, ""):
                groups.add(group)
                continue
            parents.update(self.resolved_packages[parent]["parents"])
        return LockEntry(
            requirement=resolved_package["requirement"],
            groups=tuple(sorted(groups)),
            hashes=resolved_package["hashes"],
        )
