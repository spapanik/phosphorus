import json
import tomllib
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from hashlib import sha256
from importlib.machinery import SourceFileLoader
from pathlib import Path
from typing import Any, Self, cast

from phosphorus.lib.constants import (
    BooleanOperator,
    ComparisonOperator,
    MarkerVariable,
    lock_file_name,
    pyproject_base_name,
)
from phosphorus.lib.contributors import Contributor
from phosphorus.lib.exceptions import MissingProjectRootError
from phosphorus.lib.markers import Marker
from phosphorus.lib.packages import Package
from phosphorus.lib.requirements import Requirement, RequirementGroup
from phosphorus.lib.tags import Tag
from phosphorus.lib.versions import Version, VersionClause


@dataclass(frozen=True, slots=True, order=True)
class Script:
    command: str
    entrypoint: str


@dataclass(frozen=True, slots=True, order=True)
class ProjectURL:
    name: str
    url: str


@dataclass(frozen=True, slots=True, order=True)
class LocalPackage:
    name: str
    path: Path


class JSONEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        match o:
            case Path():
                return o.as_posix()
            case ComparisonOperator():
                return str(o)
            case BooleanOperator():
                return str(o)
            case MarkerVariable():
                return str(o)
            case _:
                return super().default(o)


@dataclass(frozen=True, slots=True, order=True)
class Metadata:
    base_dir: Path
    package: Package
    version: Version
    summary: str
    homepage: str
    license: str  # noqa: A003
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
    def from_path(cls, path: Path | None = None) -> Self:
        settings_path = get_pyproject(path)
        settings = get_settings(settings_path)
        urls = settings.get("urls", {})

        if not (python := settings.get("python")):
            python = "~3.7"

        return cls(
            base_dir=settings_path.parent,
            package=get_package(settings),
            version=get_version(settings),
            summary=settings.get("summary", ""),
            homepage=urls.get("homepage", ""),
            license=settings.get("license", ""),
            keywords=keep_uniques(settings.get("keywords", [])),
            tags=(Tag(interpreter="py3", abi=None, platform="any"),),
            authors=get_contributors(settings.get("authors", [])),
            maintainers=get_contributors(settings.get("maintainers", [])),
            python=keep_uniques(
                VersionClause.from_string(clause) for clause in python.split(",")
            ),
            classifiers=keep_uniques(settings.get("classifiers", [])),
            requirement_groups=get_requirements(settings.get("dependencies", {})),
            project_urls=keep_uniques(
                ProjectURL(name=name, url=url)
                for name, url in urls.items()
                if name != "homepage"
            ),
            scripts=keep_uniques(
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
        json_dump = json.dumps(asdict(self), cls=JSONEncoder, sort_keys=True)
        return sha256(json_dump.encode("utf-8")).hexdigest()


def keep_uniques(items: Iterable[Any]) -> tuple[Any, ...]:
    return tuple(sorted(set(items)))


def get_pyproject(cwd: Path | None) -> Path:
    if cwd is None:
        cwd = Path.cwd().resolve()

    while not (pyproject := cwd.joinpath(pyproject_base_name)).is_file():
        if cwd.as_posix() == "/":
            message = f"Could not find {pyproject_base_name} in {Path.cwd().resolve()} or any parent directory"
            raise MissingProjectRootError(message)
        cwd = cwd.parent
    return pyproject


def get_contributors(settings: list[dict[str, str]]) -> tuple[Contributor, ...]:
    return tuple(Contributor.from_data(data) for data in settings)


def get_settings(settings_path: Path) -> dict[str, Any]:
    with settings_path.open("rb") as settings:
        return cast(dict[str, Any], tomllib.load(settings)["tool"]["phosphorus"])


def get_package(settings: dict[str, Any]) -> Package:
    return Package(name=settings["name"])


def get_version(settings: dict[str, Any]) -> Version:
    version = settings["version"]
    if version.startswith("./"):
        name = "_module"
        _module = SourceFileLoader(name, version).load_module(name)
        version = _module.__version__
    return Version.from_string(version)


def get_requirements(settings: dict[str, Any]) -> tuple[RequirementGroup, ...]:
    output: dict[str, list[Requirement]] = {}
    for group, requirement_info in settings.items():
        output[group] = []
        for dependency, raw_constraints in requirement_info.items():
            package = Package(name=dependency)
            if isinstance(raw_constraints, str):
                constraints = [{"version": raw_constraints, "marker": ""}]
            elif isinstance(raw_constraints, dict):
                constraints = [raw_constraints]
            else:
                constraints = raw_constraints

            output[group].extend(
                [
                    Requirement(
                        package=package,
                        clauses=tuple(
                            VersionClause.from_string(clause)
                            for clause in constraint["version"].split(",")
                        ),
                        marker=Marker.from_string(constraint["marker"]),
                    )
                    for constraint in constraints
                ]
            )

    return keep_uniques(
        RequirementGroup(group=group, requirements=keep_uniques(requirements))
        for group, requirements in output.items()
    )


def get_package_paths(
    settings: dict[str, Any], base_dir: Path
) -> tuple[LocalPackage, ...]:
    name = settings["name"]
    include = settings.get("include", [])
    output: dict[str, Path] = {}
    src_package = base_dir.joinpath("src").joinpath(name)
    base_package = base_dir.joinpath(name)
    if src_package.exists():
        output[name] = base_dir.joinpath("src")
    elif base_package.exists():
        output[name] = base_dir
    for package_info in include:
        output[package_info["name"]] = base_dir.joinpath(package_info["in"])
    return keep_uniques(
        LocalPackage(name=name, path=path) for name, path in output.items()
    )
