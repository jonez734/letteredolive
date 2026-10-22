"""A password login goes through bed's login and saves the token, as casino does.

The shell no longer checks the password itself with member.checkpassword.
Bed's login checks it server-side, mints a token, and the token is persisted
with bed.tools.auth._persist_token.
"""

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from shell import lib


@pytest.fixture
def args(tmp_path):
    a = MagicMock()
    a.debug = False
    a.bed_host = "127.0.0.1"
    a.bed_port = 8765
    a.bed_probe_timeout = 0.25
    a.token_file = str(tmp_path / "bed.token")
    return a


def _ok_reply(moniker="alice"):
    return {"ok": True, "moniker": moniker, "token": "tok-fresh",
            "session_id": "s" * 16, "expires_at": "2099-01-01T00:00:00Z",
            "is_sysop": False, "balance": 0}


@pytest.mark.unit
def test_password_login_uses_bed_login_not_checkpassword(args):
    svc = MagicMock()
    svc.login = AsyncMock(return_value=_ok_reply())
    with patch.object(lib, "probe_bed", return_value=True), \
         patch.object(lib, "prompt_credentials", return_value=("alice", "pw")), \
         patch.object(lib, "password_login_client", return_value=svc), \
         patch.object(lib, "persist_token", return_value=True), \
         patch.object(lib, "member") as m:
        assert lib.shell_login(args) == "alice"
    svc.login.assert_awaited_once_with("alice", "pw")
    m.checkpassword.assert_not_called()


@pytest.mark.unit
def test_successful_password_login_persists_token(args):
    svc = MagicMock()
    svc.login = AsyncMock(return_value=_ok_reply())
    with patch.object(lib, "probe_bed", return_value=True), \
         patch.object(lib, "prompt_credentials", return_value=("alice", "pw")), \
         patch.object(lib, "password_login_client", return_value=svc), \
         patch.object(lib, "persist_token", return_value=True) as persist:
        lib.shell_login(args)
    persist.assert_called_once()
    assert persist.call_args.args[0]["token"] == "tok-fresh"


@pytest.mark.unit
def test_refused_password_saves_nothing(args, tmp_path):
    svc = MagicMock()
    svc.login = AsyncMock(return_value={"ok": False, "code": "bad_credentials"})
    with patch.object(lib, "probe_bed", return_value=True), \
         patch.object(lib, "prompt_credentials", side_effect=[("alice", "wrong"), EOFError()]), \
         patch.object(lib, "password_login_client", return_value=svc), \
         patch.object(lib, "persist_token") as persist:
        assert lib.shell_login(args) is None
    persist.assert_not_called()


@pytest.mark.unit
def test_malformed_reply_without_token_saves_nothing(args):
    svc = MagicMock()
    svc.login = AsyncMock(return_value={"ok": True, "moniker": "alice"})
    with patch.object(lib, "probe_bed", return_value=True), \
         patch.object(lib, "prompt_credentials", return_value=("alice", "pw")), \
         patch.object(lib, "password_login_client", return_value=svc), \
         patch.object(lib, "persist_token") as persist:
        assert lib.shell_login(args) is None
    persist.assert_not_called()


@pytest.mark.unit
def test_token_and_password_not_printed(args, capsys):
    svc = MagicMock()
    svc.login = AsyncMock(return_value=_ok_reply())
    with patch.object(lib, "probe_bed", return_value=True), \
         patch.object(lib, "prompt_credentials", return_value=("alice", "pw-SECRET")), \
         patch.object(lib, "password_login_client", return_value=svc), \
         patch.object(lib, "persist_token", return_value=True):
        lib.shell_login(args)
    out = capsys.readouterr()
    assert "pw-SECRET" not in out.out + out.err
    assert "tok-fresh" not in out.out + out.err


@pytest.mark.unit
def test_login_connection_is_closed(args):
    svc = MagicMock()
    svc.login = AsyncMock(return_value=_ok_reply())
    conn = MagicMock()
    ws = MagicMock()
    ws.close = AsyncMock()
    conn._ws = ws
    with patch.object(lib, "probe_bed", return_value=True), \
         patch.object(lib, "prompt_credentials", return_value=("alice", "pw")), \
         patch.object(lib, "password_login_client", return_value=svc), \
         patch.object(lib, "persist_token", return_value=True), \
         patch.object(lib, "open_login_connection", return_value=conn):
        lib.shell_login(args)
    ws.close.assert_awaited_once()
    assert conn._ws is None
