from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable


@dataclass(frozen=True, order=True)  # TODO (py3.9): Use slots=True
class Contributor:
    name: str
    email: str

    @classmethod
    def from_data(cls, data: dict[str, str]) -> Contributor:  # TODO (py3.10): Use Self
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
