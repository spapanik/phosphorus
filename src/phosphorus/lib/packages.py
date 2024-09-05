from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from phosphorus.lib.pypi import get_version_info
from phosphorus.lib.utils import canonicalise_name
from phosphorus.lib.versions import Version, VersionClause

if TYPE_CHECKING:
    from collections.abc import Iterable
    from http.client import HTTPResponse
    from pathlib import Path

    from phosphorus.lib.requirements import Requirement


@dataclass(frozen=True, order=True)  # TODO (py3.9): Use slots=True
class VersionedPackage:
    """
    A package with an optional version.

    When the version is None, it represents the latest version.
    """

    package: Package
    version: Version | None = None


@dataclass(frozen=True, order=True)  # TODO (py3.9): Use slots=True
class ResolvedPackage:
    package: Package
    version: Version
    yanked: bool
    requires_python: list[VersionClause]
    requires_dist: list[Requirement]


@dataclass(frozen=True, order=True)  # TODO (py3.9): Use slots=True
class VersionInfo:
    etag: str
    requires_dist: list[str]
    requires_python: str
    yanked: bool
    package: Package
    version: Version
    releases: list[Version] | None = None

    @classmethod
    def from_cache(cls, cache_path: Path) -> VersionInfo:  # TODO (py3.10): Use Self
        with cache_path.open() as file:
            info: dict[str, Any] = json.load(file)
        releases = (
            [Version.from_string(release) for release in info["releases"]]
            if "releases" in info
            else None
        )
        return cls(
            etag=info["ETag"],
            requires_dist=info["requires_dist"],
            requires_python=info["requires_python"],
            yanked=info["yanked"],
            package=Package(cache_path.parent.name),
            version=Version.from_string(info["version"]),
            releases=releases,
        )

    @classmethod
    def from_response(
        cls, response: HTTPResponse
    ) -> VersionInfo:  # TODO (py3.10): Use Self
        info = json.loads(response.read())
        releases = (
            [Version.from_string(release) for release in info["releases"]]
            if "releases" in info
            else None
        )
        return cls(
            etag=response.headers["ETag"],
            requires_dist=info["info"]["requires_dist"],
            requires_python=info["info"]["requires_python"],
            yanked=info["info"]["yanked"],
            package=Package(info["info"]["name"]),
            version=Version.from_string(info["info"]["version"]),
            releases=releases,
        )

    def as_dict(self) -> dict[str, Any]:
        out = {
            "ETag": self.etag,
            "requires_dist": self.requires_dist,
            "requires_python": self.requires_python,
            "yanked": self.yanked,
            "package": self.package.name,
            "version": str(self.version),
        }
        if self.releases is not None:
            releases = [str(release) for release in self.releases]
            out["releases"] = releases
        return out


@dataclass(frozen=True, order=True)  # TODO (py3.9): Use slots=True
class Package:
    name: str
    distribution_name: str = field(repr=False, compare=False)

    def __init__(self, name: str) -> None:
        name = canonicalise_name(name)
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "distribution_name", name.replace("-", "_"))

    def __str__(self) -> str:
        return self.name

    def get_versions(
        self,
        *,
        enforce_pep440: bool = False,
        allow_pre_releases: bool = True,
        allow_dev_releases: bool = True,
        clauses: Iterable[VersionClause] = (),
        last_check: float = float("inf"),
    ) -> list[Version]:

        latest_package = VersionedPackage(package=self)
        version_info = get_version_info(
            packages=[latest_package], last_check=last_check
        )[latest_package]
        versions: list[Version] = []
        if version_info.releases is None:
            msg = "No releases found"
            raise RuntimeError(msg)
        for version in version_info.releases:
            if version.is_pre_release and not allow_pre_releases:
                continue
            if version.is_dev_release and not allow_dev_releases:
                continue
            if not version.pep_440_compliant and enforce_pep440:
                continue
            for clause in clauses:
                if not clause.match(version):
                    break
            else:
                versions.append(version)
        return sorted(versions)
