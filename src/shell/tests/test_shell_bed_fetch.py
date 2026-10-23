"""The shell supplies bed's bank reply to bbsengine6's balance lookup, and closes its socket.

bbsengine6 no longer imports bed. _bed_fetch is the shell's bed step: it resolves the token,
runs one bank_balance call on a bed connection, and releases the socket on the same loop.
"""

import asyncio
import gc
import warnings
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from shell import lib


class _FakeConn:
    def __init__(self, reply=None, raises=None):
        self.reply = reply
        self.raises = raises
        self.closes = 0
        self.close_loop = None
        self.open_loop = None

    async def __aenter__(self):
        self.open_loop = asyncio.get_running_loop()
        return self

    async def __aexit__(self, *exc):
        self.closes += 1
        self.close_loop = asyncio.get_running_loop()
        return False


def _args():
    return SimpleNamespace(debug=False, token_file="/tmp/none.token", bed_host="127.0.0.1",
                           bed_port=8765, bed_path="/", bed_call_timeout=5.0)


def _call(conn, moniker="alice"):
    async def fake_balance(self, mon, token=""):
        if conn.raises is not None:
            raise conn.raises
        return conn.reply

    with patch.object(lib, "get_bed_connection", return_value=conn), \
         patch("bed.client.bank.BedBankClient.get_balance_result", fake_balance), \
         patch.object(lib, "_read_token", return_value="tok"):
        return lib._bed_fetch(_args(), moniker)


@pytest.mark.unit
def test_bed_fetch_returns_bed_reply():
    conn = _FakeConn(reply={"balance": 250, "account": True, "bed_name": "zoid6"})
    assert _call(conn) == {"balance": 250, "account": True, "bed_name": "zoid6"}


@pytest.mark.unit
def test_bed_fetch_closes_the_connection_after_a_reply():
    conn = _FakeConn(reply={"balance": 1, "account": True})
    _call(conn)
    assert conn.closes == 1


@pytest.mark.unit
def test_bed_fetch_closes_the_connection_when_bed_refuses():
    from bed.client.exceptions import BedUnavailable
    conn = _FakeConn(raises=BedUnavailable("bank_balance: token_invalid: bad"))
    with pytest.raises(BedUnavailable):
        _call(conn)
    assert conn.closes == 1


@pytest.mark.unit
def test_bed_fetch_closes_on_the_loop_that_opened_it():
    conn = _FakeConn(reply={"balance": 1, "account": True})
    _call(conn)
    assert conn.close_loop is conn.open_loop


@pytest.mark.unit
def test_bed_fetch_leaves_no_resource_warning():
    conn = _FakeConn(reply={"balance": 1, "account": True})
    with warnings.catch_warnings(record=True) as rec:
        warnings.simplefilter("always")
        _call(conn)
        gc.collect()
    assert [w for w in rec if issubclass(w.category, ResourceWarning)] == []


@pytest.mark.unit
def test_bottombar_and_welcome_pass_bed_fetch():
    import inspect
    src = inspect.getsource(lib)
    assert "getbalance_info(args, moniker, bed_fetch=_bed_fetch)" in src
    assert "getbalance(render_args, moniker, pool=kwargs.get(\"pool\"), bed_fetch=_bed_fetch)" in src
