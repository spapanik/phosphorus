from typing import Literal, Optional

Match = Optional[str]
VersionOperator = Literal["<", "<=", "!=", "==", ">=", ">", "~=", "==="]
MarkerOperator = Literal[VersionOperator, "in", "not in"]
MarkerBoolean = Literal["and", "or"]
MarkerVariable = Literal[
    "os_name",
    "sys_platform",
    "platform_release",
    "implementation_name",
    "platform_machine",
    "platform_python_implementation",
    "python_version",
    "python_full_version",
    "platform_version",
    "implementation_version",
]
