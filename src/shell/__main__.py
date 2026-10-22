import argparse
import os
from typing import Any

from bbsengine6 import io, database

from . import lib

#: The database the shell connects to when neither --databasename nor BBSENGINE6_DBNAME
#: is given. Without it, bbsengine6 falls back to the NEEDINFO sentinel.
SHELL_DATABASE_DEFAULT = "zoid6"


def init(args: Any, **kwargs: Any) -> bool:
    lib.init_screen(args)
    return True


def access(args: Any, op: str, **kwargs: Any) -> bool:
    return True


def buildargs(args: Any, **kw: Any) -> argparse.ArgumentParser | None:
    parser = __import__("argparse").ArgumentParser("letteredolive")
    parser.add_argument("--debug", default=False)
    parser.add_argument("--bed-host", default="127.0.0.1", help="bed daemon host")
    parser.add_argument("--bed-port", type=int, default=8765, help="bed daemon port")
    parser.add_argument("--token-file", default=None, help="bed token file (default: XDG_RUNTIME_DIR)")
    # An explicit BBSENGINE6_DBNAME wins over the shell default, as it does for bbsengine6.
    database_default = os.environ.get("BBSENGINE6_DBNAME") or SHELL_DATABASE_DEFAULT
    database.buildargs(parser, defaults={"databasename": database_default})
    return parser


def main() -> None:
    parser = buildargs(None)
    args = parser.parse_args()
    lib.resolve_token_file(args)

    # Anonymous sessions are not allowed: bed must be up, and the user must be
    # authenticated (valid token or password) before the command loop starts.
    # This runs before the try block, so a refusal exits without the terminal
    # cleanup below (which needs a real terminal).
    if lib.shell_login(args) is None:
        raise SystemExit(lib.LOGIN_EXIT_CODE)

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
