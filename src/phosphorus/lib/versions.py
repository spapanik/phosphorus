from __future__ import annotations

from dataclasses import dataclass, field
from functools import total_ordering
from itertools import dropwhile
from typing import TYPE_CHECKING, Any

from phosphorus.lib.constants import ComparisonOperator
from phosphorus.lib.exceptions import UnreachableCodeError
from phosphorus.lib.regex import version_pattern, version_separators

if TYPE_CHECKING:
    from phosphorus.lib.types import Match


@dataclass(frozen=True, order=True)  # TODO (py3.9): Use slots=True
class Epoch:
    epoch: int

    @classmethod
    def from_string(cls, match: Match) -> Epoch:  # TODO (py3.10): Use Self
        return cls(epoch=int(match or 0))

    def __str__(self) -> str:
        return f"{self.epoch}!" if self.epoch else ""


@dataclass(frozen=True, order=True)  # TODO (py3.9): Use slots=True
class Release:
    release: tuple[int, ...]
    full_release: tuple[int, ...] = field(repr=False, compare=False)

    def __init__(self, full_release: tuple[int, ...]) -> None:
        release = tuple(
            reversed(list(dropwhile(lambda x: x == 0, reversed(full_release))))
        )
        object.__setattr__(self, "release", release)
        object.__setattr__(self, "full_release", full_release)

    @classmethod
    def from_string(cls, match: str) -> Release:  # TODO (py3.10): Use Self
        full_release = tuple(int(segment) for segment in match.split("."))
        return cls(full_release=full_release)

    def __str__(self) -> str:
        return ".".join(str(x) for x in self.full_release)

    @property
    def canonical_form(self) -> str:
        return ".".join(str(x) for x in self.release)

    @property
    def major(self) -> int:
        return self.release[0]

    @property
    def minor(self) -> int:
        try:
            return self.release[1]
        except IndexError:
            return 0

    @property
    def micro(self) -> int:
        try:
            return self.release[2]
        except IndexError:
            return 0

    def padded(self, zeroes: int) -> Release:  # TODO (py3.10): Use Self
        n = len(self.release)
        if zeroes < n:
            msg = "Padding cannot truncate the release"
            raise ValueError(msg)
        if zeroes == n:
            return self
        full_release = self.release + (0,) * (zeroes - n)
        return self.__class__(full_release)


@dataclass(frozen=True, order=True)  # TODO (py3.9): Use slots=True
class Pre:
    letter: str
    number: int

    @classmethod
    def from_string(
        cls, match_letter: Match, match_number: Match
    ) -> Pre:  # TODO (py3.10): Use Self
        number = int(match_number or 0)
        letter = cls._canonicalize_letter(match_letter) if match_letter else "z"
        return cls(letter=letter, number=number)

    def __bool__(self) -> bool:
        return self.letter != "z"

    def __str__(self) -> str:
        return f"{self.letter}{self.number}" if self else ""

    @staticmethod
    def _canonicalize_letter(letter: str) -> str:
        letter = letter.lower()

        if letter == "alpha":
            return "a"
        if letter == "beta":
            return "b"
        if letter in {"c", "pre", "preview"}:
            return "rc"

        return letter


@dataclass(frozen=True, order=True)  # TODO (py3.9): Use slots=True
class Post:
    post: int

    @classmethod
    def from_string(
        cls, match_letter: Match, match_number: Match
    ) -> Post:  # TODO (py3.10): Use Self
        return cls(post=int(match_number or 0) if match_letter or match_number else -1)

    def __bool__(self) -> bool:
        return self.post >= 0

    def __str__(self) -> str:
        return f".post{self.post}" if self else ""


@dataclass(frozen=True, order=True)  # TODO (py3.9): Use slots=True
class Dev:
    dev: int | float

    @classmethod
    def from_string(
        cls, match_letter: Match, match_number: Match
    ) -> Dev:  # TODO (py3.10): Use Self
        return cls(dev=int(match_number or 0) if match_letter else float("inf"))

    def __bool__(self) -> bool:
        return self.dev != float("inf")

    def __str__(self) -> str:
        return f".dev{self.dev}" if self else ""


@dataclass(frozen=True, order=True)  # TODO (py3.9): Use slots=True
class Local:
    local: tuple[str | int, ...]

    @classmethod
    def from_string(cls, match: Match) -> Local:  # TODO (py3.10): Use Self
        local_version = (
            tuple(
                int(part) if part.isdigit() else part.lower()
                for part in version_separators.split(match)
            )
            if match
            else ()
        )
        return cls(local=local_version)

    def __bool__(self) -> bool:
        return bool(self.local)

    def __str__(self) -> str:
        if not self.local:
            return ""
        canonical_local = ".".join(str(part) for part in self.local)
        return f"+{canonical_local}"


@total_ordering
@dataclass(frozen=True)  # TODO (py3.9): Use slots=True
class Version:
    epoch: Epoch
    release: Release
    post: Post
    pre: Pre
    dev: Dev
    local: Local
    prefix_match: bool = field(repr=False, default=False)
    match_all: bool = field(repr=False, default=False)
    pep_440_compliant: bool = field(repr=False, default=True)

    @classmethod
    def from_string(cls, version: str) -> Version:  # TODO (py3.10): Use Self
        if version == "*" or version.endswith("!*"):
            epoch = int(version[:-2]) if version.endswith("!*") else -1
            return cls(
                epoch=Epoch.from_string(str(epoch)),
                release=Release.from_string("0"),
                pre=Pre.from_string(None, None),
                post=Post.from_string(None, None),
                dev=Dev.from_string(None, None),
                local=Local.from_string(None),
                prefix_match=True,
                match_all=True,
            )
        if version.endswith(".*"):
            prefix_match = True
            version = version[:-2]
        else:
            prefix_match = False
        match = version_pattern.search(version.strip())
        if not match:
            return cls(
                epoch=Epoch(epoch=-2),
                release=Release.from_string("0"),
                pre=Pre.from_string(None, None),
                post=Post.from_string(None, None),
                dev=Dev.from_string(None, None),
                local=Local.from_string(version),
                pep_440_compliant=False,
            )

        if prefix_match and (match.group("dev_l") or match.group("local")):
            msg = "Prefix match containing a dev or local release is invalid"
            raise RuntimeError(msg)
        return cls(
            epoch=Epoch.from_string(match.group("epoch")),
            release=Release.from_string(match.group("release")),
            pre=Pre.from_string(match.group("pre_l"), match.group("pre_n")),
            post=Post.from_string(
                match.group("post_l"), match.group("post_n1") or match.group("post_n2")
            ),
            dev=Dev.from_string(match.group("dev_l"), match.group("dev_n")),
            local=Local.from_string(match.group("local")),
            prefix_match=prefix_match,
        )

    def __repr__(self) -> str:
        pre = (self.pre.letter, self.pre.number) if self.is_pre_release else None
        post = self.post.post if self.is_post_release else None
        dev = self.dev.dev if self.is_dev_release else None
        return (
            "Version("
            f"epoch={self.epoch.epoch}, "
            f"release={self.release.full_release}, "
            f"pre={pre}, "
            f"post={post}, "
            f"dev={dev}, "
            f"local={self.local.local or None}"
            ")"
        )

    def __str__(self) -> str:
        return f"{self.epoch}{self.release}{self.pre}{self.post}{self.dev}{self.local}"

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, Version):
            return NotImplemented

        if self.epoch != other.epoch:
            return self.epoch < other.epoch

        if self.release != other.release:
            return self.release < other.release

        if self.post != other.post:
            return self.post < other.post

        if self.is_dev_release ^ other.is_dev_release:
            return self.is_dev_release

        if self.pre != other.pre:
            return self.pre < other.pre

        if self.dev != other.dev:
            return self.dev < other.dev

        return self.local < other.local

    @property
    def major(self) -> int:
        return self.release.major

    @property
    def minor(self) -> int:
        return self.release.minor

    @property
    def micro(self) -> int:
        return self.release.micro

    @property
    def is_post_release(self) -> bool:
        return bool(self.post)

    @property
    def is_pre_release(self) -> bool:
        return bool(self.pre)

    @property
    def is_dev_release(self) -> bool:
        return bool(self.dev)

    @property
    def is_base_version(self) -> bool:
        return not (self.post or self.pre or self.dev or self.local)

    @property
    def base_version(self) -> Version:  # TODO (py3.10): Use Self
        if self.is_base_version:
            return self
        return self.__class__.from_string(f"{self.epoch}{self.release}")

    @property
    def canonical_form(self) -> str:
        return f"{self.epoch}{self.release.canonical_form}{self.pre}{self.post}{self.dev}{self.local}"

    @property
    def public_version(self) -> Version:  # TODO (py3.10): Use Self
        return self.__class__.from_string(
            f"{self.epoch}{self.release.canonical_form}{self.pre}{self.post}{self.dev}"
        )

    def padded(self, zeroes: int) -> Version:  # TODO (py3.10): Use Self
        release = self.release.padded(zeroes)
        if release.full_release == self.release.full_release:
            return self
        return self.__class__(
            epoch=self.epoch,
            release=release,
            post=self.post,
            pre=self.pre,
            dev=self.dev,
            local=self.local,
            prefix_match=self.prefix_match,
            match_all=self.match_all,
        )


@dataclass(frozen=True, order=True)  # TODO (py3.9): Use slots=True
class VersionClause:
    operator: ComparisonOperator
    identifier: Version

    def __post_init__(self) -> None:
        if self.operator in ComparisonOperator.env_marker_operator():
            msg = f"Only environment markers are permitted to use `{self.operator}`"
            raise RuntimeError(msg)
        if not self.identifier.pep_440_compliant:
            if self.operator != ComparisonOperator.EXACT_MATCH:
                msg = "Non PEP-440 versions can only be compared with ==="
                raise RuntimeError(msg)
            return
        if self.operator in ComparisonOperator.non_local_operator():
            if self.identifier.local:
                msg = "Local version identifiers are not permitted with this type of clause"
                raise RuntimeError(msg)
            if (
                self.operator == ComparisonOperator.COMPATIBLE_WITH
                and len(self.identifier.release.full_release) == 1
            ):
                msg = (
                    "Compatible release operator is not permitted with single segments"
                )
                raise RuntimeError(msg)
        if (
            self.operator not in ComparisonOperator.prefix_match_operator()
            and self.identifier.prefix_match
        ):
            msg = "Prefix match is only allowed in match or exclusion"
            raise RuntimeError(msg)

    def __str__(self) -> str:
        return f"{self.operator}{self.identifier}"

    @classmethod
    def from_string(cls, clause: str) -> VersionClause:  # TODO (py3.10): Use Self
        for candidate in ComparisonOperator:
            if clause.startswith(candidate.value):
                operator_length = len(candidate.value)
                operator = candidate
                break
        else:
            operator_length = 0
            operator = ComparisonOperator.EQUAL_TO

        return cls(
            operator=operator, identifier=Version.from_string(clause[operator_length:])
        )

    def match(self, candidate: Version) -> bool:
        if not (self.identifier.pep_440_compliant and candidate.pep_440_compliant):
            return self.match_exact(candidate)

        if (
            self.operator == ComparisonOperator.COMPATIBLE_WITH
        ):  # TODO (py3.9): Use match
            return self.match_compatible(candidate)
        if self.operator == ComparisonOperator.EQUAL_TO:
            return self.match_equality(candidate)
        if self.operator == ComparisonOperator.NOT_EQUAL:
            return not self.match_equality(candidate)
        if self.operator == ComparisonOperator.LESS_OR_EQUAL:
            return self.match_leq(candidate)
        if self.operator == ComparisonOperator.GREATER_OR_EQUAL:
            return self.match_geq(candidate)
        if self.operator == ComparisonOperator.LESS_THAN:
            return self.match_lt(candidate)
        if self.operator == ComparisonOperator.GREATER_THAN:
            return self.match_gt(candidate)
        if self.operator == ComparisonOperator.EXACT_MATCH:
            return self.match_exact(candidate)

        raise UnreachableCodeError

    def match_compatible(self, candidate: Version) -> bool:
        if not self.match_geq(candidate):
            return False

        release_parts = str(self.identifier.release).split(".")
        release_parts[-1] = "*"
        wildcard = Version.from_string(
            f"{self.identifier.epoch}{'.'.join(release_parts)}"
        )
        return VersionClause(
            operator=ComparisonOperator.EQUAL_TO, identifier=wildcard
        ).match(candidate)

    def match_equality(self, candidate: Version) -> bool:
        if candidate.epoch != self.identifier.epoch:
            return self.identifier.epoch.epoch == -1

        if self.identifier.match_all:
            return True

        if not self.identifier.prefix_match:
            if self.identifier.local.local:
                return candidate == self.identifier
            return candidate.public_version == self.identifier.public_version

        if not self.identifier.is_base_version:
            return candidate.canonical_form.startswith(self.identifier.canonical_form)

        if not candidate.is_base_version:
            candidate = candidate.base_version

        n = len(self.identifier.release.full_release)
        if len(candidate.release.full_release) <= n:
            candidate = candidate.padded(n)
        return str(candidate).startswith(str(self.identifier))

    def match_leq(self, candidate: Version) -> bool:
        return candidate <= self.identifier

    def match_geq(self, candidate: Version) -> bool:
        return candidate >= self.identifier

    def match_lt(self, candidate: Version) -> bool:
        candidate = candidate.public_version

        if self.identifier.is_pre_release:
            return candidate < self.identifier

        return candidate.base_version < self.identifier

    def match_gt(self, candidate: Version) -> bool:
        candidate = candidate.public_version

        if self.identifier.is_post_release:
            return candidate > self.identifier

        return candidate.base_version > self.identifier

    def match_exact(self, candidate: Version) -> bool:
        return candidate == self.identifier
