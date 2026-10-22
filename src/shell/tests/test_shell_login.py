"""shell_login: the shell needs bed, then a valid token, then a password.

Bed unreachable -> exit 1, no prompt. A valid token -> no prompt. Otherwise a
password, checked with member.checkpassword. Nothing sensitive is printed.
"""

import io
import os
import stat
from contextlib import redirect_stdout
from unittest.mock import MagicMock, patch

import pytest

from shell import lib


@pytest.fixture
def args(tmp_path):
    a = MagicMock()
    a.debug = False
    a.bed_host = "127.0.0.1"
    a.bed_port = 8765
    a.bed_probe_timeout = 0.25
    a.token_file = None
    return a


def _reply(ok=True, moniker="alice"):
    return {"ok": ok, "moniker": moniker, "token": "tok-new", "session_id": "s" * 16,
            "expires_at": "2099-01-01T00:00:00Z", "is_sysop": False}


def _bed_login_ok(moniker="alice"):
    """Patch bed's password login to succeed, and stop the token being written."""
    from unittest.mock import AsyncMock
    svc = MagicMock()
    svc.login = AsyncMock(return_value={"ok": True, "moniker": moniker, "token": "tok-fresh",
                                        "session_id": "s" * 16, "expires_at": "2099-01-01T00:00:00Z",
                                        "is_sysop": False, "balance": 0})
    return svc


def _refused():
    from unittest.mock import AsyncMock
    svc = MagicMock()
    svc.login = AsyncMock(return_value={"ok": False, "code": "bad_credentials"})
    return svc


@pytest.mark.unit
def test_bed_unreachable_exits_1_without_prompting(args, capsys):
    with patch.object(lib, "probe_bed", return_value=False), \
         patch.object(lib, "getpass") as gp:
        assert lib.shell_login(args) is None
    gp.assert_not_called()
    assert lib.LOGIN_EXIT_CODE == 1
    assert "bed is not reachable" in capsys.readouterr().err


@pytest.mark.unit
def test_valid_token_logs_in_without_password(args, tmp_path):
    tok = tmp_path / "bed.token"
    tok.write_text("tok-valid")
    os.chmod(tok, 0o600)
    args.token_file = str(tok)
    with patch.object(lib, "probe_bed", return_value=True), \
         patch.object(lib, "reconnect", return_value=_reply()), \
         patch.object(lib, "getpass") as gp:
        assert lib.shell_login(args) == "alice"
    gp.assert_not_called()


@pytest.mark.unit
def test_rejected_token_falls_back_to_password(args, tmp_path):
    tok = tmp_path / "bed.token"
    tok.write_text("tok-stale")
    os.chmod(tok, 0o600)
    args.token_file = str(tok)
    with patch.object(lib, "probe_bed", return_value=True), \
         patch.object(lib, "reconnect", return_value={"ok": False, "code": "token_expired"}), \
         patch.object(lib, "prompt_credentials", return_value=("alice", "pw")), \
         patch.object(lib, "password_login_client", return_value=_bed_login_ok("alice")), \
         patch.object(lib, "persist_token", return_value=True):
        assert lib.shell_login(args) == "alice"


@pytest.mark.unit
def test_missing_token_file_prompts_for_password(args, tmp_path):
    args.token_file = str(tmp_path / "absent.token")
    with patch.object(lib, "probe_bed", return_value=True), \
         patch.object(lib, "prompt_credentials", return_value=("bob", "pw")), \
         patch.object(lib, "password_login_client", return_value=_bed_login_ok("bob")), \
         patch.object(lib, "persist_token", return_value=True):
        assert lib.shell_login(args) == "bob"


@pytest.mark.unit
def test_refused_password_returns_none(args, tmp_path):
    args.token_file = str(tmp_path / "absent.token")
    with patch.object(lib, "probe_bed", return_value=True), \
         patch.object(lib, "prompt_credentials", return_value=("bob", "wrong")), \
         patch.object(lib, "password_login_client", return_value=_refused()):
        assert lib.shell_login(args) is None


@pytest.mark.unit
def test_loose_token_file_permissions_refused(args, tmp_path):
    tok = tmp_path / "bed.token"
    tok.write_text("tok-valid")
    os.chmod(tok, 0o644)
    args.token_file = str(tok)
    with patch.object(lib, "probe_bed", return_value=True), \
         patch.object(lib, "reconnect") as rc, \
         patch.object(lib, "prompt_credentials", return_value=("x", "y")), \
         patch.object(lib, "password_login_client", return_value=_refused()):
        lib.shell_login(args)
    rc.assert_not_called()


@pytest.mark.unit
def test_token_and_password_never_printed(args, tmp_path, capsys):
    tok = tmp_path / "bed.token"
    tok.write_text("tok-SECRET-VALUE")
    os.chmod(tok, 0o600)
    args.token_file = str(tok)
    with patch.object(lib, "probe_bed", return_value=True), \
         patch.object(lib, "reconnect", return_value={"ok": False, "code": "token_expired"}), \
         patch.object(lib, "prompt_credentials", return_value=("alice", "pw-SECRET-VALUE")), \
         patch.object(lib, "password_login_client", return_value=_bed_login_ok("alice")), \
         patch.object(lib, "persist_token", return_value=True):
        lib.shell_login(args)
    out = capsys.readouterr()
    assert "tok-SECRET-VALUE" not in out.out + out.err
    assert "pw-SECRET-VALUE" not in out.out + out.err


@pytest.mark.unit
def test_xdg_runtime_dir_is_honoured(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_RUNTIME_DIR", str(tmp_path))
    assert lib.default_token_file().startswith(str(tmp_path))


@pytest.mark.unit
def test_tmp_fallback_when_xdg_unset(monkeypatch):
    monkeypatch.delenv("XDG_RUNTIME_DIR", raising=False)
    assert lib.default_token_file().endswith(os.path.join(f"bed-{os.getuid()}", "bed.token"))


@pytest.mark.unit
def test_logout_clears_session_moniker():
    from bbsengine6.member import _threadlocal
    _threadlocal.moniker = "alice"
    lib.clear_session()
    assert getattr(_threadlocal, "moniker", None) is None


@pytest.mark.unit
def test_logout_command_clears_session_in_main_loop():
    import ast
    from pathlib import Path as _P
    tree = ast.parse(_P("shell/main.py").read_text())
    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.If) and isinstance(node.test, ast.Compare):
            names = [getattr(c, "value", None) for c in node.test.comparators[0].elts] if isinstance(node.test.comparators[0], ast.Tuple) else []
            if "logout" in names:
                calls = [ast.unparse(n) for n in ast.walk(node) if isinstance(n, ast.Call)]
                found = any("clear_session" in c for c in calls)
    assert found, "the logout branch must call lib.clear_session()"
