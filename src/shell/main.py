import argparse
import shlex
from typing import Any, Optional, List

from bbsengine6 import io, util, module

from . import lib


def access(args: Any, op: str, **kwargs: Any) -> bool:
    return True


def split_input(buf: str) -> Optional[List[str]]:
    """Split a typed line into arguments with shell-style quoting.

    ``--body "x test"`` gives one argument, ``x test``. Returns None for an unmatched quote,
    so the caller can report it and redraw the prompt.
    """
    try:
        return shlex.split(buf)
    except ValueError:
        return None


def init(args: Any, **kwargs: Any) -> bool:
    return True


def buildargs(args: Any, **kwargs: Any) -> argparse.ArgumentParser | None:
    return None


def main(args: Any, **kwargs: Any) -> bool | None:
    lib.init_screen(args)

    done = False
    while not done:
        # @todo: handle subcommands as tab-complete (@see cmd2)
        # ttyio.echo("args=%r" % (args), level="debug")

        lib.setbottombar(args, "falcon", stack=False)

        # ttyio.setvariable("engine.areacolor", "{bggray}{white}")

        #    if args.debug is True:
        #      ttyio.echo("bbs.main.200: areastack=%r" % (bbsengine.areastack), level="debug")

        preinputhook = f"{{f6}}{{var:promptcolor}}{util.datestamp()}"
        prompt = "{var:promptcolor}ProtoVision: {var:inputcolor}"

        buf = io.inputstring(
            prompt,
            multiple=False,
            returnseq=False,
            verify=None,
            completer=lib.shellCommandCompleter(args),
            completerdelims=" ",
            preinputhook=preinputhook,
            help=lib.help,
            args=args,
        )

        if buf is None or buf == "":
            continue
        #    elif buf == "?" or buf == "help" or buf == "KEY_HELP":
        #      ttyio.echo("help")
        #      lib.help(args=args)
        #      continue
        elif buf in ("exit", "logout", "lo", "quit", "q", "o!", "o"):
            io.echo("logout")
            lib.clear_session()
            done = True
            break

        if args.debug is True:
            io.echo(f"shell.100: {buf=}", level="debug")

        argv = split_input(buf)
        if argv is None:
            io.echo("unmatched quote in command", level="error")
            continue
        if not argv:
            continue
        decision = lib.dispatch_message(argv[0])
        if decision == "unknown":
            io.echo(f"unknown command '{argv[0]}'", level="error")
            continue
        if decision in ("not_installed", "disabled"):
            continue

        v = lib.commands[argv[0]]
        if args.debug is True:
            io.echo(f"{v=}", level="debug")
        if args.debug is True:
            io.echo(f"shell.100: {argv=}", level="debug")
        try:
            if v.get("handler") == "run_message":
                lib.run_message(args, argv)
            else:
                module.runmodule(args, v["prg"], argv=argv, pool=kwargs.get("pool"))
        except EOFError:
            raise
        except KeyboardInterrupt:
            raise
        except Exception as e:
            io.echo_traceback(f"shell.main: {e}")
