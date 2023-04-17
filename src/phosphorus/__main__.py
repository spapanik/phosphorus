from phosphorus.lib.parser import parse_args
from phosphorus.subcommands.build import BuildCommand
from phosphorus.subcommands.check import CheckCommand
from phosphorus.subcommands.install import InstallCommand
from phosphorus.subcommands.lock import LockCommand


def main() -> None:
    args = parse_args()
    match args.subcommand:
        case "build":
            BuildCommand(args).run()
        case "check":
            CheckCommand(args).run()
        case "install":
            InstallCommand(args).run()
        case "lock":
            LockCommand(args).run()
