"""The shell's entry point runs the login gate before the command loop."""

import inspect
from unittest.mock import MagicMock, patch

import pytest

import shell.__main__ as entry


@pytest.mark.unit
def test_main_runs_login_gate_before_command_loop():
    src = inspect.getsource(entry.main)
    assert "shell_login" in src
    assert src.index("shell_login") < src.index('lib.runmodule(args, "main"')


@pytest.mark.unit
def test_main_exits_1_when_gate_refuses():
    args = MagicMock()
    with patch.object(entry, "buildargs") as b, \
         patch.object(entry.database, "getpool") as gp, \
         patch.object(entry, "init", return_value=True), \
         patch.object(entry.io, "echo"), \
         patch.object(entry.lib, "shell_login", return_value=None), \
         patch.object(entry.lib, "runmodule") as run:
        b.return_value.parse_args.return_value = args
        gp.return_value.__enter__.return_value = MagicMock()
        with pytest.raises(SystemExit) as ex:
            entry.main()
    assert ex.value.code == 1
    run.assert_not_called()


@pytest.mark.unit
def test_main_enters_loop_after_successful_login():
    args = MagicMock()
    with patch.object(entry, "buildargs") as b, \
         patch.object(entry.database, "getpool") as gp, \
         patch.object(entry, "init", return_value=True), \
         patch.object(entry.io, "echo"), \
         patch.object(entry.lib, "shell_login", return_value="alice"), \
         patch.object(entry, "_check_database"), \
         patch.object(entry.lib, "runmodule") as run:
        b.return_value.parse_args.return_value = args
        gp.return_value.__enter__.return_value = MagicMock()
        entry.main()
    run.assert_called_once()
