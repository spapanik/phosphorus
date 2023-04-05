from argparse import Namespace

from phosphorus.commands.base import BaseCommand
from phosphorus.construction.api import (
    build_sdist,
    build_wheel,
    prepare_metadata_for_build_wheel,
)


class BuildCommand(BaseCommand):
    __slots__ = [*BaseCommand.__slots__, "build_metadata", "build_sdist", "build_wheel"]

    def __init__(self, args: Namespace, /):
        super().__init__(args)
        self.build_metadata = args.metadata
        self.build_sdist = args.sdist
        self.build_wheel = args.wheel

    def __call__(self) -> None:
        dist_dir = self.meta.base_dir.joinpath("dist")
        dist_dir.mkdir(exist_ok=True)
        if self.build_metadata:
            prepare_metadata_for_build_wheel(dist_dir.as_posix())
        if self.build_sdist:
            build_sdist(dist_dir.as_posix())
        if self.build_wheel:
            build_wheel(dist_dir.as_posix())
