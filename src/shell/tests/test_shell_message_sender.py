"""The shell's message command: the sender is read-only for a member, and a prompt for a sysop.

A member's sender is their own session moniker and cannot be changed. A sysop gets a prompt
with their own moniker as the default: an empty answer keeps it, and a typed moniker is used
as the sender. A member who names another sender is refused and nothing is sent.
"""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from shell import lib


def _args():
    return SimpleNamespace(token_file="/tmp/none.token", debug=False, bed_host="127.0.0.1", bed_port=8765)


def _client():
    c = MagicMock()
    c.send_message = AsyncMock(return_value={"ok": True, "message_id": 3})
    return c


@pytest.fixture
def member(monkeypatch):
    monkeypatch.setattr(lib, "current_session_moniker", lambda: "alice", raising=False)
    monkeypatch.setattr(lib, "current_session_is_sysop", lambda: False, raising=False)


@pytest.fixture
def sysop(monkeypatch):
    monkeypatch.setattr(lib, "current_session_moniker", lambda: "ops", raising=False)
    monkeypatch.setattr(lib, "current_session_is_sysop", lambda: True, raising=False)


@pytest.mark.unit
def test_member_sender_is_the_session_member_and_not_prompted(member):
    client = _client()
    with patch.object(lib, "_message_client", return_value=client), \
         patch.object(lib.io, "inputstring") as prompt, patch.object(lib.io, "echo"):
        ok = lib.run_message(_args(), ["message", "--to", "bob", "--body", "hi"])
    assert ok is True
    prompt.assert_not_called()
    assert client.send_message.await_args.kwargs.get("sender") in (None, "alice")


@pytest.mark.unit
def test_member_naming_another_sender_is_refused_and_nothing_is_sent(member):
    client = _client()
    with patch.object(lib, "_message_client", return_value=client), patch.object(lib.io, "echo") as echo:
        ok = lib.run_message(_args(), ["message", "--to", "bob", "--body", "hi", "--sender", "carol"])
    assert ok is False
    client.send_message.assert_not_called()


@pytest.mark.unit
def test_sysop_is_prompted_with_their_own_moniker_as_default(sysop):
    client = _client()
    with patch.object(lib, "_message_client", return_value=client), \
         patch.object(lib.io, "inputstring", return_value="ops") as prompt, patch.object(lib.io, "echo"):
        lib.run_message(_args(), ["message", "--to", "bob", "--body", "hi"])
    prompt.assert_called_once()
    assert prompt.call_args.args[1] == "ops"


@pytest.mark.unit
def test_sysop_empty_answer_keeps_their_own_sender(sysop):
    client = _client()
    with patch.object(lib, "_message_client", return_value=client), \
         patch.object(lib.io, "inputstring", return_value="ops"), patch.object(lib.io, "echo"):
        lib.run_message(_args(), ["message", "--to", "bob", "--body", "hi"])
    assert client.send_message.await_args.kwargs.get("sender") in (None, "ops")


@pytest.mark.unit
def test_sysop_typed_sender_is_used(sysop):
    client = _client()
    with patch.object(lib, "_message_client", return_value=client), \
         patch.object(lib.io, "inputstring", return_value="alice"), patch.object(lib.io, "echo"):
        lib.run_message(_args(), ["message", "--to", "bob", "--body", "hi"])
    assert client.send_message.await_args.kwargs["sender"] == "alice"


@pytest.mark.unit
def test_send_message_client_accepts_a_sender():
    import inspect
    from bed.client.messageservice import BedMessageServiceClient

    assert "sender" in inspect.signature(BedMessageServiceClient.send_message).parameters
