from __future__ import annotations

from subprocess import run
from typing import TYPE_CHECKING

from uv import find_uv_bin

if TYPE_CHECKING:
    from subprocess import CompletedProcess


def uv_run(args: list[str]) -> CompletedProcess[bytes]:
    uv_bin = find_uv_bin()
    return run([uv_bin, *args], capture_output=True)  # noqa: PLW1510, S603
