import sys
from argparse import ArgumentParser

from phosphorus.__version__ import __version__
from phosphorus.commands.base import BaseCommand
from phosphorus.commands.build import BuildCommand
from phosphorus.commands.check import CheckCommand
from phosphorus.commands.install import InstallCommand
from phosphorus.commands.lock import LockCommand
from phosphorus.lib.exceptions import UnreachableCodeError

sys.tracebacklimit = 0


def add_build_args(parser: ArgumentParser) -> None:
    parser.add_argument("--metadata", action="store_true")
    parser.add_argument("--no-metadata", action="store_false", dest="metadata")
    parser.add_argument("--no-sdist", action="store_false", dest="sdist")
    parser.add_argument("--sdist", action="store_true")
    parser.add_argument("--no-wheel", action="store_false", dest="wheel")
    parser.add_argument("--wheel", action="store_true")


def add_install_args(parser: ArgumentParser) -> None:
    parser.add_argument("--sync", action="store_true")
    parser.add_argument("--no-sync", action="store_false", dest="sync")
    groups = parser.add_mutually_exclusive_group()
    groups.add_argument("-e", "--exclude", action="append", default=[])
    groups.add_argument("-g", "--groups", action="append", default=[])


def add_lock_args(parser: ArgumentParser) -> None:
    parser.add_argument(
        "--no-enforce-pep440", action="store_false", dest="enforce_pep440"
    )
    parser.add_argument("--enforce-pep440", action="store_true")
    parser.add_argument("--allow-pre-releases", action="store_true")
    parser.add_argument(
        "--no-allow-pre-releases", action="store_false", dest="allow_pre_releases"
    )
    parser.add_argument("--allow-dev-releases", action="store_true")
    parser.add_argument(
        "--no-allow-dev-releases", action="store_false", dest="allow_dev_releases"
    )


def get_parser() -> ArgumentParser:
    parent_parser = ArgumentParser(add_help=False)
    parent_parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase the level of verbosity",
    )

    parser = ArgumentParser(
        prog="phosphorus", description="A dependency management tool"
    )

    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Print the version and exit",
    )

    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True

    build_parser = subparsers.add_parser(
        "build",
        parents=[parent_parser],
        help="Build the wheel and the sdist distributions for the package.",
    )
    add_build_args(build_parser)

    subparsers.add_parser(
        "check", parents=[parent_parser], help="Check that the lock file is up to date."
    )

    install_parser = subparsers.add_parser(
        "install", parents=[parent_parser], help="Install the project dependencies."
    )
    add_install_args(install_parser)

    lock_parser = subparsers.add_parser(
        "lock", parents=[parent_parser], help="Lock the project dependencies"
    )
    add_lock_args(lock_parser)

    return parser


def main() -> None:
    args = get_parser().parse_args()
    if args.verbose:
        if args.verbose > 1:
            print(args)
        sys.tracebacklimit = 9999
    command: BaseCommand
    if args.command == "build":
        command = BuildCommand(args)
    elif args.command == "check":
        command = CheckCommand(args)
    elif args.command == "install":
        command = InstallCommand(args)
    elif args.command == "lock":
        command = LockCommand(args)
    else:
        raise UnreachableCodeError("")
    command()
