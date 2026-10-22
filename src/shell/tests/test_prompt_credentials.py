"""prompt_credentials: a blank moniker asks for the moniker again, not the password."""

from unittest.mock import patch

import pytest

from shell import lib


@pytest.mark.unit
def test_blank_moniker_asks_for_moniker_again_without_asking_password():
    with patch("builtins.input", side_effect=["", "alice"]) as inp, \
         patch.object(lib.getpass, "getpass", side_effect=["pw"]) as gp:
        assert lib.prompt_credentials() == ("alice", "pw")
    assert inp.call_count == 2
    gp.assert_called_once()


@pytest.mark.unit
def test_blank_password_asks_for_password_again_without_asking_moniker():
    with patch("builtins.input", side_effect=["alice"]) as inp, \
         patch.object(lib.getpass, "getpass", side_effect=["", "pw"]) as gp:
        assert lib.prompt_credentials() == ("alice", "pw")
    assert inp.call_count == 1
    assert gp.call_count == 2
