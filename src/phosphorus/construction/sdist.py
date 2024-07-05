from __future__ import annotations

import tarfile
from pathlib import Path
from typing import TYPE_CHECKING

from phosphorus.construction.base import Builder
from phosphorus.lib.constants import pyproject_base_name
from phosphorus.lib.licenses import get_license_files
from phosphorus.lib.zipped_file import ArchiveFile

if TYPE_CHECKING:
    from collections.abc import Iterator


class SdistBuilder(Builder):
    __slots__ = ()

    @property
    def filename(self) -> str:
        return f"{self.base_name}.tar.gz"

    def collect_files(self, temp_dir: Path) -> list[ArchiveFile]:
        output: list[ArchiveFile] = []
        base_dir = self.meta.base_dir
        for package in self.meta.package_paths:
            output.extend(
                ArchiveFile.from_file(source=file, target=file.relative_to(base_dir))
                for file in package.path.glob("**/*")
                if file.is_file()
            )
        output.extend(
            ArchiveFile.from_file(source=source, target=target)
            for source, target in self.non_package_files(temp_dir)
        )
        return output

    def write_files(
        self, files: list[ArchiveFile], package: Path, _temp_dir: Path
    ) -> None:
        with tarfile.open(package, "w:gz") as tar:
            for archive_file in sorted(files):
                tar.addfile(
                    archive_file.tar_info, archive_file.absolute_path.open("rb")
                )

    def non_package_files(self, temp_dir: Path) -> Iterator[tuple[Path, Path]]:
        base_dir = self.meta.base_dir

        yield base_dir.joinpath(pyproject_base_name), Path(pyproject_base_name)

        for license_file in get_license_files(base_dir):
            yield license_file, license_file.relative_to(base_dir)

        if self.meta.readme.read_text():
            yield self.meta.readme, self.meta.readme.relative_to(base_dir)

        pkg_info = temp_dir.joinpath("PKG-INFO")
        with pkg_info.open("w") as file:
            file.writelines(f"{line}\n" for line in self.get_metadata_content())

        yield pkg_info, pkg_info.relative_to(temp_dir)
