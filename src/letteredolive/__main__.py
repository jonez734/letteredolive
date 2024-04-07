import argparse
from bbsengine6 import io, screen, database
import bbsengine6 as bbsengine

from . import lib

#from . import module

def init(args, **kw):
    bbsengine.init(args)
    screen.init()

    return True

def access(args, op, **kw):
    return True

def buildargs(args=None, **kw):
    parser = argparse.ArgumentParser("letteredolive")
    parser.add_argument("--debug", default=False)
    database.buildarggroup(parser)
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
