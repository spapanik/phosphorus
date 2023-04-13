from argparse import Namespace

from phosphorus.commands.base import BaseCommand


class RunCommand(BaseCommand):
    __slots__ = [*BaseCommand.__slots__, "group", "command"]

    def __init__(self, args: Namespace, /):
        super().__init__(args)
        self.command = args.actual
        self.group = args.group

    def __call__(self) -> None:
        print(self.group)
        print(self.command)
