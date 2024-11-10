from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from hashlib import sha256
from importlib.machinery import SourceFileLoader
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

from trove_classifiers import classifiers

from phosphorus._seven import toml_parser
from phosphorus.lib.constants import (
    BooleanOperator,
    ComparisonOperator,
    MarkerVariable,
    lock_file_name,
    pyproject_base_name,
)
from phosphorus.lib.contributors import Contributor
from phosphorus.lib.exceptions import (
    ImproperlyConfiguredProjectError,
    MissingProjectRootError,
)
from phosphorus.lib.packages import Package
from phosphorus.lib.requirements import Requirement, RequirementGroup
from phosphorus.lib.tags import Tag
from phosphorus.lib.versions import Version, VersionClause

if TYPE_CHECKING:
    from collections.abc import Iterable


@dataclass(frozen=True, order=True)  # TODO (py3.9): Use slots=True
class Script:
    command: str
    entrypoint: str


@dataclass(frozen=True, order=True)  # TODO (py3.9): Use slots=True
class ProjectURL:
    name: str
    url: str


@dataclass(frozen=True, order=True)  # TODO (py3.9): Use slots=True
class LocalPackage:
    base_dir: Path
    path: Path

    @property
    def absolute_path(self) -> Path:
        return self.base_dir.joinpath(self.path)


class JSONEncoder(json.JSONEncoder):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.base_dir = kwargs.pop("base_dir")
        super().__init__(*args, **kwargs)

    def default(self, o: Any) -> Any:
        if isinstance(o, Path):  # TODO (py3.9): Use match
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

        return super().default(o)


@dataclass(frozen=True, order=True)  # TODO (py3.9): Use slots=True
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
    requirement_groups: tuple[RequirementGroup, ...]
    scripts: tuple[Script, ...]
    project_urls: tuple[ProjectURL, ...]
    package_paths: tuple[LocalPackage, ...]

    @classmethod
    def from_path(cls, path: Path | None = None) -> Metadata:  # TODO (py3.10): Use Self
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
            readme=settings_path.parent.joinpath(settings.get("readme", os.devnull)),
            keywords=keep_unique(settings.get("keywords", [])),
            tags=(Tag(interpreter="py3", abi=None, platform="any"),),
            authors=get_contributors(settings.get("authors", [])),
            maintainers=get_contributors(settings.get("maintainers", [])),
            python=keep_unique(
                VersionClause.from_string(clause) for clause in python.split(",")
            ),
            classifiers=get_classifiers(settings.get("classifiers", [])),
            requirement_groups=get_requirements(
                settings.get("dependencies", []), settings.get("dev_dependencies", {})
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
    def lockfile(self) -> Path:
        return self.base_dir.joinpath(lock_file_name)

    @property
    def pyproject(self) -> Path:
        return self.base_dir.joinpath(pyproject_base_name)

    @property
    def p_hash(self) -> str:
        json_dump = json.dumps(
            asdict(self), cls=JSONEncoder, base_dir=self.base_dir, sort_keys=True
        )
        return sha256(json_dump.encode("utf-8")).hexdigest()


def keep_unique(items: Iterable[Any]) -> tuple[Any, ...]:
    return tuple(sorted(set(items)))


def get_pyproject(cwd: Path | None) -> Path:
    if cwd is None:
        cwd = Path.cwd().resolve()

    while not (pyproject := cwd.joinpath(pyproject_base_name)).is_file():
        if cwd.as_posix() == "/":
            raise MissingProjectRootError(cwd)
        cwd = cwd.parent
    return pyproject


def get_contributors(settings: list[dict[str, str]]) -> tuple[Contributor, ...]:
    return tuple(Contributor.from_data(data) for data in settings)


def get_settings(settings_path: Path) -> dict[str, Any]:
    with settings_path.open("rb") as settings_file:
        all_settings = toml_parser(settings_file)
    settings = all_settings.get("project", {})
    phosphorus_settings = all_settings.get("tool", {}).get("phosphorus", {})
    settings["dev_dependencies"] = phosphorus_settings.get("dev-dependencies", {})
    settings["dynamic_definitions"] = phosphorus_settings.get("dynamic", {})
    settings["included_packages"] = phosphorus_settings.get("packages", {})
    return cast(dict[str, Any], settings)


def get_package(settings: dict[str, Any]) -> Package:
    return Package(name=settings["name"])


def get_version(settings: dict[str, Any]) -> Version:
    version_key = "version"
    version = settings.get(version_key)
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


def get_license(settings: dict[str, Any]) -> str:
    license_info = settings.get("license", {})
    if license_text := license_info.get("text", ""):
        return cast(str, license_text)
    return ""


def get_classifiers(user_classifiers: list[str]) -> tuple[str, ...]:
    unique_classifiers = keep_unique(user_classifiers)
    if any(classifier not in classifiers for classifier in unique_classifiers):
        classifier_key = "classifiers"
        raise ImproperlyConfiguredProjectError(classifier_key)
    return unique_classifiers


def get_requirements(
    dependencies: list[str], dev_dependencies: dict[str, list[str]]
) -> tuple[RequirementGroup, ...]:
    output = {
        group: [Requirement.from_string(constraint) for constraint in requirement_info]
        for group, requirement_info in dev_dependencies.items()
    }
    output["main"] = [
        Requirement.from_string(constraint) for constraint in dependencies
    ]

    return keep_unique(
        RequirementGroup(group=group, requirements=keep_unique(requirements))
        for group, requirements in output.items()
    )


def get_package_paths(
    settings: dict[str, Any], base_dir: Path
) -> tuple[LocalPackage, ...]:
    package_key = "included_packages"
    if packages := settings.get(package_key, []):
        output = packages
    elif base_dir.joinpath("src").exists():
        output = ["src"]
    else:
        raise ImproperlyConfiguredProjectError(package_key)
    return keep_unique(
        LocalPackage(path=Path(path), base_dir=base_dir) for path in output
    )
