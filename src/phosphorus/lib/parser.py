import sys
from argparse import ArgumentParser, BooleanOptionalAction, Namespace

from phosphorus.__version__ import __version__

sys.tracebacklimit = 0


def add_build_args(parser: ArgumentParser) -> None:
    parser.add_argument("--metadata", action=BooleanOptionalAction, default=False)
    parser.add_argument("--sdist", action=BooleanOptionalAction, default=True)
    parser.add_argument("--wheel", action=BooleanOptionalAction, default=True)


def parse_args() -> Namespace:
    parser = ArgumentParser(description="a dependency management tool")
    parser = ArgumentParser(description="git repository manager")
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"phosphorus {__version__}",
        help="print the version and exit",
    )

    parent_parser = ArgumentParser(add_help=False)
    parent_parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        dest="verbosity",
        help="increase the level of verbosity",
    )

    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    build_parser = subparsers.add_parser(
        "build",
        parents=[parent_parser],
        help="build the wheel and the sdist distributions for the package",
    )
    build_parser.add_argument(
        "--sdist",
        action=BooleanOptionalAction,
        default=True,
        help="build the sdist distribution",
    )
    build_parser.add_argument(
        "--wheel",
        action=BooleanOptionalAction,
        default=True,
        help="build the wheel distribution",
    )

    lock_parser = subparsers.add_parser(
        "lock", parents=[parent_parser], help="lock the project dependencies"
    )
    lock_parser.add_argument(
        "-f", "--force", action="store_true", help="force recreating the lock"
    )
    lock_parser.add_argument(
        "--enforce-pep440",
        action=BooleanOptionalAction,
        default=True,
        help="enforce PEP 440",
    )
    lock_parser.add_argument(
        "--allow-pre-releases",
        action=BooleanOptionalAction,
        default=False,
        help="allow pre-releases",
    )
    lock_parser.add_argument(
        "--allow-dev-releases",
        action=BooleanOptionalAction,
        default=False,
        help="allow dev releases",
    )

    args = parser.parse_args()
    if args.verbosity > 0:
        sys.tracebacklimit = 1000

    return args
