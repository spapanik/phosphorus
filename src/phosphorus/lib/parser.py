from __future__ import annotations

import sys
from argparse import ArgumentParser, Namespace

from phosphorus.__version__ import __version__

sys.tracebacklimit = 0


def add_boolean_optional_action(
    parser: ArgumentParser,
    var: str,
    help_text: str = "",
    *,
    required: bool = False,
    default: bool | None = None,
) -> None:  # TODO (py3.8): Use BooleanOptionalAction
    dest = var.replace("-", "_")
    parser.add_argument(
        f"--{var}",
        action="store_true",
        dest=dest,
        default=default,
        help=help_text,
        required=required,
    )
    parser.add_argument(
        f"--no-{var}",
        action="store_false",
        dest=dest,
        default=default,
        help=help_text,
        required=required,
    )


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
    add_boolean_optional_action(
        build_parser,
        "sdist",
        default=True,
        help_text="build the sdist distribution",
    )
    add_boolean_optional_action(
        build_parser,
        "wheel",
        default=True,
        help_text="build the wheel distribution",
    )

    check_parser = subparsers.add_parser(
        "check", parents=[parent_parser], help="check that the lock file is up to date"
    )
    add_boolean_optional_action(
        check_parser,
        "lockfile",
        default=False,
        help_text="check if the lock file is up to date",
    )
    add_boolean_optional_action(
        check_parser,
        "outdated",
        default=False,
        help_text="check if the dependencies are outdated",
    )

    install_parser = subparsers.add_parser(
        "install", parents=[parent_parser], help="install the project dependencies"
    )
    add_boolean_optional_action(
        install_parser,
        "sync",
        default=False,
        help_text="sync the dependencies, by removing the ones that are not in the lock file",
    )
    dependency_groups = install_parser.add_mutually_exclusive_group()
    dependency_groups.add_argument(
        "-e",
        "--exclude",
        action="append",
        default=[],
        help="exclude a group of dependencies",
    )
    dependency_groups.add_argument(
        "-g",
        "--groups",
        action="append",
        default=[],
        help="install a group of dependencies",
    )

    lock_parser = subparsers.add_parser(
        "lock", parents=[parent_parser], help="lock the project dependencies"
    )
    lock_parser.add_argument(
        "-f", "--force", action="store_true", help="force recreating the lock"
    )
    add_boolean_optional_action(
        lock_parser,
        "enforce-pep440",
        default=True,
        help_text="enforce PEP 440",
    )
    add_boolean_optional_action(
        lock_parser,
        "allow-pre-releases",
        default=False,
        help_text="allow pre-releases",
    )
    add_boolean_optional_action(
        lock_parser,
        "allow-dev-releases",
        default=False,
        help_text="allow dev releases",
    )

    args = parser.parse_args()
    if args.verbosity > 0:
        sys.tracebacklimit = 1000

    return args
