import argparse
from typing import Any, Optional

from bbsengine6 import util, io, database

from . import lib


def init(args: Optional[Any] = None, **kw: Any) -> bool:
    #    ttyio.setvariable("empyre.highlightcolor", "{bggray}{white}")
    #    ttyio.echo("empyre.boot.init", level="debug")
    return True


def buildargs(args: Optional[Any], **kw: Any) -> argparse.ArgumentParser | None:
    parser: Any = __import__("argparse").ArgumentParser("shell")
    parser.add_argument("--verbose", action="store_true", dest="verbose")
    parser.add_argument("--debug", action="store_true", dest="debug")

    defaults = {
        "databasename": "zoid6",
        "databasehost": "localhost",
        "databaseuser": None,
        "databaseport": 5432,
        "databasepassword": None,
    }
    database.buildargdatabasegroup(parser, defaults)

    return parser


def main(args: Any, **kw: Any) -> None:
    if args is not None and "debug" in args and args.debug is True:
        io.echo(f"shell.main.100: {args=}", level="debug")

    util.heading("lettered olive")

    if args.debug is True:
        io.echo(
            f"{{var:labelcolor}}database: {{var:valuecolor}}{args.databasename} {{var:labelcolor}}host: {{var:valuecolor}}{args.databasehost}{{var:labelcolor}}:{{var:valuecolor}}{args.databaseport}",
            level="debug",
            end="",
        )
        if args.databasepassword is not None:
            io.echo("{var:labelcolor}password: {var:valuecolor}Yes")
        else:
            io.echo("{var:labelcolor}password: {var:valuecolor}No")

    lib.setbottombar(args, "letteredolive")

    if lib.checkmodule(args, "main") is False:
        io.echo("error running submodule 'main'", level="error")
    return
