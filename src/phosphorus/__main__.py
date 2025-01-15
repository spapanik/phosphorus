from phosphorus.lib.cli import parse_args
from phosphorus.subcommands.build import BuildCommand


def main() -> None:
    args = parse_args()
    if args.subcommand == "build":  # upgrade: py3.9: Use match
        BuildCommand(args).run()
