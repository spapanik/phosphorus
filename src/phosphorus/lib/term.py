from __future__ import annotations

from enum import IntEnum, unique
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable


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


class SGRString(str):
    _sgr: str
    __slots__ = ("_sgr",)

    def __new__(cls, value: str, *, params: Iterable[SGRParams]) -> SGRString:
        string = super().__new__(cls, value)
        prefix = "".join(param.sequence for param in params)
        suffix = SGRParams.DEFAULT.sequence
        string._sgr = f"{prefix}{value}{suffix}"  # noqa: SLF001
        return string

    def __str__(self) -> str:
        return self._sgr
