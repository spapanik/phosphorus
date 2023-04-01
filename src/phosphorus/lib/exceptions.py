class UnreachableCodeError(AssertionError):
    """This is an aid for static analyzers"""


class PipError(RuntimeError):
    """Pip exited unsuccessfully"""
