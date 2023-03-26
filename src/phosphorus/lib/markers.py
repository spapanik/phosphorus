from __future__ import annotations

import os
import platform
import sys
from dataclasses import dataclass
from typing import Any

from phosphorus.lib.types import MarkerBoolean, MarkerOperator, MarkerVariable
from phosphorus.lib.versions import Version, VersionClause

version_type_variables = {
    "python_version",
    "python_full_version",
    "implementation_version",
}
version_operators = {"<", "<=", ">=", ">", "~="}


@dataclass(frozen=True)
class MarkerAtom:
    variable: MarkerVariable
    operator: MarkerOperator
    value: str

    def __post_init__(self) -> None:
        if (
            self.variable not in version_type_variables
            and self.operator in version_operators
        ):
            msg = f"{self.operator} is not allowed with {self.variable}"
            raise ValueError(msg)

    def __str__(self) -> str:
        return f"{self.variable} {self.operator} '{self.value}'"

    def to_dict(self) -> dict[str, str]:
        return {
            "variable": self.variable,
            "operator": self.operator,
            "value": self.value,
        }

    def evaluate(self) -> bool:
        variable_value = env_vars[self.variable]
        if self.operator == "===":
            return variable_value == self.value

        if self.variable in version_type_variables:
            variable_version = Version.from_string(variable_value)
            value_version = Version.from_string(variable_value)
            clause = VersionClause(operator=self.operator, identifier=value_version)  # type: ignore[arg-type]
            return clause.match(variable_version)

        return True


@dataclass(frozen=True)
class Marker:
    boolean: MarkerBoolean | None
    markers: tuple[Marker | MarkerAtom, ...]

    @classmethod
    def from_string(cls, marker_string: str) -> Marker:
        if not marker_string:
            return cls(boolean=None, markers=())

        from packaging._parser import (  # type: ignore[attr-defined]
            DEFAULT_RULES,
            Tokenizer,
            _parse_marker,
        )
        from packaging.markers import _normalize_extra_values

        def translate_packaging(
            parsed_marker: list[Any] | tuple[Any],
        ) -> Marker | MarkerAtom:
            if isinstance(parsed_marker, tuple):
                variable, op, value = parsed_marker  # type: ignore[misc]
                return MarkerAtom(
                    variable=variable.value,  # type: ignore[has-type]
                    operator=op.value,  # type: ignore[has-type]
                    value=value.value,  # type: ignore[has-type]
                )
            if len(parsed_marker) == 1:
                return Marker(
                    boolean=None, markers=(translate_packaging(parsed_marker[0]),)
                )

            return Marker(
                boolean=parsed_marker[1],
                markers=tuple(
                    translate_packaging(sub_marker)
                    for sub_marker in parsed_marker
                    if not isinstance(sub_marker, str)
                ),
            )

        token = Tokenizer(marker_string, rules=DEFAULT_RULES)
        parsed_marker = _parse_marker(token)
        normalised_marker = _normalize_extra_values(parsed_marker)
        marker = translate_packaging(normalised_marker)

        if isinstance(marker, MarkerAtom):
            return Marker(boolean=None, markers=(marker,))
        return marker

    def __str__(self) -> str:
        if not self.markers:
            return ""

        if not self.boolean:
            return str(self.markers[0])

        parts = [
            str(marker) for marker in self.markers if isinstance(marker, MarkerAtom)
        ]
        parts.extend(
            f"({marker})"
            for marker in self.markers
            if not isinstance(marker, MarkerAtom)
        )
        joiner = f" {self.boolean} "
        return joiner.join(parts)

    @classmethod
    def from_dict(cls, specs: dict[str, Any]) -> Marker:
        boolean = specs.get("boolean")
        markers: list[Marker | MarkerAtom] = []
        for marker in specs["markers"]:
            if marker.get("variable"):
                markers.append(MarkerAtom(**marker))
            else:
                markers.append(cls.from_dict(marker))

        return Marker(boolean=boolean, markers=tuple(markers))

    def to_dict(self) -> dict[str, Any]:
        output: dict[str, Any] = {
            "markers": [marker.to_dict() for marker in self.markers]
        }
        if self.boolean:
            output["boolean"] = self.boolean

        return output

    def evaluate(self) -> bool:
        if not self.markers:
            return True

        if self.boolean == "or":
            return any(marker.evaluate for marker in self.markers)
        if self.boolean == "and":
            return all(marker.evaluate for marker in self.markers)

        return self.markers[0].evaluate()


def format_full_version(info: sys._version_info) -> str:  # noqa: SLF001
    version = f"{info.major}.{info.minor}.{info.micro}"
    kind = info.releaselevel
    return version if kind == "final" else f"{version}{kind[0]}{info.serial}"


env_vars = {
    "os_name": os.name,
    "sys_platform": sys.platform,
    "platform_release": platform.release(),
    "implementation_name": sys.implementation.name,
    "platform_machine": platform.machine(),
    "platform_python_implementation": platform.python_implementation(),
    "python_version": ".".join(platform.python_version_tuple()[:2]),
    "python_full_version": platform.python_version(),
    "platform_version": platform.version(),
    "implementation_version": format_full_version(sys.implementation.version),
}
