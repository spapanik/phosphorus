import sys
from argparse import ArgumentParser, Namespace

from phosphorus.__version__ import __version__

sys.tracebacklimit = 0


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

    parser.add_subparsers(dest="subcommand", required=True)

    args = parser.parse_args()
    if args.verbosity > 0:
        sys.tracebacklimit = 1000

    return args
