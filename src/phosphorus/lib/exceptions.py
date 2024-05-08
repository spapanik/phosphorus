from __future__ import annotations

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


class ThirdPartyError(RuntimeError):
    """A third party cli tool exited unsuccessfully"""

    def __init__(self, command: str) -> None:
        msg = f"Command `{command}` exited with a non-zero status code"
        super().__init__(msg)
