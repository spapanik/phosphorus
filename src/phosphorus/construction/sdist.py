from pathlib import Path

from poetry.core.factory import Factory
from poetry.core.masonry.builders.sdist import SdistBuilder as pSdistBuild
from poetry.core.poetry import Poetry

from phosphorus.construction.base import Builder


class SdistBuilder(Builder):
    __slots__ = []

    def build(self) -> Path:
        # TODO: build sdist
        return pSdistBuild(self.get_package_()).build(self.output_dir)

    @staticmethod
    def get_package_() -> Poetry:
        return Factory().create_poetry(Path().resolve(), with_groups=False)
