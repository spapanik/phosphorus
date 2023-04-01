from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from phosphorus.lib.packages import Package
    from phosphorus.lib.requirements import ResolvedRequirement
    from phosphorus.lib.resolver import LockEntry

Match = str | None


class ResolvedPackageInfo(TypedDict):
    requirement: ResolvedRequirement
    hashes: tuple[str, ...]
    parents: set[Package]


class PackageDiff(TypedDict):
    update: set[tuple[ResolvedRequirement | None, LockEntry]]
    remove: set[ResolvedRequirement]
