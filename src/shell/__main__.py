import argparse
import sys
import os
from typing import Any

import psycopg

from bbsengine6 import io, database

from . import lib

#: The database the shell connects to when neither --databasename nor BBSENGINE6_DBNAME
#: is given. Without it, bbsengine6 falls back to the NEEDINFO sentinel.
SHELL_DATABASE_DEFAULT = "zoid6"

#: Exit status when the database refuses the connection (distinct from LOGIN_EXIT_CODE).
DB_UNAVAILABLE_EXIT_CODE = 2


def _check_database(dsn: str) -> None:
    """Open and close one direct connection. Raises psycopg.Error if the server refuses it.

    The pool retries failed connections in worker threads and logs each attempt, so a refused
    connection (for example, no PostgreSQL role for the OS user) would flood the terminal.
    One direct attempt fails once, with one message.
    """
    conn = psycopg.connect(dsn, connect_timeout=5)
    conn.close()


def init(args: Any, **kwargs: Any) -> bool:
    lib.init_screen(args)
    return True


def access(args: Any, op: str, **kwargs: Any) -> bool:
    return True


def prog_name() -> str:
    """The command name this process was started as: letteredolive, shell, or bbs."""
    name = lib.process_argv0().lstrip("-").rsplit("/", 1)[-1]
    return name or "letteredolive"


def buildargs(args: Any, **kw: Any) -> argparse.ArgumentParser | None:
    parser = __import__("argparse").ArgumentParser(prog_name())
    parser.add_argument("--debug", default=False)
    parser.add_argument("--bed-host", default="127.0.0.1", help="bed daemon host")
    parser.add_argument("--bed-port", type=int, default=8765, help="bed daemon port")
    parser.add_argument("--token-file", default=None, help="bed token file (default: XDG_RUNTIME_DIR)")
    parser.add_argument(
        "--account",
        default=None,
        help="login account: uses bed-<NAME>.token so terminals can hold different logins",
    )
    parser.add_argument(
        "--login",
        action="store_true",
        default=False,
        help="prompt for moniker and password even if a stored token is valid; saves the new token",
    )
    # An explicit BBSENGINE6_DBNAME wins over the shell default, as it does for bbsengine6.
    database_default = os.environ.get("BBSENGINE6_DBNAME") or SHELL_DATABASE_DEFAULT
    database.buildargs(parser, defaults={"databasename": database_default})
    return parser


def main() -> None:
    parser = buildargs(None)
    args = parser.parse_args()
    lib.resolve_token_file(args)
    # A login shell is started with a leading dash on argv[0]; the idle message depends on it.
    args.login_shell = lib.is_login_shell_process()

    # Anonymous sessions are not allowed: bed must be up, and the user must be
    # authenticated (valid token or password) before the command loop starts.
    # This runs before the try block, so a refusal exits without the terminal
    # cleanup below (which needs a real terminal).
    if lib.shell_login(args) is None:
        raise SystemExit(lib.LOGIN_EXIT_CODE)

    # One direct connection before the pool exists: a refused connection ends here with one message.
    try:
        _check_database(database.make_dsn(args, dbname=args.databasename))
    except psycopg.Error as e:
        io.echo(f"letteredolive: database unavailable: {str(e).strip()}", level="error")
        raise SystemExit(DB_UNAVAILABLE_EXIT_CODE)

    try:
        with database.getpool(args) as pool:
            init(args, pool=pool)
            lib.runmodule(args, "main", pool=pool)
    except KeyboardInterrupt:
        io.echo("{/all}*INTR*")
    except EOFError:
        io.echo("{/all}*EOF*")
    finally:
        io.echo(
            f"{{savecursor}}{{curpos:{io.terminal.height()},0}}{{el}}{{reset}}{{restorecursor}}"
        )


if __name__ == "__main__":
    main()
