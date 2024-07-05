from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING, Any

from phosphorus.lib.contributors import Contributor
from phosphorus.lib.metadata import Metadata

if TYPE_CHECKING:
    from collections.abc import Iterator

    from phosphorus.lib.zipped_file import ArchiveFile


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

    def collect_files(self, temp_dir: Path) -> list[ArchiveFile]:
        raise NotImplementedError

    def write_files(
        self, files: list[ArchiveFile], package: Path, temp_dir: Path
    ) -> None:
        raise NotImplementedError

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
            yield readme_text.rstrip("\n")
