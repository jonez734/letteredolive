import time
import locale

#import bbsengine6 as bbsengine
#import ttyio6 as ttyio
from bbsengine6 import io, screen, util, module

from . import lib

def access(args, op, **kwargs):
    return True

def init(args, **kwargs):
    return True

def buildargs(args=None, **kwargs):
  return None

def main(args, **kwargs):
#  ttyio.setvariable("engine.areacolor", "{bggray}{white}")

  locale.setlocale(locale.LC_ALL, "")
  time.tzset()

#  ttyio.echo("args=%r" % (args), level="debug")

  screen.init()

#  setarea(args, "the galaxy federation bbs", stack=True)

  done = False
  while not done:
    # @todo: handle subcommands as tab-complete (@see cmd2)
    # ttyio.echo("args=%r" % (args), level="debug")

    lib.setbottombar(args, "falcon", stack=False)

#	ttyio.setvariable("engine.areacolor", "{bggray}{white}")

#    if args.debug is True:
#      ttyio.echo("bbs.main.200: areastack=%r" % (bbsengine.areastack), level="debug")

    preinputhook = f"{{f6}}{{var:promptcolor}}{util.datestamp(format='%c')}"
    prompt = "{var:promptcolor}ProtoVision: {var:inputcolor}"

    buf = io.inputstring(prompt, multiple=False, returnseq=False, verify=None, completer=lib.shellCommandCompleter(args), completerdelims=" ", preinputhook=preinputhook, help=lib.help, args=args)

    if buf is None or buf == "":
      continue
#    elif buf == "?" or buf == "help" or buf == "KEY_HELP":
#      ttyio.echo("help")
#      lib.help(args=args)
#      continue
    elif buf in ("exit", "logout", "lo", "quit", "q", "o!", "o"):
      io.echo("logout")
      done = True
      break

    if args.debug is True:
      io.echo(f"letteredolive.100: {buf=}", level="debug")

    argv = buf.split(" ")
    if argv[0] not in lib.commands:
      io.echo("command not found", level="error")
      continue

    v = lib.commands[argv[0]]
    if args.debug is True:
      io.echo(f"{v=}", level="debug")
    prg = v["prg"]
    if args.debug is True:
      io.echo(f"letteredolive.100: {argv=}", level="debug")
    try:
      module.runmodule(args, prg, argv=argv)
    except EOFError:
      raise
    except KeyboardInterrupt:
      raise
    except Exception:
      import traceback, sys
      traceback.print_exc(file=sys.stdout)
