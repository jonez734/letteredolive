"""A `message` command leaves nothing open: no ResourceWarning, no pending task, no unclosed socket.

Each check runs one `message` outcome through the real loop with a fake bed connection that
records whether it was closed. Garbage collection runs before the warnings are read, because an
unclosed socket is reported only when it is collected. These are the acceptance tests for the
`async with` change: they fail while a connection is left open.
"""

import gc
import importlib
import warnings
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from shell import lib

shell_main = importlib.import_module("shell.main")


class FakeConnection:
    """Stands in for BedConnection: records open/close and whether the close ran on the open loop."""

    def __init__(self, fail=False):
        self.fail = fail
        self.opened = 0
        self.closed = 0
        self.close_loop = None
        self.open_loop = None

    async def __aenter__(self):
        import asyncio
        self.opened += 1
        self.open_loop = asyncio.get_running_loop()
        return self

    async def __aexit__(self, *exc):
        import asyncio
        self.closed += 1
        self.close_loop = asyncio.get_running_loop()
        return False

    async def send(self, msg):
        if self.fail:
            raise ConnectionError("bed went away")
        return {"ok": True, "message_id": 5}


def _args():
    return SimpleNamespace(debug=False, token_file="/tmp/none.token", bed_host="127.0.0.1",
                           bed_port=8765, bed_probe_timeout=0.25)


def _run(lines, fake):
    """Run the real loop with ``lines``. Returns (fake, warnings recorded while collecting)."""
    script = iter(lines)
    with warnings.catch_warnings(record=True) as rec:
        warnings.simplefilter("always")
        with patch.object(shell_main.io, "inputstring", side_effect=lambda *a, **k: next(script)), \
             patch.object(lib, "init_screen"), patch.object(lib, "setbottombar"), \
             patch.object(lib, "get_bed_connection", return_value=fake), \
             patch.object(lib, "resolve_sender", side_effect=lambda p, s, sy, prompt=None: (s, None)), \
             patch.object(lib, "current_session_moniker", return_value="alice"), \
             patch.object(lib, "current_session_is_sysop", return_value=False), \
             patch.object(shell_main.io, "echo"):
            shell_main.main(_args())
        gc.collect()
    return fake, [w for w in rec if issubclass(w.category, ResourceWarning)]


@pytest.mark.unit
def test_successful_message_closes_its_connection_before_the_loop_returns():
    fake, _ = _run(['message --to bob --body "x"', "exit"], FakeConnection())
    assert fake.opened == fake.closed == 1, "every opened connection must be closed"


@pytest.mark.unit
def test_successful_message_leaves_no_resource_warning():
    _, leaks = _run(['message --to bob --body "x"', "exit"], FakeConnection())
    assert leaks == [], [str(w.message) for w in leaks]


@pytest.mark.unit
def test_failed_message_still_closes_its_connection():
    fake, _ = _run(['message --to bob --body "x"', "exit"], FakeConnection(fail=True))
    assert fake.opened == fake.closed == 1


@pytest.mark.unit
def test_failed_message_leaves_no_resource_warning():
    _, leaks = _run(['message --to bob --body "x"', "exit"], FakeConnection(fail=True))
    assert leaks == [], [str(w.message) for w in leaks]


@pytest.mark.unit
def test_close_runs_on_the_loop_that_opened_the_connection():
    fake, _ = _run(['message --to bob --body "x"', "exit"], FakeConnection())
    assert fake.close_loop is fake.open_loop, "close must run on the loop that opened the socket"


@pytest.mark.unit
def test_no_task_is_left_pending_after_a_message():
    import asyncio
    leftover = []

    real_run = asyncio.run

    def run_and_check(coro):
        async def wrapped():
            result = await coro
            leftover.extend(t for t in asyncio.all_tasks() if t is not asyncio.current_task())
            return result
        return real_run(wrapped())

    with patch.object(lib.asyncio, "run", side_effect=run_and_check):
        _run(['message --to bob --body "x"', "exit"], FakeConnection())
    assert leftover == [], f"{len(leftover)} task(s) left pending"
