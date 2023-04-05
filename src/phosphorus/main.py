import sys
from argparse import ArgumentParser

from phosphorus.__version__ import __version__

sys.tracebacklimit = 0


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

    return parser


def main() -> None:
    args = get_parser().parse_args()
    if args.verbose:
        if args.verbose > 1:
            print(args)
        sys.tracebacklimit = 9999
