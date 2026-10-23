"""The shell records whether the session belongs to a sysop, from bed's login or reconnect reply.

The message command reads this flag to decide between a read-only sender and a prompt.
"""

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from shell import lib


@pytest.fixture(autouse=True)
def _clean_session():
    lib.clear_session()
    yield
    lib.clear_session()


@pytest.mark.unit
def test_session_is_not_sysop_by_default():
    assert lib.current_session_is_sysop() is False


@pytest.mark.unit
def test_record_sysop_flag_sets_the_session():
    lib._set_session("ops", None, is_sysop=True)
    assert lib.current_session_moniker() == "ops"
    assert lib.current_session_is_sysop() is True


@pytest.mark.unit
def test_record_member_flag_clears_sysop():
    lib._set_session("ops", None, is_sysop=True)
    lib._set_session("alice", None, is_sysop=False)
    assert lib.current_session_is_sysop() is False


@pytest.mark.unit
def test_reconnect_reply_sets_the_sysop_flag(tmp_path):
    tok = tmp_path / "bed.token"
    tok.write_text("tok-ops")
    os.chmod(tok, 0o600)
    args = MagicMock(token_file=str(tok), debug=False)
    with patch.object(lib, "reconnect", return_value={"ok": True, "moniker": "ops", "is_sysop": True}):
        assert lib._try_token(args, str(tok)) == "ops"
    assert lib.current_session_is_sysop() is True


@pytest.mark.unit
def test_reconnect_reply_for_a_member_is_not_sysop(tmp_path):
    tok = tmp_path / "bed.token"
    tok.write_text("tok-alice")
    os.chmod(tok, 0o600)
    args = MagicMock(token_file=str(tok), debug=False)
    with patch.object(lib, "reconnect", return_value={"ok": True, "moniker": "alice", "is_sysop": False}):
        lib._try_token(args, str(tok))
    assert lib.current_session_is_sysop() is False


@pytest.mark.unit
def test_password_login_reply_sets_the_sysop_flag():
    reply = {"ok": True, "moniker": "ops", "token": "tok", "is_sysop": True}
    client = MagicMock()
    client.login = AsyncMock(return_value=reply)
    args = MagicMock(token_file=None, debug=False)
    with patch.object(lib, "open_login_connection", return_value=MagicMock(_ws=None)), \
         patch.object(lib, "password_login_client", return_value=client), \
         patch.object(lib, "persist_token", return_value=True):
        assert lib._password_login(args, "ops", "pw") == "ops"
    assert lib.current_session_is_sysop() is True
