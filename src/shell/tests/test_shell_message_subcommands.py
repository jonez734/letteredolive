"""The shell's `message` takes subcommands: send, list, show.

`message send --to bob --body "..."` sends. `message list` shows the pending messages. `message
show <id>` shows one message. Plain `message --to ...` (no subcommand) still sends, for existing use.
"""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from shell import lib


def _args():
    return SimpleNamespace(debug=False, token_file="/tmp/none.token", bed_host="127.0.0.1",
                           bed_port=8765, bed_probe_timeout=0.25)


def _client(list_reply=None, send_reply=None):
    c = MagicMock()
    c.list_pending = AsyncMock(return_value=list_reply or {"ok": True, "messages": []})
    c.send_message = AsyncMock(return_value=send_reply or {"ok": True, "message_id": 9})
    return c


def _run(argv, client):
    with patch.object(lib, "_message_client", return_value=client), \
         patch.object(lib, "current_session_moniker", return_value="bob"), \
         patch.object(lib, "current_session_is_sysop", return_value=False), \
         patch.object(lib, "resolve_sender", side_effect=lambda p, s, sy, prompt=None: (s, None)), \
         patch.object(lib.io, "echo") as echo:
        ok = lib.run_message(_args(), argv)
    text = [str(c.args[0]) for c in echo.call_args_list if c.args]
    return ok, text


@pytest.mark.unit
def test_send_subcommand_sends():
    client = _client()
    ok, _ = _run(["message", "send", "--to", "alice", "--body", "hi"], client)
    assert ok is True
    client.send_message.assert_awaited_once()


@pytest.mark.unit
def test_bare_to_form_still_sends():
    client = _client()
    ok, _ = _run(["message", "--to", "alice", "--body", "hi"], client)
    assert ok is True
    client.send_message.assert_awaited_once()


@pytest.mark.unit
def test_list_subcommand_shows_pending_and_sends_nothing():
    client = _client(list_reply={"ok": True, "messages": [
        {"id": 281, "sender_moniker": "alice", "urgency": "ROUTINE", "content": "hi"}]})
    ok, text = _run(["message", "list"], client)
    assert ok is True
    assert any("281" in t and "alice" in t for t in text)
    client.send_message.assert_not_called()


@pytest.mark.unit
def test_list_subcommand_says_when_empty():
    ok, text = _run(["message", "list"], _client())
    assert ok is True
    assert any("no pending" in t for t in text)


@pytest.mark.unit
def test_show_subcommand_needs_an_id():
    ok, text = _run(["message", "show"], _client())
    assert ok is False
    assert any("id" in t for t in text)


@pytest.mark.unit
def test_unknown_subcommand_is_refused_and_sends_nothing():
    client = _client()
    ok, _ = _run(["message", "bogus", "--to", "alice", "--body", "x"], client)
    assert ok is False
    client.send_message.assert_not_called()
