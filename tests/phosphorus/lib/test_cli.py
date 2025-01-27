from unittest import mock

import pytest

from phosphorus.lib.cli import parse_args


@pytest.mark.parametrize(
    ("verbose", "expected_verbosity"),
    [("-v", 1), ("-vv", 2), ("-vvvvv", 5)],
)
def test_phosphorus_verbose(verbose: str, expected_verbosity: int) -> None:
    with mock.patch("sys.argv", ["p", "build", verbose]):
        args = parse_args()

    assert args.verbosity == expected_verbosity


@pytest.mark.parametrize(
    ("options", "sdist", "wheel"),
    [("--no-sdist", False, True), ("--no-wheel", True, False)],
)
def test_phosphorus_run_build_mode(options: str, sdist: bool, wheel: bool) -> None:
    with mock.patch("sys.argv", ["p", "build", options]):
        args = parse_args()
    assert args.sdist is sdist
    assert args.wheel is wheel
    assert args.verbosity == 0


@mock.patch("sys.argv", ["p", "new_subcommand"])
def test_phosphorus_unknown_subcommand() -> None:
    with pytest.raises(SystemExit, match="2"):
        parse_args()
