from __future__ import annotations

import hashlib
from base64 import urlsafe_b64encode
from dataclasses import dataclass
from stat import S_ISDIR
from typing import TYPE_CHECKING, Self
from zipfile import ZipInfo

if TYPE_CHECKING:
    from os import stat_result
    from pathlib import Path


@dataclass(frozen=True, slots=True)
class ZippedFile:
    path: Path
    digest: str
    size: int
    zip_info: ZipInfo

    @classmethod
    def from_file(cls, source: Path, target: Path) -> Self:
        date_time = (1980, 1, 1, 0, 0, 0)
        zip_info = ZipInfo(target.as_posix(), date_time=date_time)
        stat = source.stat()

        zip_info.external_attr = cls.standardise_attributes(stat)

        return cls(
            path=target,
            digest=cls.hash_file(source),
            size=stat.st_size,
            zip_info=zip_info,
        )

    @staticmethod
    def standardise_attributes(stat: stat_result) -> int:
        external_attr = (stat.st_mode | 0o644) & ~0o133
        if stat.st_mode & 0o100:
            external_attr |= 0o111
        external_attr = (external_attr & 0xFFFF) << 16
        if S_ISDIR(stat.st_mode):
            external_attr |= 0x10

        return external_attr

    @staticmethod
    def hash_file(path: Path, buffer_size: int = 2**16) -> str:
        sha256 = hashlib.sha256()

        with path.open("rb") as f:
            while data := f.read(buffer_size):
                sha256.update(data)

        hash_value = urlsafe_b64encode(sha256.digest()).decode("ascii").rstrip("=")
        return f"sha256={hash_value}"
