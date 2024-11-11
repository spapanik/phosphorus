from __future__ import annotations

import shutil
from subprocess import run
from typing import TYPE_CHECKING

from uv import find_uv_bin

from phosphorus.lib.exceptions import (
    PythonSubprocessError,
    UnreachableCodeError,
    UVError,
)

if TYPE_CHECKING:
    from subprocess import CompletedProcess


def find_python_bin() -> str:
    python_bin = shutil.which("python")
    if python_bin is None:
        raise UnreachableCodeError
    return python_bin


def uv_run(args: list[str], *, verbose: bool) -> CompletedProcess[bytes]:
    uv_bin = find_uv_bin()
    command = [uv_bin, *args]
    output = run(command, capture_output=True)  # noqa: PLW1510, S603
    if output.returncode:
        print()
        if verbose:
            print(output.stderr.decode())
        raise UVError(*command)
    return output


def python_run(command_string: str, *, verbose: bool) -> CompletedProcess[bytes]:
    python_bin = find_python_bin()
    command = [python_bin, "-c", command_string]
    output = run(command, capture_output=True)  # noqa: PLW1510, S603
    if output.returncode:
        print()
        if verbose:
            print(output.stderr.decode())
        raise PythonSubprocessError(python_bin, command_string)
    return output
