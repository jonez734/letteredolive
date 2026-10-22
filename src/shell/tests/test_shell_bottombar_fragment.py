"""The bottom-bar fragment must accept the keyword args bottombar.render passes."""

from unittest.mock import MagicMock, patch

import pytest

from shell import lib


@pytest.mark.unit
def test_right_fragment_accepts_args_keyword_from_render():
    registered = []
    with patch.object(lib._bottombar, "register_bottombar_fragment", side_effect=lambda f: registered.append(f) or f), \
         patch.object(lib._bottombar, "setbottombar", return_value=True), \
         patch.object(lib.member, "getcurrent", return_value={"moniker": "jam", "credits": 3}):
        args = MagicMock(debug=False)
        lib.setbottombar(args, "falcon")
        fragment = registered[-1]
        # bottombar.render calls every fragment as item(**merged), with args as a keyword.
        assert fragment(args=args) == "| jam | 3 credits"
