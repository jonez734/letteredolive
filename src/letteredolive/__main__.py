import argparse
from bbsengine6 import io, screen, database

from . import lib

#from . import module

def init(args, **kwargs) -> bool:
    screen.init()

    return True

def access(args, op:str, **kwargs) -> bool:
    return True

def buildargs(args=None, **kw):
    parser = argparse.ArgumentParser("letteredolive")
    parser.add_argument("--debug", default=False)
    database.buildargs(parser)
    return parser

if __name__ == "__main__":
    parser = buildargs()
    args = parser.parse_args()

    init(args)

    try:
        lib.runmodule(args, "main")
    except KeyboardInterrupt:
        io.echo("{/all}*INTR*")
    except EOFError:
        io.echo("{/all}*EOF*")
    finally:
        io.echo(f"{{savecursor}}{{curpos:{io.terminal.height()},0}}{{el}}{{restorecursor}}{{reset}}{{/all}}")
