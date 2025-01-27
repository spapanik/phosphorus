from unittest import mock

from phosphorus.__main__ import main
from phosphorus.subcommands.build import BuildCommand


@mock.patch(
    "phosphorus.__main__.parse_args",
    new=mock.MagicMock(return_value=mock.MagicMock(subcommand="build")),
)
@mock.patch.object(BuildCommand, "run", new_callable=mock.MagicMock())
def test_main_run(mock_runner: mock.MagicMock) -> None:
    main()
    assert mock_runner.call_count == 1
    calls = [mock.call()]
    assert mock_runner.call_args_list == calls
