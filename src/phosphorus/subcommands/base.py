from __future__ import annotations

import tomllib
from typing import TYPE_CHECKING, cast

from phosphorus.lib.metadata import Metadata

if TYPE_CHECKING:
    from argparse import Namespace


class BaseCommand:
    __slots__ = ("meta",)

    def __init__(self, _args: Namespace, /) -> None:
        self.meta = Metadata.from_path()

    def run(self) -> None:
        msg = f"{self.__class__.__qualname__} must implement run"
        raise NotImplementedError(msg)

    def get_current_hash(self) -> str:
        with self.meta.lockfile.open("rb") as file:
            return cast(str, tomllib.load(file)["$meta"]["hash"])
