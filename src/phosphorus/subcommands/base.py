from __future__ import annotations

from typing import TYPE_CHECKING, cast

from phosphorus._seven import toml_parser
from phosphorus.lib.metadata import Metadata

if TYPE_CHECKING:
    from argparse import Namespace


class BaseCommand:
    __slots__ = ("meta", "verbosity")

    def __init__(self, args: Namespace, /) -> None:
        self.verbosity = args.verbosity
        self.meta = Metadata.from_path()

    def run(self) -> None:
        raise NotImplementedError

    def get_current_hash(self) -> str:
        with self.meta.lockfile.open("rb") as file:
            return cast(str, toml_parser(file)["$meta"]["hash"])
