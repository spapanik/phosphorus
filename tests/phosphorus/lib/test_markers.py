import pytest

from phosphorus.lib import markers
from phosphorus.lib.constants import BooleanOperator, ComparisonOperator, MarkerVariable


@pytest.mark.parametrize(
    ("marker_string", "expected"),
    [
        ("", markers.Marker(boolean=None, markers=())),
        (
            'python_version == "3.9"',
            markers.Marker(
                boolean=None,
                markers=(
                    markers.MarkerAtom(
                        variable=MarkerVariable.PYTHON_VERSION,
                        operator=ComparisonOperator.EQUAL_TO,
                        value="3.9",
                    ),
                ),
            ),
        ),
        (
            "(sys_platform != 'cygwin') and extra == 'testing'",
            markers.Marker(
                boolean=BooleanOperator.AND,
                markers=(
                    markers.MarkerAtom(
                        variable=MarkerVariable.SYS_PLATFORM,
                        operator=ComparisonOperator.NOT_EQUAL,
                        value="cygwin",
                    ),
                    markers.MarkerAtom(
                        variable=MarkerVariable.EXTRA,
                        operator=ComparisonOperator.EQUAL_TO,
                        value="testing",
                    ),
                ),
            ),
        ),
        (
            "python_version == '3.12' and os_name == 'posix' or sys_platform == 'linux'",
            markers.Marker(
                boolean=BooleanOperator.OR,
                markers=(
                    markers.Marker(
                        boolean=BooleanOperator.AND,
                        markers=(
                            markers.MarkerAtom(
                                variable=MarkerVariable.PYTHON_VERSION,
                                operator=ComparisonOperator.EQUAL_TO,
                                value="3.12",
                            ),
                            markers.MarkerAtom(
                                variable=MarkerVariable.OS_NAME,
                                operator=ComparisonOperator.EQUAL_TO,
                                value="posix",
                            ),
                        ),
                    ),
                    markers.MarkerAtom(
                        variable=MarkerVariable.SYS_PLATFORM,
                        operator=ComparisonOperator.EQUAL_TO,
                        value="linux",
                    ),
                ),
            ),
        ),
    ],
)
def test_marker_from_string(marker_string: str, expected: markers.Marker) -> None:
    assert markers.Marker.from_string(marker_string) == expected
