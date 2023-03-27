import json
from argparse import Namespace
from datetime import UTC, datetime
from tomllib import TOMLDecodeError
from typing import Any, TextIO

from phosphorus.__version__ import __version__
from phosphorus.commands.base import BaseCommand


class LockCommand(BaseCommand):
    __slots__ = [
        "enforce_pep440",
        "allow_pre_releases",
        "allow_dev_releases",
        "timestamp",
    ]

    def __init__(self, args: Namespace, /):
        super().__init__(args)
        self.enforce_pep440 = args.enforce_pep440
        self.allow_pre_releases = args.allow_pre_releases
        self.allow_dev_releases = args.allow_dev_releases
        self.timestamp = datetime.now(tz=UTC).timestamp()

    def __call__(self) -> None:
        try:
            p_hash = self.get_current_hash() and "!!TODO!!"
        except (FileNotFoundError, KeyError, TOMLDecodeError):
            p_hash = None
        if p_hash == self.meta.p_hash:
            return

        dependencies = self.resolve_dependencies()
        self.write_lockfile(dependencies)

    def resolve_dependencies(self) -> dict[str, dict[str, Any]]:
        # TODO: Remove rex, calculate dependencies from pyproject.toml
        base_dependencies = []
        versions = {}
        for group in self.meta.requirement_groups:
            for requirement in group.requirements:
                versions[requirement] = requirement.package.get_versions(
                    enforce_pep440=self.enforce_pep440,
                    allow_pre_releases=self.allow_pre_releases,
                    allow_dev_releases=self.allow_dev_releases,
                    clauses=requirement.clauses,
                    last_check=self.timestamp,
                )
                base_dependencies.append(requirement)

        return rex

    def write_lockfile(self, dependencies: dict[str, dict[str, Any]]) -> None:
        with self.meta.lockfile.open("w") as lockfile:
            lockfile.write("[phosphorus.meta]\n")
            lockfile.write(f'version = "{__version__}"\n')
            lockfile.write(f'hash = "{self.meta.p_hash}"\n')
            for dependency in sorted(dependencies):
                self.write_dependency_to_lockfile(
                    dependency, dependencies[dependency], lockfile
                )

    @staticmethod
    def write_dependency_to_lockfile(
        dependency: str, dependency_info: dict[str, Any], lockfile: TextIO
    ) -> None:
        lockfile.write(f'\n[packages."{dependency}"]\n')
        lockfile.write(f'version = "{dependency_info["version"]}"\n')
        lockfile.write(f'groups = {dependency_info["groups"]}\n')
        if dependency_info.get("marker"):
            marker = json.dumps(
                dependency_info["marker"], separators=(", ", " = "), sort_keys=True
            )
            lockfile.write(f"marker = {marker}\n")
        lockfile.write("files = [\n")
        for file in dependency_info["files"]:
            lockfile.write(
                f'    {{file = "{file["file"]}", hash = "{file["hash"]}"}},\n'
            )
        lockfile.write("]\n")


# TODO: Remove rex, calculate dependencies from pyproject.toml
rex: dict[str, dict[str, Any]] = {
    "alabaster": {
        "version": "0.7.13",
        "groups": ["main"],
        "files": [
            {
                "file": "alabaster-0.7.13-py3-none-any.whl",
                "hash": "sha256:1ee19aca801bbabb5ba3f5f258e4422dfa86f82f3e9cefb0859b283cdd7f62a3",
            },
            {
                "file": "alabaster-0.7.13.tar.gz",
                "hash": "sha256:a27a4a084d5e690e16e01e03ad2b2e552c61a65469419b907243193de1a84ae2",
            },
        ],
        "marker": {
            "markers": [
                {"variable": "python_version", "operator": ">=", "value": "3.11.0"},
                {
                    "markers": [
                        {"variable": "os_name", "operator": "==", "value": "unix"},
                        {
                            "variable": "sys_platform",
                            "operator": "==",
                            "value": "linux",
                        },
                    ],
                    "boolean": "or",
                },
            ],
            "boolean": "and",
        },
    },
    "decorator": {
        "version": "5.1.1",
        "groups": ["dev", "test"],
        "files": [
            {
                "file": "decorator-5.1.1-py3-none-any.whl",
                "hash": "sha256:b8c3f85900b9dc423225913c5aace94729fe1fa9763b38939a95226f02d37186",
            },
            {
                "file": "decorator-5.1.1.tar.gz",
                "hash": "sha256:637996211036b6385ef91435e4fae22989472f9d571faba8927ba8253acbc330",
            },
        ],
    },
}
