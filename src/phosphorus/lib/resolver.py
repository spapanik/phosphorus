from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from subprocess import run
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING, Self

from phosphorus.lib.constants import hash_prefix
from phosphorus.lib.exceptions import PipError
from phosphorus.lib.requirements import Requirement

if TYPE_CHECKING:
    from collections.abc import Iterator

    from phosphorus.lib.markers import Marker
    from phosphorus.lib.packages import Package, PackageVersionInfo
    from phosphorus.lib.requirements import RequirementGroup
    from phosphorus.lib.versions import Version


@dataclass(frozen=True, slots=True, order=True)
class LockEntry:
    package: Package
    version: Version
    groups: list[str]
    hashes: list[str]
    marker: Marker

    @classmethod
    def from_resolution(cls, resolution: list[str]) -> Self:
        requirement = Requirement.from_string(resolution[0])
        clause = requirement.clauses[0]
        return cls(
            package=requirement.package,
            version=clause.identifier,
            groups=["main"],
            hashes=[
                file_hash[len(hash_prefix) :]
                for file_hash in resolution[1:]
                if file_hash.startswith(hash_prefix)
            ],
            marker=requirement.marker,
        )


class Resolver:
    __slots__ = (
        "requirement_groups",
        "enforce_pep440",
        "allow_pre_releases",
        "allow_dev_releases",
        "timestamp",
        "base_dependencies",
        "versions",
        "version_info",
    )

    def __init__(
        self,
        requirement_groups: tuple[RequirementGroup, ...],
        *,
        enforce_pep440: bool,
        allow_pre_releases: bool,
        allow_dev_releases: bool,
    ) -> None:
        self.requirement_groups = requirement_groups
        self.enforce_pep440 = enforce_pep440
        self.allow_pre_releases = allow_pre_releases
        self.allow_dev_releases = allow_dev_releases
        self.timestamp = datetime.now(tz=UTC).timestamp()
        self.base_dependencies = [
            requirement
            for group in self.requirement_groups
            for requirement in group.requirements
        ]
        self.versions: dict[Package, list[Version]] = {}
        self.version_info: dict[tuple[Package, Version], PackageVersionInfo] = {}

    def resolve(self) -> list[LockEntry]:
        with NamedTemporaryFile("w", delete=False) as tmp:
            for dependency in self.base_dependencies:
                tmp.write(f"{dependency}\n")
            tmp.seek(0)
            output = run(  # noqa: PLW1510, S603
                [  # noqa: S607
                    "uv",
                    "pip",
                    "compile",
                    "--generate-hashes",
                    tmp.name,
                ],
                capture_output=True,
            )
            if output.returncode:
                print()
                msg = "Failed to resolve dependencies"
                raise PipError(msg)
            print("🗸")

        return [
            LockEntry.from_resolution(resolution)
            for resolution in self.split_resolution(output.stdout.decode())
        ]

    @staticmethod
    def split_resolution(resolution: str) -> Iterator[list[str]]:
        lines: list[str] = []
        for line in resolution.splitlines():
            stripped = line.strip(" \\")
            if not stripped or stripped.startswith("#"):
                if lines:
                    yield lines
                lines = []
            else:
                lines.append(stripped)
