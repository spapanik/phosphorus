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
