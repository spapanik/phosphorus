from dataclasses import dataclass, field

from phosphorus.lib.utils import canonicalise_name


@dataclass(frozen=True, order=True)  # upgrade: py3.9: Use slots=True
class Package:
    name: str
    distribution_name: str = field(repr=False, compare=False)

    def __init__(self, name: str) -> None:
        name = canonicalise_name(name)
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "distribution_name", name.replace("-", "_"))

    def __str__(self) -> str:
        return self.name
