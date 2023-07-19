def access(args, op, **kw):
    return True

def init(args, **kw):
    return True

def main(args=None, **kw):
#  ttyio.setvariable("engine.areacolor", "{bggray}{white}")

  locale.setlocale(locale.LC_ALL, "")
  time.tzset()

#  ttyio.echo("args=%r" % (args), level="debug")

  bbsengine.screen.init()

#  setarea(args, "the galaxy federation bbs", stack=True)

  done = False
  while not done:
    # @todo: handle subcommands as tab-complete (@see cmd2)
    # ttyio.echo("args=%r" % (args), level="debug")

    setarea(args, "the galaxy federation bbs", stack=False)

#	ttyio.setvariable("engine.areacolor", "{bggray}{white}")

#    if args.debug is True:
#      ttyio.echo("bbs.main.200: areastack=%r" % (bbsengine.areastack), level="debug")

    preinputhook = f"{{f6}}{{var:promptcolor}}{bbsengine.datestamp(format='%c')}"
    prompt = "{var:promptcolor}gfd main: {var:inputcolor}"

    try:
      buf = ttyio.inputstring(prompt, multiple=False, returnseq=False, verify=None, completer=shellCommandCompleter(args), completerdelims=" ", preinputhook=preinputhook, help=help)
    except EOFError:
      ttyio.echo("EOF")
      return
    except KeyboardInterrupt:
      ttyio.echo("INTR")
      return

    if buf is None or buf == "":
      continue
    elif buf == "?" or buf == "help":
      help(args)
      continue
    elif buf in ("exit", "logout", "lo", "quit", "q", "o!", "o"):
      ttyio.echo("logout")
      done = True
      break

    argv = buf.split(" ")
    if argv[0] not in commands:
      ttyio.echo("command not found", level="error")
      continue

    v = commands[argv[0]]
    if args.debug is True:
      ttyio.echo("v=%r" % (v), level="debug")
    prg = v["prg"]
    if args.debug is True:
      ttyio.echo("letteredolive.100: argv=%r" % (argv), level="debug")
    try:
      bbsengine.runmodule(args, prg, argv=argv)
    except EOFError:
      raise
    except KeyboardInterrupt:
      raise
    except Exception:
      import traceback
      traceback.print_exc(file=sys.stdout)
