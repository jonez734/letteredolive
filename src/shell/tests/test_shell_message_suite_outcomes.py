"""What the shell prints and does after a `message` command, through the real loop.

The bed client is faked at the message-client boundary. Each outcome prints one line, and the
loop keeps running for the next command.
"""

import importlib
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from shell import lib

shell_main = importlib.import_module("shell.main")


def _args():
    return SimpleNamespace(debug=False, token_file="/tmp/none.token", bed_host="127.0.0.1",
                           bed_port=8765, bed_probe_timeout=0.25)


def _loop(lines, reply=None, raises=None):
    """Run the real loop with ``lines``; the bed client answers with ``reply``."""
    client = MagicMock()
    if raises is not None:
        client.send_message = AsyncMock(side_effect=raises)
    else:
        client.send_message = AsyncMock(return_value=reply)
    script = iter(lines)
    echoed = []

    with patch.object(shell_main.io, "inputstring", side_effect=lambda *a, **k: next(script)), \
         patch.object(lib, "init_screen"), patch.object(lib, "setbottombar"), \
         patch.object(lib, "_message_client", return_value=client), \
         patch.object(lib, "resolve_sender", side_effect=lambda p, s, sy, prompt=None: (s, None)), \
         patch.object(lib, "current_session_moniker", return_value="alice"), \
         patch.object(lib, "current_session_is_sysop", return_value=False), \
         patch.object(shell_main.io, "echo", side_effect=lambda m, *a, **k: echoed.append((m, k.get("level")))):
        shell_main.main(_args())
    return client, echoed


@pytest.mark.unit
def test_successful_send_prints_the_message_id():
    client, echoed = _loop(['message --to bob --body "x test"', "exit"],
                           reply={"ok": True, "message_id": 281})
    assert any("sent #281 to bob" in m for m, _ in echoed)
    client.send_message.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.parametrize("code", ["forbidden", "missing_recipients", "missing_content", "not_sent"])
def test_bed_refusal_prints_one_error_line(code):
    client, echoed = _loop(['message --to bob --body "x"', "exit"],
                           reply={"ok": False, "code": code, "message": "no"})
    errors = [m for m, lvl in echoed if lvl == "error" and "message not sent" in m]
    assert len(errors) == 1
    assert code in errors[0]


@pytest.mark.unit
def test_bed_unavailable_prints_an_error_and_the_loop_continues():
    client, echoed = _loop(['message --to bob --body "x"', "exit"],
                           reply={"ok": False, "code": "bed_unavailable", "message": "down"})
    assert any("logout" in m for m, _ in echoed), "loop must reach exit after a failed send"


@pytest.mark.unit
def test_a_failed_send_does_not_stop_the_next_command():
    client, echoed = _loop(['message --to bob --body "x"', 'message --to bob --body "y"', "exit"],
                           reply={"ok": True, "message_id": 2})
    assert client.send_message.await_count == 2


@pytest.mark.unit
def test_usage_error_is_printed_and_nothing_is_sent():
    client, echoed = _loop(['message --body "x"', "exit"], reply={"ok": True, "message_id": 1})
    client.send_message.assert_not_called()
    assert any("--to" in m for m, lvl in echoed if lvl == "error")


@pytest.mark.unit
def test_unmatched_quote_is_reported_and_nothing_is_sent():
    client, echoed = _loop(['message --to bob --body "oops', "exit"], reply={"ok": True, "message_id": 1})
    client.send_message.assert_not_called()
    assert any("unmatched quote" in m for m, _ in echoed)
