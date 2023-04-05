import sys
from argparse import ArgumentParser

from phosphorus.__version__ import __version__
from phosphorus.commands.base import BaseCommand
from phosphorus.commands.build import BuildCommand
from phosphorus.lib.exceptions import UnreachableCodeError

sys.tracebacklimit = 0


def add_build_args(parser: ArgumentParser) -> None:
    parser.add_argument("--metadata", action="store_true")
    parser.add_argument("--no-metadata", action="store_false", dest="metadata")
    parser.add_argument("--no-sdist", action="store_false", dest="sdist")
    parser.add_argument("--sdist", action="store_true")
    parser.add_argument("--no-wheel", action="store_false", dest="wheel")
    parser.add_argument("--wheel", action="store_true")


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
    else:
        raise UnreachableCodeError("")
    command()
