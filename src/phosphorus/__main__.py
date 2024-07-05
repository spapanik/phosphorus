from phosphorus.lib.parser import parse_args
from phosphorus.subcommands.build import BuildCommand
from phosphorus.subcommands.check import CheckCommand
from phosphorus.subcommands.install import InstallCommand
from phosphorus.subcommands.lock import LockCommand


def main() -> None:
    args = parse_args()
    if args.subcommand == "build":  # TODO (py3.9): Use match
        BuildCommand(args).run()
    elif args.subcommand == "check":
        CheckCommand(args).run()
    elif args.subcommand == "install":
        InstallCommand(args).run()
    elif args.subcommand == "lock":
        LockCommand(args).run()
