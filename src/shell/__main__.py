from typing import Any

from bbsengine6 import io, screen, database

from . import lib


def init(args: Any, **kwargs: Any) -> bool:
    screen.init()
    return True


def access(args: Any, op: str, **kwargs: Any) -> bool:
    return True


def buildargs(args: Any, **kw: Any) -> Any:
    parser = __import__("argparse").ArgumentParser("letteredolive")
    parser.add_argument("--debug", default=False)
    parser.add_argument("--bed-host", default="127.0.0.1", help="bed daemon host")
    parser.add_argument("--bed-port", type=int, default=8765, help="bed daemon port")
    parser.add_argument("--token-file", default=None, help="bed token file (default: XDG_RUNTIME_DIR)")
    database.buildargs(parser)
    return parser


def main() -> None:
    parser = buildargs(None)
    args = parser.parse_args()

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
