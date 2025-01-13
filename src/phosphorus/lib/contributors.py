from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable

    from typing_extensions import Self  # upgrade: py3.10: import from typing

    from phosphorus.lib.type_defs import Author


@dataclass(frozen=True, order=True)  # upgrade: py3.9: Use slots=True
class Contributor:
    name: str
    email: str

    @classmethod
    def from_data(cls, data: Author) -> Self:
        return cls(name=data.get("name", ""), email=data.get("email", ""))

    def formatted_email(self) -> str:
        if not self.email:
            return ""

        if not self.name:
            return self.email

        return f'"{self.name}" <{self.email}>'

    @staticmethod
    def stringify_names(contributors: Iterable[Contributor]) -> str:
        return ",".join(
            contributor.name for contributor in contributors if contributor.name
        )

    @staticmethod
    def stringify_emails(contributors: Iterable[Contributor]) -> str:
        return ",".join(
            contributor.formatted_email()
            for contributor in contributors
            if contributor.email
        )
