from __future__ import annotations

import sys

MINOR = sys.version_info.minor


if MINOR >= 11:
    import tomllib

    toml_parser = tomllib.load
    TOMLDecodeError = tomllib.TOMLDecodeError
else:  # TODO (py3.10): Use tomllib
    import tomli

    toml_parser = tomli.load
    TOMLDecodeError = tomli.TOMLDecodeError
