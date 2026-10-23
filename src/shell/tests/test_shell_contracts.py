"""The shell's module contracts: buildargs return type, and the bed login connection closes on its own loop."""

import argparse
import asyncio
import importlib
import inspect
import sys
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

    async def record_ws_close():
        loops["close"] = asyncio.get_running_loop()

    class _Conn:
        _ws = None
        async def __aenter__(self):
            return self
        async def __aexit__(self, *exc):
            await record_ws_close()
            return False
    conn = _Conn()
    svc = MagicMock()
    svc.login = fake_login
    with patch.object(lib, "open_login_connection", return_value=conn), \
         patch.object(lib, "password_login_client", return_value=svc):
        lib._password_login(MagicMock(), "alice", "pw")
    assert loops["close"] is not None, "close ran outside any event loop"
    assert loops["close"] is loops["login"], "close must run on the login's loop"


@pytest.mark.unit
def test_login_connection_is_closed_with_await_not_force_close():
    """Closing the login socket must await the websocket close on the login loop.

    force_close schedules the close on a new loop in a thread, which raises
    "attached to a different loop" when the websocket belongs to the login loop.
    """
    import ast
    import inspect
    tree = ast.parse(inspect.getsource(lib._password_login))
    calls = [ast.unparse(n.func) for n in ast.walk(tree) if isinstance(n, ast.Call)]
    assert not any("force_close" in c for c in calls)
    # The close is owned by run_with_connection, which awaits it on the login's own loop.
    assert any(c.endswith("run_with_connection") for c in calls)


@pytest.mark.unit
def test_main_passes_the_loader_signature_check():
    """shell.main and shell.module must pass bbsengine6's signature check for main."""
    import sys
    from pathlib import Path as _P
    bbs_src = _P(__file__).resolve().parents[4] / "bbsengine6" / "py" / "src"
    if str(bbs_src) not in sys.path:
        sys.path.insert(0, str(bbs_src))
    from bbsengine6 import module as bbs_module
    import shell.main as shell_main_mod
    import shell.module as shell_module_mod
    for mod in (shell_main_mod, shell_module_mod):
        assert bbs_module._check_func_signature(mod.main, bbs_module._stub_main), mod.__name__
