from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from enum import IntEnum, unique
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence


@unique
class SGRParams(IntEnum):
    DEFAULT = 0
    BOLD = 1
    ITALIC = 3
    UNDERLINE = 4

    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    GREY = 37

    BLACK_BRIGHT = 90
    RED_BRIGHT = 91
    GREEN_BRIGHT = 92
    YELLOW_BRIGHT = 93
    BLUE_BRIGHT = 94
    MAGENTA_BRIGHT = 95
    CYAN_BRIGHT = 96
    WHITE_BRIGHT = 97

    @property
    def sequence(self) -> str:
        return f"\033[{self.value}m"


@dataclass(frozen=True, order=True)
class SGRString:
    __slots__ = ("sgr", "string")  # upgrade: py3.9: use __slots__ = True

    string: str
    sgr: tuple[SGRParams, ...]

    def __init__(self, obj: object, *, params: Iterable[SGRParams] = ()) -> None:
        object.__setattr__(self, "string", str(obj))
        object.__setattr__(self, "sgr", tuple(params))


def write(
    objects: Sequence[object] = (),
    sep: str = "",
    end: str = os.linesep,
    *,
    is_error: bool = False,
) -> None:
    n = len(objects)
    if not n:
        print(end=end, file=sys.stderr if is_error else sys.stdout)
        return
    file = sys.stderr if is_error else sys.stdout
    for index, obj in enumerate(objects, start=1):
        current_end = end if index == n else sep
        if isinstance(obj, SGRString) and file.isatty():
            sgr_prefix = "".join(code.sequence for code in obj.sgr)
            clean_object = obj.string
            sgr_suffix = SGRParams.DEFAULT.sequence if obj.sgr else ""
        else:
            sgr_prefix = ""
            clean_object = str(obj)
            sgr_suffix = ""

        print(sgr_prefix, clean_object, sgr_suffix, sep="", end=current_end, file=file)
