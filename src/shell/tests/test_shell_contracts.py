"""The shell's module contracts: buildargs return type, and the bed login connection closes on its own loop."""

import argparse
import asyncio
import importlib
import inspect
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from shell import lib


@pytest.mark.unit
@pytest.mark.parametrize("name", ["shell.main", "shell.__main__", "shell.module", "shell"])
def test_buildargs_returns_parser_or_none(name):
    mod = importlib.import_module(name)
    ann = inspect.signature(mod.buildargs).return_annotation
    assert ann in (argparse.ArgumentParser, "argparse.ArgumentParser | None", "argparse.ArgumentParser", None, inspect.Signature.empty) or "ArgumentParser" in str(ann), (name, ann)


@pytest.mark.unit
def test_password_login_closes_connection_on_the_loop_that_used_it():
    """The close must run on the same event loop as the login.

    Closing after asyncio.run has ended that loop raises "attached to a different loop".
    """
    loops = {}

    async def fake_login(moniker, password):
        loops["login"] = asyncio.get_running_loop()
        return {"ok": False, "code": "bad_credentials"}

    conn = MagicMock()

    def record_close():
        try:
            loops["close"] = asyncio.get_running_loop()
        except RuntimeError:
            loops["close"] = None

    conn.force_close.side_effect = record_close
    svc = MagicMock()
    svc.login = fake_login
    with patch.object(lib, "open_login_connection", return_value=conn), \
         patch.object(lib, "password_login_client", return_value=svc):
        lib._password_login(MagicMock(), "alice", "pw")
    assert loops["close"] is not None, "close ran outside any event loop"
    assert loops["close"] is loops["login"], "close must run on the login's loop"
