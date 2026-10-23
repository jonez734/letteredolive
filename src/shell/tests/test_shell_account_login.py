"""shell --account NAME and shell --login: choose a login per terminal.

--account NAME reads and writes bed-NAME.token beside the default file, so terminals can hold
different logins. --login skips the stored-token step and prompts for a password, then saves
the new token to the account file. A bare shell keeps the current auto-login.
"""

import argparse
import os
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from shell import __main__ as shell_main
from shell import lib
from bed.tools import _token


@pytest.fixture
def runtime(tmp_path, monkeypatch):
    d = tmp_path / "run"
    d.mkdir(mode=0o700)
    monkeypatch.setenv("XDG_RUNTIME_DIR", str(d))
    return d


def _parse(argv):
    return shell_main.buildargs(None).parse_args(argv)


# --- flags -------------------------------------------------------------------

@pytest.mark.unit
def test_buildargs_accepts_account():
    assert _parse(["--account", "alice"]).account == "alice"


@pytest.mark.unit
def test_buildargs_accepts_login():
    assert _parse(["--login"]).login is True


@pytest.mark.unit
def test_buildargs_defaults_are_auto_login():
    a = _parse([])
    assert a.login is False
    assert a.account is None


# --- token path --------------------------------------------------------------

@pytest.mark.unit
def test_account_selects_the_account_file(runtime):
    a = _parse(["--account", "alice"])
    lib.resolve_token_file(a)
    assert a.token_file == str(runtime / "bed-alice.token")


@pytest.mark.unit
def test_no_account_keeps_the_default_file(runtime):
    a = _parse([])
    lib.resolve_token_file(a)
    assert a.token_file == str(runtime / "bed.token")


@pytest.mark.unit
def test_token_file_flag_beats_account(runtime, tmp_path):
    explicit = str(tmp_path / "mine.token")
    a = _parse(["--account", "alice", "--token-file", explicit])
    lib.resolve_token_file(a)
    assert a.token_file == explicit


@pytest.mark.unit
def test_invalid_account_name_is_refused(runtime):
    with pytest.raises(ValueError):
        lib.resolve_token_file(_parse(["--account", "../bob"]))


@pytest.mark.unit
def test_shell_default_path_is_bed_token_path_for(runtime):
    # The shell and bed must agree on the file name, so they cannot drift apart.
    assert lib.default_token_file() == _token.token_path_for()


@pytest.mark.unit
def test_two_accounts_never_share_a_file(runtime):
    a = _parse(["--account", "alice"])
    b = _parse(["--account", "bob"])
    lib.resolve_token_file(a)
    lib.resolve_token_file(b)
    assert a.token_file != b.token_file


# --- login behaviour ---------------------------------------------------------

@pytest.mark.unit
def test_login_flag_skips_the_stored_token(runtime):
    args = _parse(["--login", "--account", "alice"])
    lib.resolve_token_file(args)
    with patch.object(lib, "probe_bed", return_value=True), \
         patch.object(lib, "_try_token") as try_token, \
         patch.object(lib, "prompt_credentials", return_value=("alice", "pw")), \
         patch.object(lib, "_password_login", return_value="alice"), \
         patch.object(lib, "_show_welcome"), \
         patch.object(lib, "_set_session", return_value="alice"):
        assert lib.shell_login(args) == "alice"
    try_token.assert_not_called()


@pytest.mark.unit
def test_plain_shell_still_tries_the_stored_token(runtime):
    args = _parse([])
    lib.resolve_token_file(args)
    with patch.object(lib, "probe_bed", return_value=True), \
         patch.object(lib, "_try_token", return_value="bob") as try_token, \
         patch.object(lib, "_set_session", return_value="bob"):
        assert lib.shell_login(args) == "bob"
    try_token.assert_called_once()


@pytest.mark.unit
def test_login_saves_the_new_token_to_the_account_file(runtime):
    args = _parse(["--login", "--account", "alice"])
    lib.resolve_token_file(args)
    with patch.object(lib, "probe_bed", return_value=True), \
         patch.object(lib, "prompt_credentials", return_value=("alice", "pw")), \
         patch.object(lib, "_password_login", return_value="alice") as pl, \
         patch.object(lib, "_show_welcome"), \
         patch.object(lib, "_set_session", return_value="alice"):
        lib.shell_login(args)
    assert args.token_file == str(runtime / "bed-alice.token")
    pl.assert_called_once()


@pytest.mark.unit
def test_persist_token_writes_to_the_account_file(runtime):
    args = _parse(["--account", "alice"])
    lib.resolve_token_file(args)
    with patch("bed.tools.auth._persist_token", return_value=True) as persist:
        lib.persist_token({"token": "t"}, args)
    used = persist.call_args.args[1]
    assert used.token_file == str(runtime / "bed-alice.token")


# --- message uses the shell's own token file ---------------------------------

@pytest.mark.unit
def test_message_reads_the_shells_account_file(runtime):
    args = _parse(["--account", "alice"])
    lib.resolve_token_file(args)
    with patch.object(lib, "_read_token", wraps=lib._read_token) as rt, \
         patch.object(lib, "get_bed_connection", return_value=MagicMock()), \
         patch("bed.client.messageservice.BedMessageServiceClient") as cls:
        lib._message_client(args)
    assert cls.call_args.kwargs["token_file"] == str(runtime / "bed-alice.token")
