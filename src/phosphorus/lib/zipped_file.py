from __future__ import annotations

import hashlib
from base64 import urlsafe_b64encode
from dataclasses import dataclass
from stat import S_ISDIR
from tarfile import TarInfo
from typing import TYPE_CHECKING
from zipfile import ZipInfo

if TYPE_CHECKING:
    from pathlib import Path


@dataclass(frozen=True, order=True)  # TODO (py3.9): Use slots=True
class ArchiveFile:
    absolute_path: Path
    base_dir: Path
    digest: str
    size: int
    mode: int

    @classmethod
    def from_file(
        cls, source: Path, base_dir: Path
    ) -> ArchiveFile:  # TODO (py3.10): Use Self
        stat = source.stat()

        return cls(
            absolute_path=source,
            base_dir=base_dir,
            digest=cls.hash_file(source),
            size=stat.st_size,
            mode=stat.st_mode,
        )

    @property
    def relative_path(self) -> Path:
        return self.absolute_path.relative_to(self.base_dir)

    @property
    def zip_info(self) -> ZipInfo:
        path = self.relative_path
        date_time = (1980, 1, 1, 0, 0, 0)
        zip_info = ZipInfo(path.as_posix(), date_time=date_time)
        zip_info.external_attr = self.normalised_mode()
        return zip_info

    @property
    def tar_info(self) -> TarInfo:
        path = self.relative_path
        tarinfo = TarInfo(path.as_posix())
        tarinfo.mtime = 0
        tarinfo.uid = 0
        tarinfo.gid = 0
        tarinfo.uname = ""
        tarinfo.gname = ""
        tarinfo.mode = self.normalised_mode(for_zip=False)
        tarinfo.size = self.size
        return tarinfo

    def normalised_mode(self, *, for_zip: bool = True) -> int:
        mode = (self.mode | 0o644) & ~0o133
        if self.mode & 0o100:
            mode |= 0o111
        if for_zip:
            mode = (mode & 0xFFFF) << 16
            if S_ISDIR(self.mode):
                mode |= 0x10

        return mode

    @staticmethod
    def hash_file(path: Path, buffer_size: int = 2**16) -> str:
        sha256 = hashlib.sha256()

        with path.open("rb") as f:
            while data := f.read(buffer_size):
                sha256.update(data)

        hash_value = urlsafe_b64encode(sha256.digest()).decode("ascii").rstrip("=")
        return f"sha256={hash_value}"
