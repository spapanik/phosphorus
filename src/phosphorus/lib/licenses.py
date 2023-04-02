from collections.abc import Iterator
from itertools import chain
from pathlib import Path

from phosphorus.lib.constants import licence_base_names


def get_license_files(base_dir: Path) -> Iterator[Path]:
    for base_name in licence_base_names:
        for file in chain(
            [base_dir.joinpath(base_name)],
            base_dir.glob(f"{base_name}.*"),
            base_dir.glob(f"docs/{base_name}.*"),
            base_dir.glob(f"{base_name}/**/*"),
            base_dir.glob(f"docs/{base_name}/**/*"),
        ):
            if file.is_file():
                yield file
