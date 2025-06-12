from phosphorus.lib.cli import parse_args
from phosphorus.subcommands.build import BuildCommand


def main() -> None:
    args = parse_args()
    match args.subcommand:
        case "build":  # pragma: no branch
            BuildCommand(args).run()
