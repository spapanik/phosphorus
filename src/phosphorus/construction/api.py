from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from phosphorus.construction.sdist import SdistBuilder
from phosphorus.construction.wheel import WheelBuilder

# mandatory hooks


def build_wheel(
    wheel_directory: str,
    config_settings: dict[str, Any] | None = None,
    metadata_directory: str | None = None,
) -> str:
    metadata_path = None if metadata_directory is None else Path(metadata_directory)
    builder = WheelBuilder(Path(wheel_directory), config_settings, metadata_path)
    return builder.build().name


def build_sdist(
    sdist_directory: str, config_settings: dict[str, Any] | None = None
) -> str:
    builder = SdistBuilder(Path(sdist_directory), config_settings, None)
    return builder.build().name


# optional hooks


def prepare_metadata_for_build_wheel(
    metadata_directory: str, config_settings: dict[str, Any] | None = None
) -> str:
    builder = WheelBuilder(Path(os.devnull), config_settings, Path(metadata_directory))
    return builder.prepare_metadata().name


def build_editable(
    wheel_directory: str,
    config_settings: dict[str, Any] | None = None,
    metadata_directory: str | None = None,
) -> str:
    metadata_path = None if metadata_directory is None else Path(metadata_directory)
    builder = WheelBuilder(
        Path(wheel_directory), config_settings, metadata_path, editable=True
    )
    return builder.build().name
