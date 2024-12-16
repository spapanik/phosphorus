from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Protocol, TypedDict, Union

if TYPE_CHECKING:
    from typing_extensions import Self  # upgrade: py3.10: import from typing

    from phosphorus.lib.packages import Package
    from phosphorus.lib.requirements import ResolvedRequirement
    from phosphorus.lib.resolver import LockEntry
    from phosphorus.lib.versions import Version

Match = Optional[str]  # upgrade: py3.9: Use |
JsonType = Union[  # upgrade: py3.9: Use |
    None, bool, int, float, str, list["JsonType"], dict[str, "JsonType"]
]


class Comparable(Protocol):
    def __eq__(self, other: object) -> bool: ...
    def __lt__(self, other: Self) -> bool: ...


class ResolvedPackageInfo(TypedDict):
    requirement: ResolvedRequirement
    hashes: tuple[str, ...]
    parents: set[Package]


class PackageDiff(TypedDict):
    update: set[tuple[ResolvedRequirement | None, LockEntry]]
    remove: set[ResolvedRequirement]


class InstalledVersions(TypedDict, total=False):
    package: Package
    installed_version: Version
    latest_version: Version


class LockfileMeta(TypedDict):
    version: str
    hash: str


class LockfilePackage(TypedDict):
    name: str
    version: str
    groups: list[str]
    marker: str
    hashes: list[str]


Lockfile = TypedDict(
    "Lockfile", {"$meta": LockfileMeta, "packages": list[LockfilePackage]}
)


class VersionInfoDict(TypedDict, total=False):
    ETag: str
    requires_dist: list[str]
    requires_python: str
    yanked: bool
    package: str
    version: str
    releases: list[str]


PhosphorusSettings = TypedDict(
    "PhosphorusSettings",
    {
        "dev-dependencies": dict[str, list[str]],
        "dynamic": dict[str, dict[str, str]],
        "packages": dict[str, list[str]],
    },
    total=False,
)


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
        "readme": Union[str, FileSettings],
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


class MetadataSettings(ProjectSettings, total=False):
    dev_dependencies: dict[str, list[str]]
    dynamic_definitions: dict[str, dict[str, str]]
    included_packages: dict[str, list[str]]
