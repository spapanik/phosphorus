import tomllib
from argparse import Namespace
from typing import cast

from phosphorus.lib.metadata import Metadata


class BaseCommand:
    __slots__ = ["meta"]

    def __init__(self, _args: Namespace, /):
        self.meta = Metadata.from_path()

    def __call__(self) -> None:
        raise NotImplementedError(f"{self.__class__.__qualname__} must be callable.")

    def get_current_hash(self) -> str:
        with self.meta.lockfile.open("rb") as file:
            return cast(str, tomllib.load(file)["phosphorus"]["meta"]["hash"])
