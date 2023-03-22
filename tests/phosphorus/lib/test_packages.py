import pytest

from phosphorus.lib import packages


@pytest.mark.parametrize(
    "name",
    [
        "friendly-bard",
        "Friendly-Bard",
        "FRIENDLY-BARD",
        "friendly.bard",
        "friendly_bard",
        "friendly--bard",
        "FrIeNdLy-._.-bArD",
    ],
)
def test_canonical_names(name: str) -> None:
    assert packages.Package(name).name == "friendly-bard"
    assert packages.Package(name).distribution_name == "friendly_bard"
