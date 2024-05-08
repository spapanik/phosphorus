from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from phosphorus.lib.packages import Package
    from phosphorus.lib.requirements import ResolvedRequirement

Match = str | None


class ResolvedPackageInfo(TypedDict):
    requirement: ResolvedRequirement
    hashes: tuple[str, ...]
    parents: set[Package]
