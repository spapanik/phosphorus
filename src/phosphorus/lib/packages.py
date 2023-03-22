import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from phosphorus.lib.versions import Version

cache = Path("~/.cache/phosphorus/packages/PyPI").expanduser()


@dataclass(frozen=True, order=True)
class Package:
    name: str
    distribution_name: str = field(repr=False, compare=False)

    def __init__(self, name: str):
        name = re.sub(r"[-_.]+", "-", name).lower()
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "distribution_name", name.replace("-", "_"))

    def get_dependency_info(self, version: str = "") -> dict[str, Any]:
        if version:
            version = Version.from_string(version).canonical_form
        local_cache_dir = cache.joinpath(self.name)
        local_cache_dir.mkdir(parents=True, exist_ok=True)
        local_cache = local_cache_dir.joinpath(version or "latest")
        etag = ""
        if local_cache.exists():
            with local_cache.open() as file:
                local_info: dict[str, Any] = json.load(file)
                etag = local_info["ETag"]
        pypi_info = self._get_info_from_pypi(etag=etag, version=version)
        if not pypi_info["use_cache"]:
            del pypi_info["use_cache"]
            with local_cache.open("w") as file:
                json.dump(pypi_info, file, indent=4)
            if not version:
                local_cache = local_cache_dir.joinpath(pypi_info["version"])
                with local_cache.open("w") as file:
                    json.dump(pypi_info, file, indent=4)
            return pypi_info
        return local_info

    def _get_info_from_pypi(self, etag: str, version: str) -> dict[str, Any]:
        package_slug = f"{self.name}/{version}" if version else self.name
        url = f"https://pypi.org/pypi/{package_slug}/json"
        headers = {}
        if etag:
            headers["If-None-Match"] = etag
        request = Request(url, headers=headers)
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
