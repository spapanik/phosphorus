from phosphorus.lib.parser import parse_args
from phosphorus.subcommands.build import BuildCommand


def main() -> None:
    args = parse_args()
    match args.subcommand:
        case "build":
            BuildCommand(args).run()
