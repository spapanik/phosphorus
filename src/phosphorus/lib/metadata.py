from __future__ import annotations

import json
import os
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass
from importlib.machinery import SourceFileLoader
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypeVar, cast

from trove_classifiers import classifiers

from phosphorus._seven import toml_parser
from phosphorus.lib.constants import (
    BooleanOperator,
    ComparisonOperator,
    MarkerVariable,
    pyproject_base_name,
)
from phosphorus.lib.contributors import Contributor
from phosphorus.lib.exceptions import (
    ImproperlyConfiguredProjectError,
    MissingProjectRootError,
)
from phosphorus.lib.packages import Package
from phosphorus.lib.requirements import Requirement
from phosphorus.lib.tags import Tag
from phosphorus.lib.type_defs import (
    Author,
    Comparable,
    DependencyGroupMember,
    JsonType,
    MetadataSettings,
    PyProjectSettings,
)
from phosphorus.lib.versions import Version, VersionClause

if TYPE_CHECKING:
    from typing_extensions import Self  # upgrade: py3.10: import from typing


T = TypeVar("T", bound=Comparable)


@dataclass(frozen=True, order=True)  # upgrade: py3.9: Use slots=True
class Script:
    command: str
    entrypoint: str


@dataclass(frozen=True, order=True)  # upgrade: py3.9: Use slots=True
class ProjectURL:
    name: str
    url: str


@dataclass(frozen=True, order=True)  # upgrade: py3.9: Use slots=True
class LocalPackage:
    base_dir: Path
    path: Path

    @property
    def absolute_path(self) -> Path:
        return self.base_dir.joinpath(self.path)


class JSONEncoder(json.JSONEncoder):
    def __init__(self, *, base_dir: Path, **kwargs: Any) -> None:  # type: ignore[misc]  # noqa: ANN401
        self.base_dir = base_dir
        super().__init__(**kwargs)

    def default(self, o: object) -> JsonType:
        if isinstance(o, Path):  # upgrade: py3.9: Use match
            if o == Path(os.devnull):
                return os.devnull
            if o.is_absolute():
                return o.relative_to(self.base_dir).as_posix()
            return o.as_posix()
        if isinstance(o, ComparisonOperator):
            return str(o)
        if isinstance(o, BooleanOperator):
            return str(o)
        if isinstance(o, MarkerVariable):
            return str(o)

        return cast(JsonType, super().default(o))


@dataclass(frozen=True, order=True)  # upgrade: py3.9: Use slots=True
class Metadata:
    base_dir: Path
    package: Package
    version: Version
    summary: str
    homepage: str
    license: str
    readme: Path
    keywords: tuple[str, ...]
    tags: tuple[Tag, ...]
    authors: tuple[Contributor, ...]
    maintainers: tuple[Contributor, ...]
    python: tuple[VersionClause, ...]
    classifiers: tuple[str, ...]
    requirements: tuple[Requirement, ...]
    scripts: tuple[Script, ...]
    project_urls: tuple[ProjectURL, ...]
    package_paths: tuple[LocalPackage, ...]

    @classmethod
    def from_path(cls, path: Path | None = None) -> Self:
        settings_path = get_pyproject(path)
        settings = get_settings(settings_path)

        urls = settings.get("urls", {})
        python = settings["requires-python"]

        return cls(
            base_dir=settings_path.parent,
            package=get_package(settings),
            version=get_version(settings),
            summary=settings.get("description", ""),
            homepage=urls.get("homepage", ""),
            license=get_license(settings),
            readme=settings_path.parent.joinpath(get_readme(settings)),
            keywords=keep_unique(settings.get("keywords", [])),
            tags=(Tag(interpreter="py3", abi=None, platform="any"),),
            authors=get_contributors(settings.get("authors", [])),
            maintainers=get_contributors(settings.get("maintainers", [])),
            python=keep_unique(
                VersionClause.from_string(clause) for clause in python.split(",")
            ),
            classifiers=get_classifiers(settings.get("classifiers", [])),
            requirements=get_requirements(
                settings.get("dependencies", []), settings.get("dependency_groups", {})
            ),
            project_urls=keep_unique(
                ProjectURL(name=name, url=url)
                for name, url in urls.items()
                if name != "homepage"
            ),
            scripts=keep_unique(
                Script(command=command, entrypoint=entrypoint)
                for command, entrypoint in settings.get("scripts", {}).items()
            ),
            package_paths=get_package_paths(settings, settings_path.parent),
        )

    @property
    def pyproject(self) -> Path:
        return self.base_dir.joinpath(pyproject_base_name)


def keep_unique(items: Iterable[T]) -> tuple[T, ...]:
    return tuple(sorted(set(items)))


def get_pyproject(cwd: Path | None) -> Path:
    if cwd is None:
        cwd = Path.cwd().resolve()

    while not (pyproject := cwd.joinpath(pyproject_base_name)).is_file():
        if cwd.as_posix() == "/":
            raise MissingProjectRootError(cwd)
        cwd = cwd.parent
    return pyproject


def get_contributors(settings: list[Author]) -> tuple[Contributor, ...]:
    return tuple(Contributor.from_data(data) for data in settings)


def get_readme(settings: MetadataSettings) -> Path:
    readme = settings.get("readme", os.devnull)
    if isinstance(readme, dict):
        return Path(readme["file"])
    return Path(readme)


def get_settings(settings_path: Path) -> MetadataSettings:
    with settings_path.open("rb") as settings_file:
        all_settings = cast(PyProjectSettings, toml_parser(settings_file))
    settings = cast(MetadataSettings, all_settings.get("project", {}))
    settings["dependency_groups"] = cast(
        dict[str, Sequence[DependencyGroupMember]],
        all_settings.get("dependency-groups", {}),
    )
    phosphorus_settings = all_settings.get("tool", {}).get("phosphorus", {})
    settings["dynamic_definitions"] = phosphorus_settings.get("dynamic", {})
    settings["included_packages"] = phosphorus_settings.get("packages", {})
    return settings


def get_package(settings: MetadataSettings) -> Package:
    return Package(name=settings["name"])


def get_version(settings: MetadataSettings) -> Version:
    version_key = "version"
    version = cast(str, settings.get(version_key))
    if version:
        return Version.from_string(version)
    try:
        version = settings["dynamic_definitions"][version_key]["file"]
    except KeyError as exc:
        raise ImproperlyConfiguredProjectError(version_key) from exc
    name = "_module"
    _module = SourceFileLoader(name, version).load_module(name)
    version = _module.__version__
    return Version.from_string(version)


def get_license(settings: MetadataSettings) -> str:
    license_info = settings.get("license", {})
    return license_info.get("text", "")


def get_classifiers(user_classifiers: list[str]) -> tuple[str, ...]:
    unique_classifiers = keep_unique(user_classifiers)
    if any(classifier not in classifiers for classifier in unique_classifiers):
        classifier_key = "classifiers"
        raise ImproperlyConfiguredProjectError(classifier_key)
    return unique_classifiers


def _get_requirements(
    dependency_groups: dict[str, Sequence[DependencyGroupMember]],
    groups: set[str],
) -> Iterator[Requirement]:
    for group, requirements in dependency_groups.items():
        if group not in groups:
            continue
        for requirement in requirements:
            if isinstance(requirement, str):
                yield Requirement.from_string(requirement)
            elif isinstance(requirement, dict):
                include_group = requirement["include-group"]
                yield from _get_requirements(dependency_groups, {include_group})


def get_requirements(
    dependencies: Sequence[str],
    dependency_groups: dict[str, Sequence[DependencyGroupMember]],
) -> tuple[Requirement, ...]:
    dependency_groups[""] = dependencies
    return keep_unique(_get_requirements(dependency_groups, set(dependency_groups)))


def get_package_paths(
    settings: MetadataSettings, base_dir: Path
) -> tuple[LocalPackage, ...]:
    package_key = "included_packages"
    if packages := cast(list[str], settings.get(package_key, [])):
        output = packages
    elif base_dir.joinpath("src").exists():
        output = ["src"]
    else:
        raise ImproperlyConfiguredProjectError(package_key)
    return keep_unique(
        LocalPackage(path=Path(path), base_dir=base_dir) for path in output
    )
