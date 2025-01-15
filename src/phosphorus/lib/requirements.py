from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

from phosphorus.lib.markers import Marker
from phosphorus.lib.packages import Package
from phosphorus.lib.regex import requirement_pattern
from phosphorus.lib.versions import VersionClause

if TYPE_CHECKING:
    from typing_extensions import Self  # upgrade: py3.10: import from typing


@dataclass(frozen=True, order=True)  # upgrade: py3.9: Use slots=True
class Requirement:
    package: Package
    clauses: tuple[VersionClause, ...]
    marker: Marker

    @classmethod
    def from_string(cls, requirement: str) -> Self:
        clause, *markers = requirement.split(";", maxsplit=1)
        marker = (
            Marker.from_string(markers[0].strip())
            if markers
            else Marker(boolean=None, markers=())
        )
        full_match = re.fullmatch(requirement_pattern, clause.strip())
        if not full_match:
            msg = "Could not parse the requirement"
            raise RuntimeError(msg)
        name = full_match["name"].strip()
        if full_match["clauses"]:
            clauses = tuple(
                VersionClause.from_string(matched_clause)
                for matched_clause in full_match["clauses"].strip(" ()").split(",")
            )
        else:
            clauses = ()
        return cls(package=Package(name=name), clauses=clauses, marker=marker)

    def __str__(self) -> str:
        parts = [self.package.name]
        if self.clauses:
            clauses = ",".join(str(clause) for clause in self.clauses)
            parts.append(f"({clauses})")
        if self.marker:
            parts.append(f"; {self.marker}")
        return " ".join(parts)
