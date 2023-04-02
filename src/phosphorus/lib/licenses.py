from __future__ import annotations

from collections.abc import Iterator
from itertools import chain
from pathlib import Path

# Accept the British spelling for the noun
BASE_NAMES = {"COPYING", "LICENCE", "LICENCES", "LICENSE", "LICENSES"}


def get_license_files(base_dir: Path) -> Iterator[Path]:
    for base_name in BASE_NAMES:
        for file in chain(
            [base_dir.joinpath(base_name)],
            base_dir.glob(f"{base_name}.*"),
            base_dir.glob(f"{base_name}/**/*"),
        ):
            if file.is_file():
                yield file
