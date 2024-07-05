from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from phosphorus.lib.constants import pypi_cache
from phosphorus.lib.utils import canonicalise_name
from phosphorus.lib.versions import Version, VersionClause

if TYPE_CHECKING:
    from collections.abc import Iterable

    from phosphorus.lib.requirements import Requirement


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
        dependencies = self._get_version_info(last_check=last_check)
        versions: list[Version] = []
        for release in dependencies["releases"]:
            version = Version.from_string(release)
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

    def get_version_info(
        self, version: Version, *, last_check: float = float("inf")
    ) -> ResolvedPackage:
        from phosphorus.lib.requirements import Requirement

        info = self._get_version_info(version.canonical_form, last_check=last_check)
        return ResolvedPackage(
            package=self,
            version=version,
            yanked=info["yanked"],
            requires_python=[
                VersionClause.from_string(version.strip())
                for version in (info["requires_python"] or "*").split(",")
            ],
            requires_dist=[
                Requirement.from_string(requirement)
                for requirement in info["requires_dist"] or []
            ],
        )

    def _get_version_info(
        self, version: str = "", *, last_check: float = float("inf")
    ) -> dict[str, Any]:
        if version:
            version = Version.from_string(version).canonical_form
            filename = f"{version}.json"
        else:
            filename = "latest.json"
        local_cache_dir = pypi_cache.joinpath(self.name)
        local_cache_dir.mkdir(parents=True, exist_ok=True)
        local_cache = local_cache_dir.joinpath(filename)
        etag = ""
        if local_cache.exists():
            with local_cache.open() as file:
                local_info: dict[str, Any] = json.load(file)
                etag = local_info["ETag"]
            modified = local_cache.stat().st_mtime
            if modified >= last_check:
                return local_info

        pypi_info = self._get_info_from_pypi(etag=etag, version=version)
        if pypi_info["use_cache"]:
            local_cache.touch()
            if not version:
                version = Version.from_string(local_info["version"]).canonical_form
                local_cache_dir.joinpath(f"{version}.json").touch()
            return local_info

        del pypi_info["use_cache"]
        with local_cache.open("w") as file:
            json.dump(pypi_info, file, indent=4)
        if not version:
            version = Version.from_string(pypi_info["version"]).canonical_form
            local_cache = local_cache_dir.joinpath(f"{version}.json")
            with local_cache.open("w") as file:
                json.dump(pypi_info, file, indent=4)
        return pypi_info

    def _get_info_from_pypi(self, etag: str, version: str) -> dict[str, Any]:
        package_slug = f"{self.name}/{version}" if version else self.name
        url = f"https://pypi.org/pypi/{package_slug}/json"
        headers = {}
        if etag:
            headers["If-None-Match"] = etag
        request = Request(url, headers=headers)  # noqa: S310
        try:
            response = urlopen(request, timeout=60)  # noqa: S310
        except TimeoutError as exc:
            msg = "pypi connection timed out"
            raise RuntimeError(msg) from exc
        except HTTPError as exc:
            if exc.status == 304:
                return {"use_cache": True}
            raise
        info = json.loads(response.read())
        out = {
            "use_cache": False,
            "ETag": response.headers["ETag"],
            "requires_dist": info["info"]["requires_dist"],
            "requires_python": info["info"]["requires_python"],
            "yanked": info["info"]["yanked"],
            "version": info["info"]["version"],
        }
        if not version:
            out["releases"] = list(info["releases"].keys())
        return out


@dataclass(frozen=True, order=True)  # TODO (py3.9): Use slots=True
class ResolvedPackage:
    package: Package
    version: Version
    yanked: bool
    requires_python: list[VersionClause]
    requires_dist: list[Requirement]
