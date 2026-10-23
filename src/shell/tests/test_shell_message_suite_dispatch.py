"""The shell's main loop dispatches `message` with the typed arguments intact.

These drive the real `main` loop with scripted input. Only the terminal (`io.inputstring`),
the screen setup, and the bed client are replaced, so the loop, the input splitting, and the
dispatch all run as they do in a session.
"""

from types import SimpleNamespace
from unittest.mock import patch

import pytest

from shell import lib
import importlib

shell_main = importlib.import_module("shell.main")


def _args():
    return SimpleNamespace(debug=False, token_file="/tmp/none.token", bed_host="127.0.0.1",
                           bed_port=8765, bed_probe_timeout=0.25)


def _run_loop(lines):
    """Run the real main loop with ``lines`` as the typed input. Returns the run_message calls."""
    script = iter(lines)

    def fake_input(*a, **k):
        return next(script)

    with patch.object(shell_main.io, "inputstring", side_effect=fake_input), \
         patch.object(lib, "init_screen"), \
         patch.object(lib, "setbottombar"), \
         patch.object(lib, "run_message", return_value=True) as rm, \
         patch.object(shell_main.io, "echo"):
        shell_main.main(_args())
    return rm


@pytest.mark.unit
def test_message_with_a_quoted_body_reaches_run_message_as_one_value():
    rm = _run_loop(['message --to bob --body "x test"', "exit"])
    assert rm.call_count == 1
    argv = rm.call_args.args[1]
    assert argv == ["message", "--to", "bob", "--body", "x test"]


@pytest.mark.unit
def test_message_with_an_apostrophe_in_double_quotes_is_one_value():
    rm = _run_loop(["message --to bob --body \"it's fine\"", "exit"])
    argv = rm.call_args.args[1]
    assert argv[argv.index("--body") + 1] == "it's fine"


@pytest.mark.unit
def test_unquoted_message_still_dispatches():
    rm = _run_loop(["message --to bob --body hi", "exit"])
    assert rm.call_args.args[1] == ["message", "--to", "bob", "--body", "hi"]


@pytest.mark.unit
def test_exit_ends_the_loop_without_dispatching_anything():
    rm = _run_loop(["exit"])
    rm.assert_not_called()
