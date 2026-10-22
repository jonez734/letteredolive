"""The shell's welcome line shows the balance source label, and the shell's logger takes the
bed name it is connected to after login."""

import logging
from unittest.mock import patch

import pytest

from shell import lib


def _echoed(fn, *a):
    with patch.object(lib.io, "echo") as echo:
        fn(*a)
    return " ".join(str(c.args[0]) for c in echo.call_args_list if c.args)


@pytest.mark.unit
def test_welcome_shows_the_bed_bank_source_label():
    text = _echoed(lib._welcome, "jam", "2026-10-22T14:52:26+00:00", {"balance": 100, "source": "zoid6 bank"})
    assert "source: zoid6 bank" in text
    assert "100" in text


@pytest.mark.unit
def test_welcome_shows_the_local_and_credits_labels():
    assert "source: bank" in _echoed(lib._welcome, "bob", None, {"balance": 1, "source": "bank"})
    assert "source: credits" in _echoed(lib._welcome, "bob", None, {"balance": 1, "source": "credits"})


@pytest.mark.unit
def test_login_records_the_bed_name_for_the_shell_logger():
    reply = {"ok": True, "moniker": "jam", "token": "t", "last_login": None, "bed_name": "zoid6"}
    with patch.object(lib, "password_login_client") as plc, \
         patch.object(lib, "open_login_connection"), \
         patch.object(lib, "persist_token"):
        import asyncio
        async def fake(moniker, password):
            return reply
        plc.return_value.login = fake
        lib._password_login(None, "jam", "pw")
    assert lib._BED_NAME["value"] == "zoid6"


@pytest.mark.unit
def test_shell_logger_uses_the_bed_name_after_login():
    lib._BED_NAME["value"] = "zoid6"
    assert lib.shell_logger().name == "zoid6"


@pytest.mark.unit
def test_shell_logger_uses_the_shell_name_before_login():
    lib._BED_NAME["value"] = None
    assert lib.shell_logger().name == "shell"
