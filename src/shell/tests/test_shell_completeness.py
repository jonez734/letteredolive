"""Shell completeness: hidden-but-listed commands, one registry, logout exits."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from shell import lib

SHELL = Path(__file__).resolve().parents[1]


@pytest.mark.unit
def test_missing_command_is_listed_in_registry_but_hidden_from_completion():
    with patch.object(lib.module, "check", side_effect=lambda args, name, **kw: name != "empyre"):
        assert "empyre" in lib.commands
        assert "empyre" not in lib.visible_commands(MagicMock())


@pytest.mark.unit
def test_completer_and_help_share_the_visibility_check():
    with patch.object(lib.module, "check", side_effect=lambda args, name, **kw: name != "empyre"):
        completions = []
        i = 0
        while True:
            c = lib.shellCommandCompleter.complete("", i)
            if c is None:
                break
            completions.append(c)
            i += 1
        assert set(completions) == set(lib.visible_commands(MagicMock()))
        assert "empyre" not in completions


@pytest.mark.unit
def test_typing_a_missing_command_prints_not_installed():
    with patch.object(lib.module, "check", return_value=False), \
         patch.object(lib.io, "echo") as echo:
        assert lib.dispatch_message("empyre") == "not_installed"
    text = " ".join(str(c.args[0]) for c in echo.call_args_list).lower()
    assert "empyre" in text and "not installed" in text


@pytest.mark.unit
def test_commands_json_is_removed_as_a_second_registry():
    assert not (SHELL / "commands.json").exists()


@pytest.mark.unit
def test_logout_branch_clears_session_and_exits_process():
    import ast
    tree = ast.parse((SHELL / "main.py").read_text())
    branch_calls = []
    for node in ast.walk(tree):
        if isinstance(node, ast.If) and "logout" in ast.unparse(node.test):
            branch_calls = [ast.unparse(n) for n in ast.walk(node) if isinstance(n, ast.Call)]
            assert any("clear_session" in c for c in branch_calls)
            assert any("done = True" in ast.unparse(n) for n in node.body)
            return
    pytest.fail("no logout branch found")
