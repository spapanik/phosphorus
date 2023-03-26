import pytest

from phosphorus.lib import markers


@pytest.mark.parametrize(
    ("marker_string", "expected"),
    [
        ("", markers.Marker(boolean=None, markers=())),
        (
            "python_version == '3.9'",
            markers.Marker(
                boolean=None,
                markers=(
                    markers.MarkerAtom(
                        variable="python_version", operator="==", value="3.9"
                    ),
                ),
            ),
        ),
        (
            "python_version == '3.9' and os_name == 'linux'",
            markers.Marker(
                boolean="and",
                markers=(
                    markers.MarkerAtom(
                        variable="python_version", operator="==", value="3.9"
                    ),
                    markers.MarkerAtom(
                        variable="os_name", operator="==", value="linux"
                    ),
                ),
            ),
        ),
        (
            "python_version == '3.9' and (os_name == 'linux' or sys_platform == 'linux')",
            markers.Marker(
                boolean="and",
                markers=(
                    markers.MarkerAtom(
                        variable="python_version", operator="==", value="3.9"
                    ),
                    markers.Marker(
                        boolean="or",
                        markers=(
                            markers.MarkerAtom(
                                variable="os_name", operator="==", value="linux"
                            ),
                            markers.MarkerAtom(
                                variable="sys_platform", operator="==", value="linux"
                            ),
                        ),
                    ),
                ),
            ),
        ),
    ],
)
def test_marker_from_string(marker_string: str, expected: markers.Marker) -> None:
    assert markers.Marker.from_string(marker_string) == expected
