from __future__ import annotations

from typing import TYPE_CHECKING

from phosphorus.construction.api import build_sdist, build_wheel
from phosphorus.lib.term import SGRParams, SGRString
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
        print(f"Building {package_name} {version} ...")
        dist_dir = self.meta.base_dir.joinpath("dist")
        dist_dir.mkdir(exist_ok=True)
        if self.build_sdist:
            print(f"🔧 Building {SGRString('sdist', params=[SGRParams.MAGENTA])} ...")
            sdist = build_sdist(dist_dir.as_posix())
            sgr_sdist = SGRString(str(sdist), params=[SGRParams.BLUE])
            print(f"✅ {sgr_sdist} built successfully!")
        if self.build_wheel:
            print(f"🔧 Building {SGRString('wheel', params=[SGRParams.MAGENTA])} ...")
            wheel = build_wheel(dist_dir.as_posix())
            sgr_wheel = SGRString(str(wheel), params=[SGRParams.BLUE])
            print(f"✅ {sgr_wheel} built successfully!")
