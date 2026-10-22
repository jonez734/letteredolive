"""Shell login prompts use bbsengine6's input functions, not input() or getpass."""

import inspect
from unittest.mock import patch

import pytest

from shell import lib


@pytest.mark.unit
def test_moniker_uses_io_inputstring_shown_as_typed():
    with patch.object(lib.io, "inputstring", side_effect=["alice"]) as inp, \
         patch.object(lib.util, "inputpassword", side_effect=["pw"]):
        lib.prompt_credentials()
    assert inp.call_args.args[0] == "moniker: "
    assert inp.call_args.kwargs.get("mask") is None


@pytest.mark.unit
def test_password_uses_util_inputpassword_with_default_mask():
    with patch.object(lib.io, "inputstring", side_effect=["alice"]), \
         patch.object(lib.util, "inputpassword", side_effect=["pw"]) as pw:
        lib.prompt_credentials()
    assert pw.call_args.args[0] == "password: "


@pytest.mark.unit
def test_blank_password_reprompts_with_inputpassword():
    with patch.object(lib.io, "inputstring", side_effect=["alice"]), \
         patch.object(lib.util, "inputpassword", side_effect=["", "pw"]) as pw:
        assert lib.prompt_credentials() == ("alice", "pw")
    assert pw.call_count == 2


@pytest.mark.unit
def test_blank_moniker_reprompts_with_inputstring():
    with patch.object(lib.io, "inputstring", side_effect=["", "alice"]) as inp, \
         patch.object(lib.util, "inputpassword", side_effect=["pw"]):
        assert lib.prompt_credentials() == ("alice", "pw")
    assert inp.call_count == 2


@pytest.mark.unit
def test_ctrl_d_at_moniker_propagates_as_eoferror():
    with patch.object(lib.io, "inputstring", side_effect=EOFError):
        with pytest.raises(EOFError):
            lib.prompt_credentials()


@pytest.mark.unit
def test_prompt_credentials_does_not_use_input_or_getpass():
    src = inspect.getsource(lib.prompt_credentials)
    assert "input(" not in src.replace("io.inputstring(", "").replace("util.inputpassword(", "")
    assert "getpass" not in src
