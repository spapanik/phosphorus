from __future__ import annotations

import tarfile
from typing import TYPE_CHECKING

from phosphorus.construction.base import Builder
from phosphorus.lib.constants import pyproject_base_name
from phosphorus.lib.licenses import get_license_files
from phosphorus.lib.zipped_file import ArchiveFile

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator
    from pathlib import Path


class SdistBuilder(Builder):
    __slots__ = ()

    @property
    def filename(self) -> str:
        return f"{self.base_name}.tar.gz"

    def package_files(self, _temp_dir: Path) -> Iterator[ArchiveFile]:
        base_dir = self.meta.base_dir
        for package in self.meta.package_paths:
            for file in package.absolute_path.rglob("*"):
                if file.is_file():
                    yield ArchiveFile.from_file(source=file, base_dir=base_dir)

    def non_package_files(self, _temp_dir: Path) -> Iterator[ArchiveFile]:
        base_dir = self.meta.base_dir
        yield ArchiveFile.from_file(
            base_dir.joinpath(pyproject_base_name), base_dir=base_dir
        )

        for license_file in get_license_files(base_dir):
            yield ArchiveFile.from_file(license_file, base_dir=base_dir)

        if self.meta.readme.read_text():
            yield ArchiveFile.from_file(self.meta.readme, base_dir=base_dir)

    def get_info_file(self, temp_dir: Path, _data: str = "") -> ArchiveFile:
        pkg_info = temp_dir.joinpath("PKG-INFO")
        with pkg_info.open("w") as file:
            file.writelines(f"{line}\n" for line in self.get_metadata_content())

        return ArchiveFile.from_file(source=pkg_info, base_dir=temp_dir)

    def write_files(
        self, files: Iterable[ArchiveFile], package: Path, temp_dir: Path
    ) -> None:
        with tarfile.open(package, "w:gz") as tar:
            for archive_file in sorted(files):
                tar.addfile(
                    archive_file.tar_info, archive_file.absolute_path.open("rb")
                )

            info_file = self.get_info_file(temp_dir)
            tar.addfile(info_file.tar_info, info_file.absolute_path.open("rb"))
