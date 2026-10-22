"""The bottom bar shows the current moniker and the balance from member.getbalance."""

from unittest.mock import MagicMock, patch

import pytest

from shell import lib


def _fragment(args):
    registered = []
    with patch.object(lib._bottombar, "register_bottombar_fragment", side_effect=lambda f: registered.append(f) or f), \
         patch.object(lib._bottombar, "setbottombar", return_value=True):
        lib.setbottombar(args, "falcon")
    return registered[-1]


@pytest.mark.unit
def test_bar_shows_moniker_and_balance_from_getbalance():
    args = MagicMock(debug=False)
    with patch.object(lib.member, "getcurrentmoniker", return_value="jam"), \
         patch.object(lib.member, "getbalance", return_value=250) as gb:
        text = _fragment(args)(args=args)
    assert text == "| jam | 250 credits"
    assert gb.call_args.args[1] == "jam"


@pytest.mark.unit
def test_bar_is_empty_when_no_member():
    args = MagicMock(debug=False)
    with patch.object(lib.member, "getcurrentmoniker", return_value=None):
        assert _fragment(args)(args=args) == ""


@pytest.mark.unit
def test_bar_uses_one_credit_for_1():
    args = MagicMock(debug=False)
    with patch.object(lib.member, "getcurrentmoniker", return_value="jam"), \
         patch.object(lib.member, "getbalance", return_value=1):
        assert _fragment(args)(args=args) == "| jam | 1 credit"


@pytest.mark.unit
def test_set_session_does_not_set_a_member_id():
    from bbsengine6.member import _threadlocal
    _threadlocal.id = None
    lib._set_session("jam", MagicMock(debug=False))
    assert getattr(_threadlocal, "id", None) is None
