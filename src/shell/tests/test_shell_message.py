"""``message`` is a shell command that sends through the bed daemon with the session token.

Usage: ``message --to bob [--to carol] --body "text" [--urgency ROUTINE]``.
The shell does not load the bbsengine6 message module (a no-op); it calls bed directly.
"""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from shell import lib


def _args(token_file="/run/user/1000/bed.token", debug=False):
    return SimpleNamespace(token_file=token_file, debug=debug, bed_host="127.0.0.1", bed_port=8765)


@pytest.mark.unit
def test_message_is_a_registry_command_with_a_handler():
    assert "message" in lib.commands
    assert lib.commands["message"].get("handler") is not None
    assert lib.commands["message"].get("disabled") is not True


@pytest.mark.unit
def test_message_dispatch_runs_without_the_module_loader():
    with patch.object(lib.module, "check", return_value=False), patch.object(lib.io, "echo"):
        assert lib.dispatch_message("message") == "run"


@pytest.mark.unit
def test_parse_collects_repeated_to_and_body():
    parsed = lib.parse_message_args(["message", "--to", "bob", "--to", "carol", "--body", "hi there"])
    assert parsed["recipients"] == ["bob", "carol"]
    assert parsed["body"] == "hi there"
    assert parsed["urgency"] == "ROUTINE"


@pytest.mark.unit
def test_parse_accepts_comma_separated_recipients():
    parsed = lib.parse_message_args(["message", "--to", "bob,carol", "--body", "x"])
    assert parsed["recipients"] == ["bob", "carol"]


@pytest.mark.unit
def test_parse_rejects_missing_to():
    with pytest.raises(ValueError, match="--to"):
        lib.parse_message_args(["message", "--body", "x"])


@pytest.mark.unit
def test_parse_rejects_missing_body():
    with pytest.raises(ValueError, match="--body"):
        lib.parse_message_args(["message", "--to", "bob"])


@pytest.mark.unit
def test_message_command_sends_through_bed_with_the_session_token():
    client = MagicMock()
    client.send_message = AsyncMock(return_value={"ok": True, "message_id": 11})
    with patch.object(lib, "_message_client", return_value=client), \
         patch.object(lib, "_read_token", return_value="tok-alice"), \
         patch.object(lib.io, "echo") as echo:
        ok = lib.run_message(_args(), ["message", "--to", "bob", "--body", "hello"])
    assert ok is True
    kwargs = client.send_message.await_args.kwargs
    assert kwargs["recipients"] == ["bob"]
    assert kwargs["content"] == "hello"
    assert kwargs["urgency"] == "ROUTINE"


@pytest.mark.unit
def test_message_command_reports_usage_on_bad_arguments():
    with patch.object(lib.io, "echo") as echo:
        ok = lib.run_message(_args(), ["message", "--body", "x"])
    assert ok is False
    assert any("--to" in str(c.args[0]) for c in echo.call_args_list if c.args)


@pytest.mark.unit
def test_message_command_reports_a_refusal():
    client = MagicMock()
    client.send_message = AsyncMock(return_value={"ok": False, "code": "forbidden", "message": "no"})
    with patch.object(lib, "_message_client", return_value=client), \
         patch.object(lib, "_read_token", return_value="tok-alice"), \
         patch.object(lib.io, "echo") as echo:
        ok = lib.run_message(_args(), ["message", "--to", "bob", "--body", "hi"])
    assert ok is False
    assert any("forbidden" in str(c.args[0]) for c in echo.call_args_list if c.args)
