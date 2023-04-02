import csv
from collections.abc import Iterator
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
from zipfile import ZIP_DEFLATED, ZipFile

from phosphorus.lib.contributors import Contributor
from phosphorus.lib.metadata import Metadata
from phosphorus.lib.zipped_file import ZippedFile


class Builder:
    __slots__ = ("config", "metadata_dir", "output_dir", "meta")

    def __init__(
        self, output_dir: Path, config: dict[str, Any] | None, metadata_dir: Path | None
    ) -> None:
        self.output_dir = output_dir
        self.config = config or {}
        self.metadata_dir = metadata_dir
        self.meta = Metadata.from_path()

    def build(self) -> Path:
        package = self.output_dir.joinpath(self.filename)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        package.unlink(missing_ok=True)

        with TemporaryDirectory() as temp_dir_name:
            temp_dir = Path(temp_dir_name).resolve()
            files = self.collect_files(temp_dir)
            self.write_files(files, package, temp_dir)

        return package

    @property
    def filename(self) -> str:
        raise NotImplementedError

    def collect_files(self, temp_dir: Path) -> dict[Path, ZippedFile]:
        raise NotImplementedError

    def write_files(
        self, files: dict[Path, ZippedFile], package: Path, temp_dir: Path
    ) -> None:
        with ZipFile(package, mode="w", compression=ZIP_DEFLATED) as zip_file:
            rows = []
            for file, info in sorted(files.items(), key=lambda item: item[1].path):
                zip_file.writestr(
                    info.zip_info, file.read_bytes(), compress_type=ZIP_DEFLATED
                )
                rows.append([info.path, info.digest, info.size])

            if self.record_target:
                record = temp_dir.joinpath("RECORD")
                rows.append([self.record_target, "", ""])
                with record.open("w") as csv_file:
                    write = csv.writer(csv_file)
                    write.writerows(rows)

                record_info = ZippedFile.from_file(
                    source=record, target=self.record_target
                )
                zip_file.writestr(
                    record_info.zip_info,
                    record.read_bytes(),
                    compress_type=ZIP_DEFLATED,
                )

    @property
    def base_name(self) -> str:
        package_name = self.meta.package.distribution_name
        return f"{package_name}-{self.meta.version}"

    @property
    def record_target(self) -> Path | None:
        return None

    def get_metadata_content(self) -> Iterator[str]:
        yield "Metadata-Version: 2.3"
        yield f"Name: {self.meta.package.name}"
        yield f"Version: {self.meta.version}"
        if self.meta.summary:
            yield f"Summary: {self.meta.summary}"

        if self.meta.homepage:
            yield f"Home-page: {self.meta.homepage}"

        if self.meta.license:
            yield f"License: {self.meta.license}"

        if self.meta.keywords:
            keyword_string = ",".join(self.meta.keywords)
            yield f"Keywords: {keyword_string}"

        if names := Contributor.stringify_names(self.meta.authors):
            yield f"Author: {names}"

        if emails := Contributor.stringify_emails(self.meta.authors):
            yield f"Author-email: {emails}"

        if names := Contributor.stringify_names(self.meta.maintainers):
            yield f"Maintainer: {names}"

        if emails := Contributor.stringify_emails(self.meta.maintainers):
            yield f"Maintainer-email: {emails}"

        python_versions = ",".join(str(clause) for clause in self.meta.python)
        yield f"Requires-Python: {python_versions}"

        for classifier in self.meta.classifiers:
            yield f"Classifier: {classifier}"

        for requirement_group in self.meta.requirement_groups:
            if requirement_group.group == "main":
                for requirement in requirement_group.requirements:
                    yield f"Requires-Dist: {requirement}"
                break

        for project_url in self.meta.project_urls:
            yield f"Project-URL: {project_url.name.title()}, {project_url.url}"

        if readme_text := self.meta.readme.read_text():
            yield "Description-Content-Type: text/markdown"
            yield ""
            yield readme_text
