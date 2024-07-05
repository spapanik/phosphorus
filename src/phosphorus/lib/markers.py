from __future__ import annotations

import ast
from contextlib import contextmanager
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from phosphorus.lib.constants import (
    BooleanOperator,
    ComparisonOperator,
    MarkerVariable,
    TokenRule,
)
from phosphorus.lib.exceptions import UnreachableCodeError
from phosphorus.lib.utils import canonicalise_name
from phosphorus.lib.versions import Version, VersionClause

if TYPE_CHECKING:
    import re
    from collections.abc import Iterator


@dataclass(frozen=True)  # TODO (py3.9): Use slots=True
class MarkerAtom:
    variable: MarkerVariable
    operator: ComparisonOperator
    value: str

    def __str__(self) -> str:
        return f"{self.variable} {self.operator} '{self.value}'"

    @classmethod
    def from_dict(cls, specs: dict[str, Any]) -> MarkerAtom:  # TODO (py3.10): Use Self
        variable = specs["variable"]
        if isinstance(variable, str):
            variable = MarkerVariable(variable)

        operator = specs["operator"]
        if isinstance(operator, str):
            operator = ComparisonOperator(operator)

        return cls(variable=variable, operator=operator, value=specs["value"])

    def evaluate(self, extra: str = "") -> bool:
        environment_value = self.variable.get_env_value(extra)
        if self.operator == ComparisonOperator.IN:  # TODO (py3.9): Use match
            return environment_value in self.value
        if self.operator == ComparisonOperator.NOT_IN:
            return environment_value in self.value
        if self.variable in {
            MarkerVariable.PYTHON_VERSION,
            MarkerVariable.PYTHON_FULL_VERSION,
            MarkerVariable.IMPLEMENTATION_VERSION,
            MarkerVariable.PLATFORM_VERSION,
        }:
            clause = VersionClause(
                operator=self.operator,
                identifier=Version.from_string(self.value),
            )
            return clause.match(Version.from_string(environment_value))
        if self.operator in {
            ComparisonOperator.COMPATIBLE_WITH,
            ComparisonOperator.EXACT_MATCH,
        }:
            msg = f"Cannot compare `{self.variable}` with `{self.operator}`"
            raise ValueError(msg)
        if self.operator == ComparisonOperator.EQUAL_TO:
            return environment_value == self.value
        if self.operator == ComparisonOperator.NOT_EQUAL:
            return environment_value != self.value
        if self.operator == ComparisonOperator.LESS_OR_EQUAL:
            return environment_value <= self.value
        if self.operator == ComparisonOperator.GREATER_OR_EQUAL:
            return environment_value >= self.value
        if self.operator == ComparisonOperator.LESS_THAN:
            return environment_value < self.value
        if self.operator == ComparisonOperator.GREATER_THAN:
            return environment_value > self.value

        raise UnreachableCodeError


@dataclass(frozen=True)  # TODO (py3.9): Use slots=True
class Marker:
    boolean: BooleanOperator | None
    markers: tuple[Marker | MarkerAtom, ...]

    @classmethod
    def from_string(cls, marker_string: str) -> Marker:
        return MarkerParser(marker_string).parse()

    def __str__(self) -> str:
        if not self.markers:
            return ""

        if self.boolean is None:
            return str(self.markers[0])

        joiner = f" {self.boolean} "
        return joiner.join(
            str(marker) if isinstance(marker, MarkerAtom) else f"({marker})"
            for marker in self.markers
        )

    @classmethod
    def from_dict(cls, specs: dict[str, Any]) -> Marker:  # TODO (py3.10): Use Self
        boolean = specs.get("boolean")
        if isinstance(boolean, str):
            boolean = BooleanOperator(boolean)
        markers: list[Marker | MarkerAtom] = []
        if "markers" not in specs:
            return cls(boolean=None, markers=(MarkerAtom.from_dict(specs),))
        for marker in specs["markers"]:
            variable = marker.get("variable")
            if isinstance(variable, str):
                variable = MarkerVariable(variable)
            if isinstance(variable, MarkerVariable):  # TODO (py3.9): Use match
                markers.append(MarkerAtom.from_dict(marker))
            else:
                markers.append(cls.from_dict(marker))

        return cls(boolean=boolean, markers=tuple(markers))

    def evaluate(self, extra: str = "") -> bool:
        if not self.markers:
            return True

        if self.boolean == BooleanOperator.OR:  # TODO (py3.9): Use match
            return any(marker.evaluate(extra) for marker in self.markers)
        if self.boolean == BooleanOperator.AND:
            return all(marker.evaluate(extra) for marker in self.markers)
        return self.markers[0].evaluate(extra)


@dataclass(frozen=True)  # TODO (py3.9): Use slots=True
class Token:
    name: re.Pattern[str]
    text: str
    position: int


class MarkerParser:
    def __init__(self, marker_string: str) -> None:
        self.string = marker_string
        self.next_token: Token | None = None
        self.position = 0

    def parse(self) -> Marker:
        if not self.string:
            return Marker(boolean=None, markers=())

        marker = self.to_dict(self.parse_marker())
        if isinstance(marker, MarkerAtom):
            return Marker(boolean=None, markers=(marker,))
        return marker

    @classmethod
    def to_dict(cls, parsed_marker: list[Any] | MarkerAtom) -> Marker | MarkerAtom:
        if isinstance(parsed_marker, MarkerAtom):
            return parsed_marker

        if len(parsed_marker) == 1:
            return cls.to_dict(parsed_marker[0])

        operators = {
            operator for index, operator in enumerate(parsed_marker) if index % 2
        }
        if len(operators) == 1:
            return Marker(
                boolean=parsed_marker[1],
                markers=tuple(
                    cls.to_dict(sub_marker)
                    for index, sub_marker in enumerate(parsed_marker)
                    if not index % 2
                ),
            )

        grouped_markers = cls.group_boolean_operators(parsed_marker)
        return cls.to_dict(grouped_markers)

    @staticmethod
    def group_boolean_operators(ungrouped: list[Any]) -> list[Any]:
        output: list[Any] = []
        tmp: list[Any] = []
        for i in range(len(ungrouped) // 2):
            op = ungrouped[2 * i + 1]
            if op == BooleanOperator.OR and tmp:
                tmp.append(ungrouped[2 * i])
                output.extend([tmp, BooleanOperator.OR])
                tmp = []
            elif op == BooleanOperator.OR:
                output.extend([ungrouped[2 * i], BooleanOperator.OR])
            else:
                tmp.extend([ungrouped[2 * i], BooleanOperator.AND])
        if tmp:
            tmp.append(ungrouped[-1])
            output.append(tmp)
        else:
            output.append(ungrouped[-1])
        return output

    def parse_marker(self) -> list[Any]:
        expression: list[Any] = [self.parse_marker_atom()]
        while self.check(TokenRule.BOOLEAN_OPERATOR):
            token = self.read()
            expr_right = self.parse_marker_atom()
            expression.extend([BooleanOperator(token.text), expr_right])
        return expression

    def parse_marker_atom(self) -> list[Any] | MarkerAtom:
        marker: list[Any] | MarkerAtom
        self.consume(TokenRule.WHITESPACE)
        if self.check(TokenRule.LEFT_PARENTHESIS, prepare_token=False):
            with self.enclosing_tokens(
                TokenRule.LEFT_PARENTHESIS, TokenRule.RIGHT_PARENTHESIS
            ):
                self.consume(TokenRule.WHITESPACE)
                marker = self.parse_marker()
                self.consume(TokenRule.WHITESPACE)
        else:
            marker = self.parse_marker_item()
        self.consume(TokenRule.WHITESPACE)
        return marker

    def parse_marker_item(self) -> MarkerAtom:
        self.consume(TokenRule.WHITESPACE)
        marker_left = self.parse_marker_var_or_str()
        self.consume(TokenRule.WHITESPACE)
        marker_op = self.parse_marker_op()
        self.consume(TokenRule.WHITESPACE)
        marker_right = self.parse_marker_var_or_str()
        self.consume(TokenRule.WHITESPACE)

        if isinstance(marker_right, MarkerVariable):
            marker_left, marker_right = marker_right, marker_left
        if not (
            isinstance(marker_left, MarkerVariable) and isinstance(marker_right, str)
        ):
            msg = "Expected a marker variable and a string"
            raise TypeError(msg)

        if marker_left == MarkerVariable.EXTRA:
            marker_right = canonicalise_name(marker_right)
        return MarkerAtom(variable=marker_left, operator=marker_op, value=marker_right)

    def parse_marker_op(self) -> ComparisonOperator:
        if self.check(TokenRule.IN):
            self.read()
            return ComparisonOperator.IN
        if self.check(TokenRule.NOT_IN):
            self.read()
            return ComparisonOperator.NOT_IN
        if self.check(TokenRule.OPERATOR):
            return ComparisonOperator(self.read().text)
        msg = "Expected a marker operator."
        raise ValueError(msg)

    def parse_marker_var_or_str(self) -> MarkerVariable | str:
        if self.check(TokenRule.VARIABLE):
            return MarkerVariable(self.read().text.replace(".", "_"))
        if self.check(TokenRule.QUOTED_STRING):
            return str(ast.literal_eval(self.read().text))
        msg = "Expected a marker variable"
        raise ValueError(msg)

    def consume(self, name: TokenRule) -> None:
        if self.check(name):
            self.read()

    def check(self, rule: TokenRule, *, prepare_token: bool = True) -> bool:
        expression = rule.value

        match = expression.match(self.string, self.position)
        if match is None:
            return False

        if prepare_token:
            self.next_token = Token(expression, match[0], self.position)

        return True

    def read(self) -> Token:
        token = self.next_token

        if token is None:
            msg = "No token to read"
            raise RuntimeError(msg)

        self.position += len(token.text)
        self.next_token = None

        return token

    @contextmanager
    def enclosing_tokens(
        self, open_token: TokenRule, close_token: TokenRule
    ) -> Iterator[None]:
        if self.check(open_token):
            open_position = self.position
            self.read()
        else:
            open_position = None

        yield

        if open_position is None:
            return

        if not self.check(close_token):
            msg = f"Expected matching {close_token} for {open_token}"
            raise RuntimeError(msg)

        self.read()
