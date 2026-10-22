"""init_screen runs for real: it sets the scroll region once and no more."""

from unittest.mock import patch

import pytest

from shell import lib


@pytest.fixture(autouse=True)
def reset_flag():
    lib._screen_initialized = False
    yield
    lib._screen_initialized = False


@pytest.mark.unit
def test_init_screen_sets_scroll_region_once():
    with patch.object(lib.io, "echo") as echo, \
         patch("bbsengine6.io.terminal.lines", return_value=40):
        lib.init_screen(None)
        first = echo.call_count
        lib.init_screen(None)
    assert first > 0
    assert echo.call_count == first
    assert any("decstbm" in str(c.args[0]) for c in echo.call_args_list if c.args)
