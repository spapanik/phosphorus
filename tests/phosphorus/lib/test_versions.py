import pytest

from phosphorus.lib import versions


def test_release_trailing_zeroes() -> None:
    major = versions.Release.from_string("1")
    minor = versions.Release.from_string("1.0")
    micro = versions.Release.from_string("1.0.0")
    assert major == minor
    assert minor == micro


def test_release_implied_segments() -> None:
    release = versions.Release.from_string("1")
    assert release.major == 1
    assert release.minor == 0
    assert release.micro == 0


@pytest.mark.parametrize(
    ("big", "small"),
    [
        ("1.1.post1", "1.1"),
        ("1.1", "1.1.rc1"),
        ("1.1.rc1", "1.1.b1"),
        ("1.1.b1", "1.1.a1"),
        ("1.1.a1", "1.1.dev1"),
    ],
)
def test_version_comparison(big: str, small: str) -> None:
    assert versions.Version.from_string(big) > versions.Version.from_string(small)


@pytest.mark.parametrize(
    ("version_string", "match_all", "epoch"),
    [("1.2.*", False, 0), ("*", True, -1), ("15!*", True, 15)],
)
def test_version_wildcards(version_string: str, match_all: bool, epoch: int) -> None:
    version = versions.Version.from_string(version_string)
    assert version.prefix_match is True
    assert version.match_all is match_all
    assert version.epoch.epoch == epoch


@pytest.mark.parametrize(
    ("candidate", "clause", "match"),
    [
        ("1.2", "*", True),
        ("1.2", "0!*", True),
        ("1.2", "1!*", False),
        ("1.2", "==1.2", True),
        ("1.2", "==1!1.2", False),
        ("1.2", "==1.2.*", True),
        ("1.2", "==1.2.post1", False),
        ("1.2", "==1.2.*", True),  # noqa: PT014
        ("1.2.0.5", "==1.2.*", True),
        ("1.2.0.5-1", "==1.2.*", True),
        ("1.2.a1", "==1.2.*", True),
        ("1.2.7", "==1.2.*", True),
        ("1.2", "==1.2.0.*", True),
        ("1.2.0.5", "==1.2.0.*", True),
        ("1.2.0.5-1", "==1.2.0.*", True),
        ("1.2.a1", "==1.2.0.*", True),
        ("1.2.7", "==1.2.0.*", False),
        ("1.2", "==*", True),
        ("1.2", "==1!*", False),
        ("1.2+local", "==1.2", True),
        ("1.2", "==1.2+local", False),
        ("1.2", "!=1.2", False),
        ("1.2", "!=1!1.2", True),
        ("1.2", "!=1.2.*", False),
        ("1.2", "!=1.2.post1", True),
        ("1.2", "!=1.2.*", False),  # noqa: PT014
        ("1.2.0.5", "!=1.2.*", False),
        ("1.2.0.5-1", "!=1.2.*", False),
        ("1.2.a1", "!=1.2.*", False),
        ("1.2.7", "!=1.2.*", False),
        ("1.2", "!=1.2.0.*", False),
        ("1.2.0.5", "!=1.2.0.*", False),
        ("1.2.0.5-1", "!=1.2.0.*", False),
        ("1.2.a1", "!=1.2.0.*", False),
        ("1.2.7", "!=1.2.0.*", True),
        ("1.2", "!=*", False),
        ("1.2", "!=1!*", True),
        ("1.2+local", "!=1.2", False),
        ("1.2", "!=1.2+local", True),
        ("1.2", "~=1.2", True),
        ("1!1.2", "~=1.2", False),
        ("1.2", "~=1!1.2", False),
        ("1.2", "~=1.2.post1", False),
        ("1.3", "~=1.2", True),
        ("1.2.42", "~=1.2", True),
        ("1.2.42", "~=1.2.43", False),
        ("1.2+local", "~=1.2", True),
        ("1!1.2", ">=1.2", True),
        ("1.2", ">=1!1.2", False),
        ("1.2", ">=1.2.post1", False),
        ("1.3", ">=1.2", True),
        ("1.2.42", ">=1.2", True),
        ("1.2.42", ">=1.2.43", False),
        ("1.2+local", ">=1.2", True),
        ("1.2.1", ">=1.2.0.5", True),
        ("1!1.2", "<=1.2", False),
        ("1.2", "<=1!1.2", True),
        ("1.2", "<=1.2.post1", True),
        ("1.3", "<=1.2", False),
        ("1.2.42", "<=1.2", False),
        ("1.2.42", "<=1.2.43", True),
        ("1.2+local", "<=1.2", False),
        ("1.2.1", "<=1.2.0.5", False),
        ("1.2", ">=1.2", True),
        ("1.2", "<=1.2", True),
        ("1.2", ">=1.2.0", True),
        ("1.2", "<=1.2.0", True),
        ("1!1.2", ">1.2", True),
        ("1.2", ">1!1.2", False),
        ("1.2", ">1.2.post1", False),
        ("1.3", ">1.2", True),
        ("1.2.42", ">1.2", True),
        ("1.2.42", ">1.2.43", False),
        ("1.2+local", ">1.2", False),
        ("1.2.1", ">1.2.0.5", True),
        ("1.7.1", ">1.7", True),
        ("1.7.0.post1", ">1.7", False),
        ("1.7.1", ">1.7.post2", True),
        ("1.7.0.post3", ">1.7.post2", True),
        ("1.7.0", ">1.7.post2", False),
        ("1!1.2", "<1.2", False),
        ("1.2", "<1!1.2", True),
        ("1.2", "<1.2.post1", True),
        ("1.3", "<1.2", False),
        ("1.3", "<1.4", True),
        ("1.2.42", "<1.2", False),
        ("1.2.42", "<1.2.43", True),
        ("1.2+local", "<1.2", False),
        ("1.2.1", "<1.2.0.5", False),
        ("1.7.1", "<1.7", False),
        ("1.7.0.rc1", "<1.7", False),
        ("1.7.0.dev999", "<1.7", False),
        ("1.7.1", "<1.7.1.rc2", False),
        ("1.7.1.rc1", "<1.7.1.rc2", True),
        ("1.7.0", "<1.7.1.rc2", True),
    ],
)
def test_version_matching(candidate: str, clause: str, match: bool) -> None:
    candidate_version = versions.Version.from_string(candidate)
    version_clause = versions.VersionClause.from_string(clause)
    assert version_clause.match(candidate_version) is match
