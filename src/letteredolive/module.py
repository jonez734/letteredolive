import time
import locale
import argparse

#import ttyio6 as ttyio
#import bbsengine6 as bbsengine
from bbsengine6 import util, io, database

from . import lib
from . import _version

def init(args=None, **kw):
#    ttyio.setvariable("empyre.highlightcolor", "{bggray}{white}")
#    ttyio.echo("empyre.boot.init", level="debug")
    return True

def buildargs(args=None, **kw):
    parser = argparse.ArgumentParser("letteredolive")
    parser.add_argument("--verbose", action="store_true", dest="verbose")
    parser.add_argument("--debug", action="store_true", dest="debug")

    defaults = {"databasename": "zoid6", "databasehost":"localhost", "databaseuser": None, "databaseport":5432, "databasepassword":None}
    database.buildargdatabasegroup(parser, defaults)

    return parser
    
def main(args, **kw):
    if args is not None and "debug" in args and args.debug is True:
        io.echo(f"letteredolive.main.100: {args=}", level="debug")

    util.heading("lettered olive")

    if args.debug is True:
        io.echo(f"{{var:labelcolor}}database: {{var:valuecolor}}{args.databasename} {{var:labelcolor}}host: {{var:valuecolor}}{args.databasehost}{{var:labelcolor}}:{{var:valuecolor}}{args.databaseport}", level="debug", end="")
        if args.databasepassword is not None:
            io.echo("{var:labelcolor}password: {var:valuecolor}Yes")
        else:
            io.echo("{var:labelcolor}password: {var:valuecolor}No")

#    ttyio.echo(f"letteredolive.main.main.100: args={args!r}", level="debug")
    lib.setarea(args, "letteredolive", f"startup {_version.__datestamp__} rev {_version.__version__}")

    if lib.runsubmodule(args, "main") is False:
        io.echo("error running submodule 'main'", level="error")
    return    
