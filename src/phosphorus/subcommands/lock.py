from __future__ import annotations

from typing import TYPE_CHECKING, TextIO

from phosphorus.__version__ import __version__
from phosphorus._seven import TOMLDecodeError
from phosphorus.lib.resolver import LockEntry, Resolver
from phosphorus.lib.term import SGRParams, SGRString
from phosphorus.subcommands.base import BaseCommand

if TYPE_CHECKING:
    from argparse import Namespace


class LockCommand(BaseCommand):
    __slots__ = (
        "force",
        "enforce_pep440",
        "allow_pre_releases",
        "allow_dev_releases",
        "timestamp",
    )

    def __init__(self, args: Namespace, /) -> None:
        super().__init__(args)
        self.force = args.force
        self.enforce_pep440 = args.enforce_pep440
        self.allow_pre_releases = args.allow_pre_releases
        self.allow_dev_releases = args.allow_dev_releases

    def run(self) -> None:
        if self.force:
            print(
                f"🔄🔒 {SGRString('lock', params=[SGRParams.GREEN])} "
                "was run with --force, rebuilding the lock ..."
            )
            dependencies = self.resolve_dependencies()
            return self.write_lockfile(dependencies)

        try:
            p_hash = self.get_current_hash()
        except (FileNotFoundError, KeyError, TOMLDecodeError):
            p_hash = None

        if p_hash == self.meta.p_hash:
            print("🔒✅ Lockfile is up to date, nothing to do ...")
            return None

        print("🔄 Lockfile is not up to date, rebuilding the lock ...")
        dependencies = self.resolve_dependencies()
        return self.write_lockfile(dependencies)

    def resolve_dependencies(self) -> list[LockEntry]:
        print("🔍 Resolving dependencies ...")
        return Resolver(
            self.meta.requirement_groups,
            enforce_pep440=self.enforce_pep440,
            allow_pre_releases=self.allow_pre_releases,
            allow_dev_releases=self.allow_dev_releases,
        ).resolve()

    def write_lockfile(self, dependencies: list[LockEntry]) -> None:
        print("🔒 Writing new lockfile ...")
        with self.meta.lockfile.open("w") as lockfile:
            lockfile.write('["$meta"]\n')
            lockfile.write(f'version = "{__version__}"\n')
            lockfile.write(f'hash = "{self.meta.p_hash}"\n')
            for dependency in sorted(dependencies):
                self.write_dependency_to_lockfile(dependency, lockfile)

    @staticmethod
    def write_dependency_to_lockfile(entry: LockEntry, lockfile: TextIO) -> None:
        requirement = entry.requirement
        lockfile.write("\n[[packages]]\n")
        lockfile.write(f'name = "{requirement.package}"\n')
        lockfile.write(f'version = "{requirement.version}"\n')
        lockfile.write("groups = [\n")
        for group in entry.groups:
            lockfile.write(f'    "{group}",\n')
        lockfile.write("]\n")
        if marker := str(requirement.marker):
            lockfile.write(f'marker = "{marker}"\n')
        lockfile.write("hashes = [\n")
        for file_hash in entry.hashes:
            lockfile.write(f'    "{file_hash}",\n')
        lockfile.write("]\n")
