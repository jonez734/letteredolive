from typing import Any

from bbsengine6 import io, screen, database

from . import lib


def init(args: Any, **kwargs: Any) -> bool:
    screen.init()
    return True


def access(args: Any, op: str, **kwargs: Any) -> bool:
    return True


def buildargs(args: Any = None, **kw: Any) -> Any:
    parser = __import__("argparse").ArgumentParser("letteredolive")
    parser.add_argument("--debug", default=False)
    database.buildargs(parser)
    return parser


if __name__ == "__main__":
    parser = buildargs()
    args = parser.parse_args()

    init(args)

    try:
        with database.getpool(args) as pool:
            lib.runmodule(args, "main", pool=pool)
    except KeyboardInterrupt:
        io.echo("{/all}*INTR*")
    except EOFError:
        io.echo("{/all}*EOF*")
    finally:
        io.echo(
            f"{{savecursor}}{{curpos:{io.terminal.height()},0}}{{el}}{{reset}}{{restorecursor}}"
        )
