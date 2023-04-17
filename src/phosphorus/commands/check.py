from phosphorus._seven import TOMLDecodeError
from phosphorus.commands.base import BaseCommand


class CheckCommand(BaseCommand):
    __slots__ = BaseCommand.__slots__

    def __call__(self) -> None:
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
