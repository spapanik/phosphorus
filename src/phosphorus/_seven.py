from __future__ import annotations

import sys

MINOR = sys.version_info.minor


if MINOR >= 9:  # noqa: PLR2004
    remove_prefix = str.removeprefix
else:

    def remove_prefix(s: str, prefix: str) -> str:  # TODO (py3.9): Use str.removeprefix
        if s.startswith(prefix):
            return s[len(prefix) :]
        return s


if MINOR >= 11:  # noqa: PLR2004
    import tomllib

    toml_parser = tomllib.load
    TOMLDecodeError = tomllib.TOMLDecodeError
else:  # TODO (py3.10): Use tomllib
    import tomli

    toml_parser = tomli.load
    TOMLDecodeError = tomli.TOMLDecodeError
