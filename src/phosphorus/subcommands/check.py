import sys

from phosphorus._seven import TOMLDecodeError
from phosphorus.subcommands.base import BaseCommand


class CheckCommand(BaseCommand):
    __slots__ = ()

    def run(self) -> None:
        try:
            self.check()
        except RuntimeError as exc:
            print(f"❌ Lockfile check failed: {exc}", file=sys.stderr)
            sys.exit(1)
        else:
            print("✅ Success: Lockfile is valid and up-to-date with pyproject.toml")

    def check(self) -> None:
        try:
            p_hash = self.get_current_hash()
        except FileNotFoundError as exc:
            msg = "No lockfile found"
            raise RuntimeError(msg) from exc
        except (KeyError, TOMLDecodeError) as exc:
            msg = "Lockfile is invalid"
            raise RuntimeError(msg) from exc

        if p_hash != self.meta.p_hash:
            msg = "Hashes don't match"
            raise RuntimeError(msg)
