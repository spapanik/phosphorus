from __future__ import annotations

import shlex
from typing import TYPE_CHECKING

from phosphorus.lib.constants import pyproject_base_name

if TYPE_CHECKING:
    from pathlib import Path


class UnreachableCodeError(AssertionError):
    """This is an aid for static analysers"""


class MissingProjectRootError(RuntimeError):
    """The project root could not be found"""

    def __init__(self, path: Path) -> None:
        msg = f"Could not find {pyproject_base_name} in {path} or any parent directory"
        super().__init__(msg)


class ImproperlyConfiguredProjectError(RuntimeError):
    """The pyproject.toml file is not correctly formatted"""

    def __init__(self, key: str) -> None:
        msg = f"The pyproject.toml file is missing the key: {key} and isn't marked as dynamic"
        super().__init__(msg)


class UVError(RuntimeError):
    """uv exited unsuccessfully"""

    def __init__(self, *command_parts: str) -> None:
        command_string = shlex.join(command_parts)
        msg = f"uv command `{command_string}` exited with a non-zero status code"
        super().__init__(msg)


class PythonSubprocessError(RuntimeError):
    """python as a subprocess exited unsuccessfully"""

    def __init__(self, python_binary: str, command: str) -> None:
        msg = f"python command `{command}` exited with a non-zero status code when run with `{python_binary}`"
        super().__init__(msg)
