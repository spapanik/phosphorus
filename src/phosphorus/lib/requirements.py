from __future__ import annotations

import re
from dataclasses import dataclass, field

from phosphorus.lib.markers import Marker
from phosphorus.lib.packages import Package
from phosphorus.lib.regex import requirement_pattern
from phosphorus.lib.versions import Version, VersionClause


@dataclass(frozen=True, order=True)  # TODO (py3.9): Use slots=True
class Requirement:
    package: Package
    clauses: tuple[VersionClause, ...]
    marker: Marker

    @classmethod
    def from_string(cls, requirement: str) -> Requirement:  # TODO (py3.10): Use Self
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
        name = self.package.name
        clauses = ",".join(str(clause) for clause in self.clauses)
        marker = str(self.marker)
        if clauses and marker:
            return f"{name} ({clauses}) ; {marker}"
        if clauses:
            return f"{name} ({clauses})"
        if marker:
            return f"{name} ; {marker}"
        return name


@dataclass(frozen=True, order=True)  # TODO (py3.9): Use slots=True
class RequirementGroup:
    group: str
    requirements: tuple[Requirement, ...]


@dataclass(frozen=True, order=True)  # TODO (py3.9): Use slots=True
class ResolvedRequirement:
    package: Package
    version: Version
    marker: Marker = field(default_factory=lambda: Marker(boolean=None, markers=()))

    @classmethod
    def from_string(
        cls, requirement: str
    ) -> ResolvedRequirement:  # TODO (py3.10): Use Self
        resolved_package, *markers = requirement.split(";", maxsplit=1)
        marker = (
            Marker.from_string(markers[0].strip())
            if markers
            else Marker(boolean=None, markers=())
        )
        name, matched_version = resolved_package.split("==")
        return cls(
            package=Package(name=name),
            version=Version.from_string(matched_version),
            marker=marker,
        )
