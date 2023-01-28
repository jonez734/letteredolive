import os
import sys
import time
import locale
import argparse
import importlib
import traceback

import ttyio5 as ttyio
import bbsengine5 as bbsengine

#
# @see https://sites.google.com/site/xiangyangsite/home/technical-tips/software-development/python/python-readline-completions
# @see https://docs.python.org/3.3/howto/argparse.html#introducing-positional-arguments
# @see https://docs.python.org/3.3/library/argparse.html#module-argparse
# @see https://pymotw.com/3/importlib/
#

def setarea(args, left, stack=False):
  def right():
    currentmember = bbsengine.getcurrentmember(args)
    if currentmember is None:
      return ""
    rightbuf = "| %s | %s" % (currentmember["name"], bbsengine.pluralize(currentmember["credits"], "credit", "credits"))
    if args.debug is True:
      rightbuf += " | debug"
    return rightbuf
  bbsengine.setarea(left, right, stack)

#def runprg(args, **kwargs):
#  print("runprg.100: trace")
#  parents = kwargs["parents"] if "parents" in kwargs else []
#  command = kwargs["command"] if "command" in kwargs else None
#  prg = command["prg"] if "prg" in command else None
#  if command is None:
#    return None
# return bbsengine.runcallback(args, prg, **kwargs)  # callprgmethod(args, prg, **kwargs)
#  ttyio.echo("runprg.120: module=%r" % (module))
#  if prg is None:
#    return None
#  x = prg.split(".")
#  m = x[0]
#  if len(x) == 1:
#    f = "main"
#  else:
#    f = x[1]
#  a = importlib.import_module(m)
#  ttyio.echo("a=%r" % (a), interpet=False, level="debug")
#  res = eval("a.%s" % (f), {"a": a})
#  print(res)
#  if callable(res) is True:
#    res(args, **kwargs)
#  else:
#    ttyio.echo("programming error", level="error")
#  return

commands = {
    "baghdad":     {"prg": "baghdad",     "help": "maintain zoidweb5 sigs"},
    "teos":        {"prg": "teos",        "help": "zoidweb4 sig view"},
    "socrates":    {"prg": "socrates",    "help": "threaded discussion system"},
    "vulcan":      {"prg": "vulcan",      "help": "link database"},
    "ogun":        {"prg": "ogun",        "help": "zoidweb5 link database"},
    "glossary":    {"prg": "glossary",    "help": "glossary of terms"},
    "empyre":      {"prg": "empyre",      "help": "run the game empyre"},
    "achilles":    {"prg": "achilles",    "help": "achilles: a study of msg and related flavor enhancers"},
    "engine":      {"prg": "engine",      "help": "manage engine (members, sessions, etc)"},
    "weather":     {"prg": "almanac.weather",     "help": "weather report for a given location"},
    "banderole":   {"prg": "banderole",   "help": "print short string in large letters (from banner)"},
    "votingbooth": {"prg": "votingbooth", "help": "vote on various topics", "aka":"vb"},
#    "projup":      {"prg": "zoidbo.project.projup",      "help": "add or update a project to projectflow"},
#    "pho":         {"prg": "zoidbo.project.pho",         "help": "lookup phone numbers"},
#    "grepproj":    {"prg": "zoidbo.project.grepproj",    "help": "search through projects"},
    "blackjack":   {"prg": "casino.blackjack",   "help": "the game of blackjack, no gambling"},
    "repo":        {"prg": "repo",        "help": "software repository management"},
    "casino":      {"prg": "casino",      "help": "use the casino"},
    "murdermotel": {"prg": "murdermotel", "help": "the game of 'murder motel' ported from imagebbs"},
    "almanac":     {"prg": "almanac",     "help": "almanac -- weather, zodiac, sun position, and moon position"},
    "postoffice":  {"prg": "postoffice",  "help": "postoffice -- send and receive messages"},
    "repotools":   {"prg": "repotools",   "help": "software repository tools"},
    "murdermotel": {"prg": "murdermotel", "help": "murder motel -- assassination game"},
    "whiteboard":  {"prg": "zoidbackoffice.whiteboard", "help": "whiteboard -- part of zoid backoffice"},
    "wb":          {"prg": "zoidbackoffice.whiteboard", "help": "whiteboard -- part of zoid backoffice"},

    "logout":      {"help": "logout of the system"},
    "exit":        {"help": "exit shell"},
}

# @since 20201125
class shellCommandCompleter(object):
  def __init__(self:object, args:object):
#    ttyio.echo("init shellCommandCompleter object", level="debug")
    pass

  @classmethod
  def complete(self:object, text:str, state:int):
    vocab = []
    for c in commands.keys():
      vocab.append(c)
    results = [x for x in vocab if x.startswith(text)] + [None]
    return results[state]

def help():
  maxlen = 0
  for k in commands.keys():
    l = len(k)+2
    if l > maxlen:
      maxlen = l

#  ttyio.echo("help.100: maxlen=%r" % (maxlen), level="debug")
  bbsengine.title("shell commands") #, hrcolor="{green}", titlecolor="{bggray}{white}")
  for k, v in commands.items():
    n = k.ljust(maxlen)
    if "help" in v:
      ttyio.echo("{bggray}{white}%s{/bgcolor}{green} %s" % (n, v["help"]))
    else:
      ttyio.echo("{bggray}{white}%s{/bgcolor}{green}" % (n))
  ttyio.echo("{/all}")
  return

def buildargs(args=None):
  argparser = argparse.ArgumentParser(prog="letteredolive")
  argparser.add_argument("--verbose", default=True, action="store_true", help="use verbose mode")
  argparser.add_argument("--debug", default=False, action="store_true", help="use debug mode")

  defaults = {"databasename":"zoidweb5", "databasehost": "localhost", "databaseport":5432, "databaseuser": None, "databasepassword":None}
  bbsengine.buildargdatabasegroup(argparser, defaults)

  return argparser

def main(args=None):
#  ttyio.setvariable("engine.areacolor", "{bggray}{white}")

  locale.setlocale(locale.LC_ALL, "")
  time.tzset()

#  ttyio.echo("args=%r" % (args), level="debug")

  bbsengine.initscreen()

#  setarea(args, "the galaxy federation bbs", stack=True)

  done = False
  while not done:
    # @todo: handle subcommands as tab-complete (@see cmd2)
    # ttyio.echo("args=%r" % (args), level="debug")

    setarea(args, "the galaxy federation bbs", stack=False)

#	ttyio.setvariable("engine.areacolor", "{bggray}{white}")

    if args.debug is True:
      ttyio.echo("bbs.main.200: areastack=%r" % (bbsengine.areastack), level="debug")

    prompt = "{f6}{var:promptcolor}%s{F6}gfd main: {var:inputcolor}" % (bbsengine.datestamp(format="%c"))

    try:
      buf = ttyio.inputstring(prompt, multiple=False, returnseq=False, verify=None, completer=shellCommandCompleter(args), completerdelims=" ")
    except EOFError:
      ttyio.echo("EOF")
      return
    except KeyboardInterrupt:
      ttyio.echo("INTR")
      return

    if buf is None or buf == "":
      continue
    elif buf == "?" or buf == "help":
      help()
      continue
    elif buf in ("logout", "lo", "quit", "q", "o!", "o"):
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
      ttyio.echo("bbs.100: argv=%r" % (argv), level="debug")
    try:
      bbsengine.runmodule(args, prg, argv=argv)
    except EOFError:
      raise
    except KeyboardInterrupt:
      raise
    except Exception:
      traceback.print_exc(file=sys.stdout)
#    bbsengine.runcallback(args, "%s.init" % (prg))
#    prgargparse = bbsengine.runcallback(args, "%s.buildargs" % (prg))
#    if prgargparse is not None:
#      try:
#        prgargs = prgargparse.parse_args(argv[1:])
#      except SystemExit:
#        continue
#      except argparse.ArgumentError:
#        ttyio.echo("argument error", level="error")
#        continue

#      if args.debug is True:
#        ttyio.echo("bbs.main.220: prgargs=%r" % (prgargs), level="debug")
#      done = bbsengine.runcallback(prgargs, "%s.main" % (prg))

#    bbsengine.poparea()

if __name__ == "__main__":
  argparser = buildargs()
  args = argparser.parse_args()

  try:
      main(args)
  except KeyboardInterrupt:
      ttyio.echo("{/all}{bold}INTR{bold}")
  except EOFError:
      ttyio.echo("{/all}{bold}EOF{/bold}")
  finally:
      ttyio.echo("{decsc}{curpos:%d,0}{el}{decrc}{reset}{/all}" % (ttyio.getterminalheight()))
