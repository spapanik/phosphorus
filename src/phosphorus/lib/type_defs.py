from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, TypedDict

if TYPE_CHECKING:
    from collections.abc import Sequence

    from typing_extensions import Self  # upgrade: py3.10: import from typing

Match = str | None
JsonType = None | bool | int | float | str | list["JsonType"] | dict[str, "JsonType"]


class Comparable(Protocol):  # noqa: PLW1641
    def __eq__(self, other: object) -> bool: ...
    def __lt__(self, other: Self) -> bool: ...


class PhosphorusSettings(TypedDict, total=False):
    dynamic: dict[str, dict[str, str]]
    packages: dict[str, list[str]]


class ToolSettings(TypedDict, total=False):
    phosphorus: PhosphorusSettings


class FileSettings(TypedDict, total=False):
    file: str
    text: str


class Author(TypedDict):
    name: str
    email: str


ProjectSettings = TypedDict(
    "ProjectSettings",
    {
        "authors": list[Author],
        "classifiers": list[str],
        "dependencies": list[str],
        "description": str,
        "dynamic": list[str],
        "entry-points": dict[str, str],
        "gui-scripts": dict[str, str],
        "keywords": list[str],
        "license": FileSettings,
        "maintainers": list[Author],
        "name": str,
        "optional-dependencies": dict[str, list[str]],
        "readme": str | FileSettings,
        "requires-python": str,
        "scripts": dict[str, str],
        "urls": dict[str, str],
        "version": str,
    },
    total=False,
)


class PyProjectSettings(TypedDict, total=False):
    project: ProjectSettings
    tool: ToolSettings


DependencyGroupDict = TypedDict("DependencyGroupDict", {"include-group": str})
DependencyGroupMember = str | DependencyGroupDict


class MetadataSettings(ProjectSettings, total=False):
    dependency_groups: dict[str, Sequence[DependencyGroupMember]]
    dynamic_definitions: dict[str, dict[str, str]]
    included_packages: dict[str, list[str]]
