"""A `message` sent from a logged-in session: the login sets who sends, and the account picks the file.

The existing login tests cover each piece. These check the chain: login with a stored token,
then `message` through the real loop, sends as the logged-in member, and `--account` makes the
shell read that account's token file.
"""

import importlib
import os
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from shell import lib

shell_main = importlib.import_module("shell.main")


@pytest.fixture
def runtime(tmp_path, monkeypatch):
    d = tmp_path / "run"
    d.mkdir(mode=0o700)
    monkeypatch.setenv("XDG_RUNTIME_DIR", str(d))
    lib._threadlocal.__dict__.clear()
    yield d
    lib.clear_session()
    lib._threadlocal.__dict__.clear()


def _token(path, text):
    path.write_text(text)
    os.chmod(path, 0o600)


def _login_then_message(args, reconnect_reply, lines):
    """Log in from the stored token, then run the loop. Returns the bed client and the echoes."""
    client = MagicMock()
    client.send_message = AsyncMock(return_value={"ok": True, "message_id": 9})
    script = iter(lines)
    echoed = []
    with patch.object(lib, "probe_bed", return_value=True), \
         patch.object(lib, "reconnect", return_value=reconnect_reply), \
         patch.object(lib, "_show_welcome"), \
         patch.object(lib, "_message_client", return_value=client), \
         patch.object(shell_main.io, "inputstring", side_effect=lambda *a, **k: next(script)), \
         patch.object(lib, "init_screen"), patch.object(lib, "setbottombar"), \
         patch.object(shell_main.io, "echo", side_effect=lambda m, *a, **k: echoed.append((m, k.get("level")))):
        logged_in = lib.shell_login(args)
        assert logged_in is not None, "login must succeed from the stored token"
        shell_main.main(args)
    return client, echoed


@pytest.mark.unit
def test_member_message_sends_as_the_logged_in_member(runtime):
    tok = runtime / "bed-alice.token"
    _token(tok, "tok-alice")
    args = SimpleNamespace(debug=False, token_file=None, account="alice", login=False,
                           bed_host="127.0.0.1", bed_port=8765, bed_probe_timeout=0.25)
    lib.resolve_token_file(args)
    client, echoed = _login_then_message(
        args, {"ok": True, "moniker": "alice", "is_sysop": False},
        ['message --to bob --body "x test"', "exit"])
    assert any("sent #9 to bob" in m for m, _ in echoed)
    kwargs = client.send_message.await_args.kwargs
    assert kwargs["recipients"] == ["bob"]
    assert kwargs["content"] == "x test"
    assert kwargs["sender"] in (None, "alice")


@pytest.mark.unit
def test_account_flag_reads_only_that_accounts_token_file(runtime):
    _token(runtime / "bed-alice.token", "tok-alice")
    _token(runtime / "bed-bob.token", "tok-bob")
    args = SimpleNamespace(debug=False, token_file=None, account="bob", login=False,
                           bed_host="127.0.0.1", bed_port=8765, bed_probe_timeout=0.25)
    lib.resolve_token_file(args)
    with patch.object(lib, "reconnect", return_value={"ok": True, "moniker": "bob", "is_sysop": False}) as rc, \
         patch.object(lib, "probe_bed", return_value=True), patch.object(lib, "_show_welcome"):
        lib.shell_login(args)
    assert rc.call_args.args[1] == "tok-bob", "the bob shell must present bob's token"


@pytest.mark.unit
def test_sysop_session_is_prompted_for_a_sender(runtime):
    _token(runtime / "bed-ops.token", "tok-ops")
    args = SimpleNamespace(debug=False, token_file=None, account="ops", login=False,
                           bed_host="127.0.0.1", bed_port=8765, bed_probe_timeout=0.25)
    lib.resolve_token_file(args)
    with patch.object(lib, "probe_bed", return_value=True), \
         patch.object(lib, "reconnect", return_value={"ok": True, "moniker": "ops", "is_sysop": True}), \
         patch.object(lib, "_show_welcome"):
        lib.shell_login(args)
    assert lib.current_session_is_sysop() is True
    assert lib.current_session_moniker() == "ops"
