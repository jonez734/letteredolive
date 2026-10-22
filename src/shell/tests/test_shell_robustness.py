"""Login gate robustness: order, blank input, Ctrl-D, network errors, token cleanup."""

import os
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
    a.token_file = str(tmp_path / "bed.token")
    return a


@pytest.mark.unit
def test_bed_is_probed_before_database_is_opened():
    import inspect
    from shell import __main__ as entry
    src = inspect.getsource(entry.main)
    assert src.index("shell_login") < src.index("getpool") or \
        src.index("probe_bed") < src.index("getpool")


@pytest.mark.unit
def test_blank_moniker_reprompts_until_a_value_is_given(args):
    answers = iter([("", ""), ("alice", "pw")])
    with patch.object(lib, "probe_bed", return_value=True), \
         patch.object(lib, "prompt_credentials", side_effect=lambda: next(answers)), \
         patch.object(lib, "member") as m:
        m.checkpassword.return_value = True
        assert lib.shell_login(args) == "alice"


@pytest.mark.unit
def test_blank_password_reprompts(args):
    answers = iter([("alice", ""), ("alice", "pw")])
    with patch.object(lib, "probe_bed", return_value=True), \
         patch.object(lib, "prompt_credentials", side_effect=lambda: next(answers)), \
         patch.object(lib, "member") as m:
        m.checkpassword.return_value = True
        assert lib.shell_login(args) == "alice"


@pytest.mark.unit
def test_ctrl_d_at_login_exits_with_plain_message(args, capsys):
    with patch.object(lib, "probe_bed", return_value=True), \
         patch.object(lib, "prompt_credentials", side_effect=EOFError):
        assert lib.shell_login(args) is None
    err = capsys.readouterr().err
    assert "logged out" in err.lower() or "cancel" in err.lower()
    assert "Traceback" not in err


@pytest.mark.unit
def test_reconnect_network_error_is_treated_as_bed_unreachable(args, tmp_path, capsys):
    tok = tmp_path / "bed.token"
    tok.write_text("tok")
    os.chmod(tok, 0o600)
    args.token_file = str(tok)
    with patch.object(lib, "probe_bed", return_value=True), \
         patch.object(lib, "reconnect", side_effect=ConnectionError("dropped")), \
         patch.object(lib, "prompt_credentials") as pc:
        assert lib.shell_login(args) is None
    pc.assert_not_called()
    assert "bed is not reachable" in capsys.readouterr().err


@pytest.mark.unit
def test_rejected_token_file_is_deleted(args, tmp_path):
    tok = tmp_path / "bed.token"
    tok.write_text("tok-stale")
    os.chmod(tok, 0o600)
    args.token_file = str(tok)
    with patch.object(lib, "probe_bed", return_value=True), \
         patch.object(lib, "reconnect", return_value={"ok": False, "code": "token_expired"}), \
         patch.object(lib, "prompt_credentials", side_effect=[("", ""), EOFError()]):
        lib.shell_login(args)
    assert not tok.exists()


@pytest.mark.unit
def test_oserror_reading_token_is_treated_as_no_token(args, capsys):
    with patch.object(lib, "probe_bed", return_value=True), \
         patch.object(lib._token, "read_token_file", side_effect=OSError("io")), \
         patch.object(lib, "reconnect") as rc, \
         patch.object(lib, "prompt_credentials", side_effect=[("", ""), EOFError()]):
        lib.shell_login(args)
    rc.assert_not_called()


@pytest.mark.unit
def test_bed_host_port_and_token_come_from_namespace(args):
    import inspect
    from shell import __main__ as entry
    src = inspect.getsource(entry.buildargs)
    for flag in ("--bed-host", "--bed-port", "--token-file"):
        assert flag in src
    assert "bed_host" in inspect.getsource(lib._bed_unreachable)
    assert "bed_port" in inspect.getsource(lib._bed_unreachable)
