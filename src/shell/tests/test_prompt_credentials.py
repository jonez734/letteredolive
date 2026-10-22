"""prompt_credentials: a blank field asks again for that field only."""

from unittest.mock import patch

import pytest

from shell import lib


@pytest.mark.unit
def test_blank_moniker_asks_for_moniker_again_without_asking_password():
    with patch.object(lib.io, "inputstring", side_effect=["", "alice"]) as inp, \
         patch.object(lib.util, "inputpassword", side_effect=["pw"]) as pw:
        assert lib.prompt_credentials() == ("alice", "pw")
    assert inp.call_count == 2
    pw.assert_called_once()


@pytest.mark.unit
def test_blank_password_asks_for_password_again_without_asking_moniker():
    with patch.object(lib.io, "inputstring", side_effect=["alice"]) as inp, \
         patch.object(lib.util, "inputpassword", side_effect=["", "pw"]) as pw:
        assert lib.prompt_credentials() == ("alice", "pw")
    assert inp.call_count == 1
    assert pw.call_count == 2
