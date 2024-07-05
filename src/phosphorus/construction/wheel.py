from __future__ import annotations

import csv
import shutil
from pathlib import Path
from typing import TYPE_CHECKING, Any
from zipfile import ZIP_DEFLATED, ZipFile

from phosphorus.__version__ import __version__
from phosphorus.construction.base import Builder
from phosphorus.lib.licenses import get_license_files
from phosphorus.lib.tags import Tag
from phosphorus.lib.zipped_file import ArchiveFile

if TYPE_CHECKING:
    from collections.abc import Iterator


class WheelBuilder(Builder):
    __slots__ = ("editable",)

    def __init__(
        self,
        output_dir: Path,
        config: dict[str, Any] | None,
        metadata_dir: Path | None,
        *,
        editable: bool = False,
    ) -> None:
        super().__init__(output_dir, config, metadata_dir)
        self.editable = editable

    @property
    def filename(self) -> str:
        tag = Tag(
            interpreter=self.config.get("interpreter", "py3"),
            abi=self.config.get("abi"),
            platform=self.config.get("platform", "any"),
        )
        return self.wheel_filenames[tag]

    @property
    def dist_info(self) -> str:
        return f"{self.base_name}.dist-info"

    @property
    def wheel_filenames(self) -> dict[Tag, str]:
        return {tag: f"{self.base_name}-{tag}.whl" for tag in self.meta.tags}

    def collect_files(self, temp_dir: Path) -> list[ArchiveFile]:
        output = []
        if self.editable:
            file = self.create_pth(temp_dir)
            output.append(
                ArchiveFile.from_file(source=file, target=file.relative_to(temp_dir))
            )
        else:
            for package in self.meta.package_paths:
                output.extend(
                    ArchiveFile.from_file(
                        source=file, target=file.relative_to(package.path)
                    )
                    for file in package.path.glob("**/*")
                    if file.is_file()
                )
        output.extend(
            ArchiveFile.from_file(source=file, target=file.relative_to(temp_dir))
            for file in self.prepare_metadata(temp_dir).glob("**/*")
            if file.is_file()
        )
        return output

    def write_files(
        self, files: list[ArchiveFile], package: Path, temp_dir: Path
    ) -> None:
        with ZipFile(package, mode="w", compression=ZIP_DEFLATED) as zip_file:
            rows = []
            for archive_file in sorted(files):
                zip_file.writestr(
                    archive_file.zip_info,
                    archive_file.absolute_path.read_bytes(),
                    compress_type=ZIP_DEFLATED,
                )
                rows.append([archive_file.path, archive_file.digest, archive_file.size])

            record = temp_dir.joinpath("RECORD")
            rows.append([self.record_target, "", ""])
            with record.open("w") as csv_file:
                write = csv.writer(csv_file)
                write.writerows(rows)

            record_info = ArchiveFile.from_file(
                source=record, target=self.record_target
            )
            zip_file.writestr(
                record_info.zip_info,
                record.read_bytes(),
                compress_type=ZIP_DEFLATED,
            )

    @property
    def record_target(self) -> Path:
        return Path(self.dist_info).joinpath("RECORD")

    def is_pure_lib(self) -> bool:
        return all(tag.abi is None for tag in self.meta.tags)

    def create_pth(self, tmp_dir: Path) -> Path:
        paths = {package.path.as_posix() for package in self.meta.package_paths}
        pth = tmp_dir.joinpath(f"{self.meta.package.name}.pth")
        pth.write_text("\n".join(sorted(paths)))
        return pth

    def prepare_metadata(self, temp_dir: Path | None = None) -> Path:
        base = temp_dir or self.metadata_dir
        if base is None:
            msg = f"Cannot create {self.dist_info} without a metadata directory."
            raise TypeError(msg)

        dist_info = base.joinpath(self.dist_info)
        shutil.rmtree(dist_info, ignore_errors=True)
        dist_info.mkdir(parents=True, exist_ok=True)

        for path, content_generator in self.get_dist_info_entries():
            with dist_info.joinpath(path).open("w") as file:
                file.writelines(f"{line}\n" for line in content_generator)

        for license_file in get_license_files(self.meta.base_dir):
            destination = dist_info.joinpath(
                license_file.relative_to(self.meta.base_dir)
            )

            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(license_file, destination)

        return dist_info

    def get_dist_info_entries(self) -> Iterator[tuple[str, Iterator[str]]]:
        yield "WHEEL", self.get_wheel_content()
        yield "METADATA", self.get_metadata_content()
        if self.meta.scripts:
            yield "entry_points.txt", self.get_entry_points_content()

    def get_entry_points_content(self) -> Iterator[str]:
        yield "[console_scripts]"
        for script in self.meta.scripts:
            yield f"{script.command}={script.entrypoint}"

    def get_wheel_content(self) -> Iterator[str]:
        yield "Wheel-Version: 1.0"
        yield f"Generator: phosphorus {__version__}"
        pure_lib = str(self.is_pure_lib()).lower()
        yield f"Root-Is-Purelib: {pure_lib}"
        for tag in self.meta.tags:
            yield f"Tag: {tag}"
