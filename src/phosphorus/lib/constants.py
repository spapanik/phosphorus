from __future__ import annotations

import re
from enum import Enum, unique
from pathlib import Path

package_cache = Path.home().joinpath(".cache/phosphorus/packages/")
pypi_cache = package_cache.joinpath("PyPI")
pyproject_base_name = "pyproject.toml"
lock_file_name = "p-lock.toml"
hash_prefix = "--hash=sha256:"

# Accept the British spelling for the noun
licence_base_names = {"COPYING", "LICENCE", "LICENCES", "LICENSE", "LICENSES"}


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
    IN = "in"
    NOT_IN = "not in"

    def __str__(self) -> str:
        return self.value

    @classmethod
    def prefix_match_operator(cls) -> set[ComparisonOperator]:
        return {cls.EQUAL_TO, cls.NOT_EQUAL}

    @classmethod
    def env_marker_operator(cls) -> set[ComparisonOperator]:
        return {cls.IN, cls.NOT_IN}

    @classmethod
    def non_local_operator(cls) -> set[ComparisonOperator]:
        return {
            cls.LESS_THAN,
            cls.LESS_OR_EQUAL,
            cls.GREATER_OR_EQUAL,
            cls.GREATER_THAN,
            cls.COMPATIBLE_WITH,
        }


@unique
class BooleanOperator(Enum):
    AND = "and"
    OR = "or"

    def __str__(self) -> str:
        return self.value


@unique
class MarkerVariable(Enum):
    PYTHON_VERSION = "python_version"
    PYTHON_FULL_VERSION = "python_full_version"
    OS_NAME = "os_name"
    SYS_PLATFORM = "sys_platform"
    PLATFORM_RELEASE = "platform_release"
    PLATFORM_SYSTEM = "platform_system"
    PLATFORM_VERSION = "platform_version"
    PLATFORM_MACHINE = "platform_machine"
    PLATFORM_PYTHON_IMPLEMENTATION = "platform_python_implementation"
    IMPLEMENTATION_NAME = "implementation_name"
    IMPLEMENTATION_VERSION = "implementation_version"
    EXTRA = "extra"

    def __str__(self) -> str:
        return self.value


class TokenRule(Enum):
    LEFT_PARENTHESIS = re.compile(r"\(")
    RIGHT_PARENTHESIS = re.compile(r"\)")
    WHITESPACE = re.compile(r"[ \t]+")
    OPERATOR = re.compile(r"(===|==|~=|!=|<=|>=|<|>)")
    BOOLEAN_OPERATOR = re.compile(r"\b(or|and)\b")
    IN = re.compile(r"\bin\b")
    NOT_IN = re.compile(r"\bnot[ \t]+in\b")
    QUOTED_STRING = re.compile(
        r"""
            (
                ('[^']*')
                |
                ("[^"]*")
            )
        """,
        re.VERBOSE,
    )
    VARIABLE = re.compile(
        r"""
            \b(
                python_version
                |python_full_version
                |os[._]name
                |sys[._]platform
                |platform_(release|system)
                |platform[._](version|machine|python_implementation)
                |python_implementation
                |implementation_(name|version)
                |extra
            )\b
        """,
        re.VERBOSE,
    )
