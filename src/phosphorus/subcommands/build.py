from __future__ import annotations

from typing import TYPE_CHECKING

from phosphorus.construction.api import build_sdist, build_wheel
from phosphorus.lib.term import SGRParams, SGRString, write
from phosphorus.subcommands.base import BaseCommand

if TYPE_CHECKING:
    from argparse import Namespace


class BuildCommand(BaseCommand):
    __slots__ = ("build_sdist", "build_wheel")

    def __init__(self, args: Namespace, /) -> None:
        super().__init__(args)
        self.build_sdist = args.sdist
        self.build_wheel = args.wheel

    def run(self) -> None:
        package_name = SGRString(self.meta.package.name, params=[SGRParams.CYAN])
        version = SGRString(f"({self.meta.version})", params=[SGRParams.BOLD])
        write(["Building ", package_name, version, "..."])

        dist_dir = self.meta.base_dir.joinpath("dist")
        dist_dir.mkdir(exist_ok=True)
        if self.build_sdist:
            self._print_building_start("sdist")
            sdist = build_sdist(dist_dir.as_posix())
            self._print_building_end(sdist)
        if self.build_wheel:
            self._print_building_start("wheel")
            wheel = build_wheel(dist_dir.as_posix())
            self._print_building_end(wheel)

    @staticmethod
    def _print_building_start(build_type: str) -> None:
        write(
            ["🔧 Building ", SGRString(build_type, params=[SGRParams.MAGENTA]), "..."]
        )

    @staticmethod
    def _print_building_end(file_path: str) -> None:
        write(
            [
                "✅ ",
                SGRString(file_path, params=[SGRParams.BLUE]),
                " built successfully!",
            ]
        )
