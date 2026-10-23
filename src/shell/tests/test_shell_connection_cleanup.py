"""The shell closes every bed connection it opens, on the loop that opened it, with no warning.

Each path (token reconnect, password login, the message client, and the message command) is run
against a fake connection that records its close. A failing call still closes.
"""

import asyncio
import gc
import warnings
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from shell import lib


class FakeConn:
    def __init__(self, fail=False):
        self.fail = fail
        self.closes = 0
        self.close_loop = None
        self.open_loop = None
        self._ws = object()

    async def __aenter__(self):
        self.open_loop = asyncio.get_running_loop()
        return self

    async def __aexit__(self, *exc):
        await self.aclose()
        return False

    async def aclose(self):
        self.closes += 1
        self.close_loop = asyncio.get_running_loop()
        self._ws = None

    async def send(self, msg):
        if self.fail:
            raise ConnectionError("bed went away")
        return {"ok": True, "moniker": "alice", "message_id": 3, "is_sysop": False}


def _args():
    return SimpleNamespace(debug=False, token_file="/tmp/none.token", bed_host="127.0.0.1",
                           bed_port=8765, bed_path="/", bed_call_timeout=5.0, bed_probe_timeout=0.25)


def _warnings_during(fn):
    with warnings.catch_warnings(record=True) as rec:
        warnings.simplefilter("always")
        result = fn()
        gc.collect()
    return result, [w for w in rec if issubclass(w.category, ResourceWarning)]


@pytest.mark.unit
@pytest.mark.parametrize("fail", [False, True])
def test_token_reconnect_closes_its_connection(fail):
    fake = FakeConn(fail=fail)
    with patch.object(lib, "get_bed_connection", return_value=fake):
        try:
            lib.reconnect(_args(), "tok")
        except Exception:
            pass
    assert fake.closes == 1


@pytest.mark.unit
def test_token_reconnect_leaves_no_resource_warning():
    fake = FakeConn()
    with patch.object(lib, "get_bed_connection", return_value=fake):
        _, leaks = _warnings_during(lambda: lib.reconnect(_args(), "tok"))
    assert leaks == []


@pytest.mark.unit
def test_close_runs_on_the_loop_that_opened_the_connection():
    fake = FakeConn()
    with patch.object(lib, "get_bed_connection", return_value=fake):
        lib.reconnect(_args(), "tok")
    assert fake.close_loop is fake.open_loop


@pytest.mark.unit
def test_message_command_closes_its_connection():
    fake = FakeConn()
    with patch.object(lib, "get_bed_connection", return_value=fake), \
         patch.object(lib, "resolve_sender", side_effect=lambda p, s, sy, prompt=None: (s, None)), \
         patch.object(lib, "current_session_moniker", return_value="alice"), \
         patch.object(lib, "current_session_is_sysop", return_value=False), \
         patch.object(lib.io, "echo"):
        lib.run_message(_args(), ['message', '--to', 'bob', '--body', 'x'])
    assert fake.closes == 1


@pytest.mark.unit
def test_message_command_closes_when_the_send_fails():
    fake = FakeConn(fail=True)
    with patch.object(lib, "get_bed_connection", return_value=fake), \
         patch.object(lib, "resolve_sender", side_effect=lambda p, s, sy, prompt=None: (s, None)), \
         patch.object(lib, "current_session_moniker", return_value="alice"), \
         patch.object(lib, "current_session_is_sysop", return_value=False), \
         patch.object(lib.io, "echo"):
        lib.run_message(_args(), ['message', '--to', 'bob', '--body', 'x'])
    assert fake.closes == 1


@pytest.mark.unit
def test_password_login_closes_its_connection():
    fake = FakeConn()
    client = MagicMock()
    client.login = AsyncMock(return_value={"ok": True, "moniker": "alice", "token": "t", "is_sysop": False})
    with patch.object(lib, "open_login_connection", return_value=fake), \
         patch.object(lib, "password_login_client", return_value=client), \
         patch.object(lib, "persist_token", return_value=True):
        lib._password_login(_args(), "alice", "pw")
    assert fake.closes == 1


@pytest.mark.unit
def test_password_login_leaves_no_resource_warning():
    fake = FakeConn()
    client = MagicMock()
    client.login = AsyncMock(return_value={"ok": True, "moniker": "alice", "token": "t", "is_sysop": False})
    with patch.object(lib, "open_login_connection", return_value=fake), \
         patch.object(lib, "password_login_client", return_value=client), \
         patch.object(lib, "persist_token", return_value=True):
        _, leaks = _warnings_during(lambda: lib._password_login(_args(), "alice", "pw"))
    assert leaks == []
