"""Commands flagged disabled stay in the registry but are hidden and do not run."""

from unittest.mock import patch

import pytest

from shell import lib

DISABLED = ["weather", "banderole", "repo"]


@pytest.mark.unit
@pytest.mark.parametrize("name", DISABLED)
def test_disabled_commands_are_flagged_in_registry(name):
    assert lib.commands[name].get("disabled") is True


@pytest.mark.unit
def test_disabled_commands_hidden_even_when_module_present():
    with patch.object(lib.module, "check", return_value=True):
        visible = lib.visible_commands(None)
    for name in DISABLED:
        assert name not in visible


@pytest.mark.unit
def test_typing_disabled_command_prints_disabled_not_run(capsys):
    with patch.object(lib.module, "check", return_value=True), \
         patch.object(lib.io, "echo") as echo:
        assert lib.dispatch_message("repo") == "disabled"
    text = " ".join(str(c.args[0]) for c in echo.call_args_list).lower()
    assert "repo" in text and "disabled" in text


@pytest.mark.unit
def test_main_loop_does_not_run_a_disabled_command():
    import importlib
    import inspect
    shell_loop = importlib.import_module("shell.main")
    assert '"disabled"' in inspect.getsource(shell_loop.main)
