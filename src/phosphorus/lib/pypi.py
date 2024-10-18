from __future__ import annotations

import json
from http import HTTPStatus
from threading import Thread
from typing import TYPE_CHECKING
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from phosphorus.lib.constants import pypi_cache

if TYPE_CHECKING:
    from phosphorus.lib.packages import Package, VersionedPackage, VersionInfo
    from phosphorus.lib.versions import Version


def get_version_info(
    packages: list[VersionedPackage], *, last_check: float = float("inf")
) -> dict[VersionedPackage, VersionInfo]:

    threads: list[Thread] = []
    results: dict[VersionedPackage, VersionInfo] = {}
    for package_info in packages:
        thread = Thread(
            target=_get_version_info,
            args=(package_info.package, package_info.version, last_check, results),
        )
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    return results


def _get_version_info(
    package: Package,
    version: Version | None,
    last_check: float,
    results: dict[VersionedPackage, VersionInfo],
) -> None:
    from phosphorus.lib.packages import VersionedPackage, VersionInfo

    key = VersionedPackage(package, version)
    filename = "latest.json" if version is None else f"{version.canonical_form}.json"
    local_cache = pypi_cache.joinpath(package.name, filename)
    if local_cache.exists():
        local_info = VersionInfo.from_cache(local_cache)
        modified = local_cache.stat().st_mtime
        if modified >= last_check:
            results[key] = local_info
            return
        etag = local_info.etag
    else:
        local_cache.parent.mkdir(parents=True, exist_ok=True)
        etag = ""

    try:
        pypi_info = _get_info_from_pypi(package, version, etag)
    except HTTPError as exc:
        if exc.status == HTTPStatus.NOT_MODIFIED:
            local_cache.touch()
            results[key] = local_info
            return
        raise

    with local_cache.open("w") as file:
        json.dump(pypi_info.as_dict(), file, indent=4)
    results[key] = pypi_info


def _get_info_from_pypi(
    package: Package, version: Version | None, etag: str
) -> VersionInfo:
    from phosphorus.lib.packages import VersionInfo

    package_slug = f"{package.name}/{version}" if version else package.name
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
    return VersionInfo.from_response(response)
