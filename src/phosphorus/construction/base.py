from collections.abc import Iterator
from pathlib import Path
from typing import Any

from phosphorus.lib.contributors import Contributor
from phosphorus.lib.metadata import Metadata


class Builder:
    __slots__ = ["config", "metadata_dir", "output_dir", "meta"]

    def __init__(
        self, output_dir: Path, config: dict[str, Any] | None, metadata_dir: Path | None
    ):
        self.output_dir = output_dir
        self.config = config or {}
        self.metadata_dir = metadata_dir
        self.meta = Metadata.from_path()

    def build(self) -> Path:
        raise NotImplementedError(f"{self.__class__.__qualname__} must implement build")

    def get_metadata_content(self) -> Iterator[str]:
        yield "Metadata-Version: 2.1"
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

        for project_url in self.meta.project_urls:
            yield f"Project-URL: {project_url.name}, {project_url.url}"
