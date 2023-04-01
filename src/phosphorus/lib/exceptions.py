class UnreachableCodeError(AssertionError):
    """This is an aid for static analysers"""


class MissingProjectRootError(RuntimeError):
    """The project root could not be found"""


class PipError(RuntimeError):
    """Pip exited unsuccessfully"""
