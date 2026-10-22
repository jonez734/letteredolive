"""The shell resolves the bed token path once, at startup, and every later bed call uses it."""

import argparse
import inspect
from unittest.mock import MagicMock, patch

import pytest

from shell import __main__ as entry
from shell import lib


@pytest.mark.unit
def test_main_sets_token_file_before_login():
    src = inspect.getsource(entry.main)
    assert "lib.resolve_token_file(args)" in src
    assert src.index("lib.resolve_token_file(args)") < src.index("shell_login(args)")


@pytest.mark.unit
def test_resolved_path_is_the_flag_value_when_given(tmp_path):
    p = tmp_path / "given.token"
    args = argparse.Namespace(token_file=str(p))
    lib.resolve_token_file(args)
    assert args.token_file == str(p)


@pytest.mark.unit
def test_resolved_path_defaults_to_the_xdg_location(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_RUNTIME_DIR", str(tmp_path))
    args = argparse.Namespace(token_file=None)
    lib.resolve_token_file(args)
    assert args.token_file == str(tmp_path / "bed.token")


@pytest.mark.unit
def test_balance_lookup_from_the_shell_sends_the_token(tmp_path):
    tok = tmp_path / "bed.token"
    tok.write_text("tok-abc")
    tok.chmod(0o600)
    args = argparse.Namespace(token_file=str(tok), token=None, debug=False)
    from bbsengine6.member import lib as member_lib
    from bed.tools import _token
    with patch.object(_token, "read_token_file", return_value="tok-abc") as rt:
        assert member_lib._resolve_bed_token(args) == "tok-abc"
    rt.assert_called_once()
