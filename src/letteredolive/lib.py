import os
import sys
import time
import locale
import argparse

import ttyio6 as ttyio
import bbsengine6 as bbsengine

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
  bbsengine.util.setarea(left, right, stack)

commands = {
    "baghdad":     {"prg": "baghdad",     "help": "maintain zoidweb5 sigs"},
    "teos":        {"prg": "teos",        "help": "zoidweb4 sig view"},
    "socrates":    {"prg": "socrates",    "help": "threaded discussion system"},
    "vulcan":      {"prg": "vulcan",      "help": "link database"},
#    "ogun":        {"prg": "ogun",        "help": "zoidweb5 link database"},
    "glossary":    {"prg": "glossary",    "help": "glossary of terms"},
    "empyre":      {"prg": "empyre",      "help": "run the game empyre"},
    "achilles":    {"prg": "achilles",    "help": "achilles: a study of msg and related flavor enhancers"},
#    "engine":      {"prg": "engine",      "help": "manage engine (members, sessions, etc)"},
    "weather":     {"prg": "almanac.weather",     "help": "weather report for a given location"},
    "banderole":   {"prg": "banderole",   "help": "print short string in large letters (from banner)"},
    "votingbooth": {"prg": "votingbooth", "help": "vote on various topics", "aka":"vb"},
    "blackjack":   {"prg": "casino.blackjack",   "help": "the game of blackjack, no gambling"},
    "repo":        {"prg": "repo",        "help": "software repository management"},
    "casino":      {"prg": "casino",      "help": "use the casino"},
    "murdermotel": {"prg": "murdermotel", "help": "the game of 'murder motel' ported from imagebbs"},
    "almanac":     {"prg": "almanac",     "help": "almanac -- weather, zodiac, sun position, and moon position"},
    "postoffice":  {"prg": "postoffice",  "help": "postoffice -- send and receive messages"},
#    "repotools":   {"prg": "repotools",   "help": "software repository tools"},
    "murdermotel": {"prg": "murdermotel", "help": "murder motel -- assassination game"},
    "moneyday":    {"prg": "moneyday",    "help": "displays a calendar showing e.g. the 2nd wednesday of a month"}, 
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

def help(args=None, **kw):
  maxlen = 0
  for k in commands.keys():
    l = len(k)+2
    if l > maxlen:
      maxlen = l

#  ttyio.echo("help.100: maxlen=%r" % (maxlen), level="debug")
  bbsengine.util.heading("shell commands") #, hrcolor="{green}", titlecolor="{bggray}{white}")
  for k, v in commands.items():
    prg = v["prg"] if "prg" in v else None
    if prg is not None and bbsengine.checkmodule(args, v["prg"]) is False:
      continue
    n = k.ljust(maxlen)
    if "help" in v:
      ttyio.echo("{bggray}{white}%s{/bgcolor}{green} %s" % (n, v["help"]))
    else:
      ttyio.echo("{bggray}{white}%s{/bgcolor}{green}" % (n))
  ttyio.echo("{/all}")
  return
