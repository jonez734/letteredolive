"""A database that refuses the connection ends the shell with one message, not a retry flood.

bbsengine6's ConnectionPool retries in worker threads and logs every failed attempt, so a missing
PostgreSQL role (e.g. the OS user has no role) produced a screen of repeated errors. The shell
checks one connection up front and exits cleanly when it fails.
"""

from unittest.mock import MagicMock, patch

import psycopg
import pytest

from shell import __main__ as shell_main
from shell import lib


class _Refused(psycopg.OperationalError):
    pass


def _args():
    args = MagicMock()
    args.databasename = "zoid6"
    return args


@pytest.mark.unit
def test_db_failure_exits_with_one_message_and_no_pool(monkeypatch):
    monkeypatch.setattr(lib, "shell_login", lambda args: object())
    messages = []

    def refuse(dsn):
        raise _Refused('FATAL:  role "lo_test" does not exist')

    with patch.object(shell_main.database, "buildargs"), \
         patch.object(shell_main.database, "make_dsn", return_value="dbname=zoid6"), \
         patch.object(shell_main.database, "getpool") as gp, \
         patch.object(shell_main, "_check_database", side_effect=refuse), \
         patch.object(shell_main.io, "echo", side_effect=lambda msg, **k: messages.append(msg)), \
         patch.object(shell_main, "buildargs") as b, \
         patch("sys.argv", ["shell"]):
        b.return_value.parse_args.return_value = _args()
        with pytest.raises(SystemExit) as exc:
            shell_main.main()

    assert exc.value.code == shell_main.DB_UNAVAILABLE_EXIT_CODE
    gp.assert_not_called()
    text = "\n".join(messages)
    assert 'role "lo_test" does not exist' in text, messages
    assert text.count("FATAL") == 1, messages


@pytest.mark.unit
def test_db_check_uses_a_single_direct_connection(monkeypatch):
    seen = {}

    class _Conn:
        def close(self):
            seen["closed"] = True

    def fake_connect(dsn, **kwargs):
        seen["dsn"] = dsn
        seen["kwargs"] = kwargs
        return _Conn()

    monkeypatch.setattr(shell_main.psycopg, "connect", fake_connect)
    shell_main._check_database("dbname=zoid6")
    assert seen["dsn"] == "dbname=zoid6"
    assert seen["kwargs"].get("connect_timeout") == 5
    assert seen.get("closed")


@pytest.mark.unit
def test_healthy_database_still_starts_the_pool(monkeypatch):
    monkeypatch.setattr(lib, "shell_login", lambda args: object())
    started = []

    class _Pool:
        def __enter__(self):
            started.append("enter")
            return self

        def __exit__(self, *a):
            return False

    with patch.object(shell_main, "buildargs") as b, \
         patch.object(shell_main.database, "make_dsn", return_value="dbname=zoid6"), \
         patch.object(shell_main, "_check_database"), \
         patch.object(shell_main.database, "getpool", return_value=_Pool()), \
         patch.object(shell_main, "init", lambda *a, **k: None), \
         patch.object(shell_main.lib, "runmodule", lambda *a, **k: None), \
         patch.object(shell_main.io, "echo"), \
         patch("sys.argv", ["shell"]):
        b.return_value.parse_args.return_value = _args()
        shell_main.main()
    assert started == ["enter"]
