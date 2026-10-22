"""After a password login the shell prints a welcome line with the last login and the balance.

The line names the moniker, the last login (from bed's reply), and the balance with the
source that produced it. It never contains the password or the token.
"""

from unittest.mock import MagicMock, patch

import pytest

from shell import lib


def _echoed(fn, *a):
    with patch.object(lib.io, "echo") as echo:
        fn(*a)
    return " ".join(str(c.args[0]) for c in echo.call_args_list if c.args)


def _args():
    a = MagicMock()
    a.debug = False
    a.bed_host = "127.0.0.1"
    a.bed_port = 8765
    a.token_file = "/tmp/none.token"
    return a


@pytest.mark.unit
def test_welcome_line_has_moniker_last_login_and_bank_balance():
    out = _echoed(lib._welcome, "jam", "2026-10-22T14:52:26+00:00", {"balance": 100, "source": "bed"})
    assert "welcome back jam!" in out
    assert "last login: 2026-10-22T14:52:26+00:00" in out
    assert "bank balance: 100" in out


@pytest.mark.unit
def test_welcome_line_labels_credits_when_that_is_the_source():
    out = _echoed(lib._welcome, "alice", None, {"balance": 40, "source": "credits"})
    assert "credits: 40" in out
    assert "bank balance" not in out


@pytest.mark.unit
def test_first_login_reports_no_previous_login():
    out = _echoed(lib._welcome, "bob", None, {"balance": 100, "source": "bank"})
    assert "last login: never" in out or "first login" in out


@pytest.mark.unit
def test_welcome_never_prints_password_or_token():
    out = _echoed(lib._welcome, "jam", "2026-10-22T14:52:26+00:00", {"balance": 1, "source": "bed"})
    assert "password" not in out.lower()
    assert "token" not in out.lower()


@pytest.mark.unit
def test_password_login_prints_welcome_after_success():
    args = _args()
    with patch.object(lib, "probe_bed", return_value=True), \
         patch.object(lib, "prompt_credentials", return_value=("jam", "pw")), \
         patch.object(lib, "_password_login", return_value="jam") as pl, \
         patch.object(lib, "_last_login_for", return_value="2026-10-22T14:52:26+00:00"), \
         patch.object(lib.member, "getbalance_info", return_value={"balance": 100, "source": "bed"}), \
         patch.object(lib, "_welcome") as welcome:
        assert lib.shell_login(args) == "jam"
    welcome.assert_called_once()
    assert welcome.call_args.args[0] == "jam"


@pytest.mark.unit
def test_refused_password_prints_no_welcome():
    args = _args()
    with patch.object(lib, "probe_bed", return_value=True), \
         patch.object(lib, "prompt_credentials", side_effect=[("jam", "bad"), EOFError()]), \
         patch.object(lib, "_password_login", return_value=None), \
         patch.object(lib, "_welcome") as welcome:
        assert lib.shell_login(args) is None
    welcome.assert_not_called()
