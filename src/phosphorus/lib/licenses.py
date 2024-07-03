from __future__ import annotations

from itertools import chain
from typing import TYPE_CHECKING

from phosphorus.lib.constants import licence_base_names

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path


def get_license_files(base_dir: Path) -> Iterator[Path]:
    for base_name in licence_base_names:
        for file in chain(
            [base_dir.joinpath(base_name)],
            base_dir.glob(f"{base_name}.*"),
            base_dir.glob(f"{base_name}/**/*"),
        ):
            if file.is_file():
                yield file
