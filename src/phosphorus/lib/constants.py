from __future__ import annotations

from enum import Enum, unique
from pathlib import Path

package_cache = Path.home().joinpath(".cache/phosphorus/packages/")
pypi_cache = package_cache.joinpath("PyPI")


@unique
class ComparisonOperator(Enum):
    EXACT_MATCH = "==="
    EQUAL_TO = "=="
    NOT_EQUAL = "!="
    COMPATIBLE_WITH = "~="
    LESS_OR_EQUAL = "<="
    GREATER_OR_EQUAL = ">="
    LESS_THAN = "<"
    GREATER_THAN = ">"

    def __str__(self) -> str:
        return self.value

    @classmethod
    def prefix_match_operator(cls) -> set[ComparisonOperator]:
        return {cls.EQUAL_TO, cls.NOT_EQUAL}

    @classmethod
    def non_local_operator(cls) -> set[ComparisonOperator]:
        return {
            cls.LESS_THAN,
            cls.LESS_OR_EQUAL,
            cls.GREATER_OR_EQUAL,
            cls.GREATER_THAN,
            cls.COMPATIBLE_WITH,
        }
