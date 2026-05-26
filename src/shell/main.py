from typing import Any

from bbsengine6 import io, screen, util, module

from . import lib


def access(args: Any, op: str, **kwargs: Any) -> bool:
    return True


def init(args: Any, **kwargs: Any) -> bool:
    return True


def buildargs(args: Any = None, **kwargs: Any) -> None:
    return None


def main(args: Any, **kwargs: Any) -> None:
    screen.init()

    done = False
    while not done:
        # @todo: handle subcommands as tab-complete (@see cmd2)
        # ttyio.echo("args=%r" % (args), level="debug")

        lib.setbottombar(args, "falcon", stack=False)

        # ttyio.setvariable("engine.areacolor", "{bggray}{white}")

        #    if args.debug is True:
        #      ttyio.echo("bbs.main.200: areastack=%r" % (bbsengine.areastack), level="debug")

        preinputhook = f"{{f6}}{{var:promptcolor}}{util.datestamp(format='%c')}"
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
            done = True
            break

        if args.debug is True:
            io.echo(f"shell.100: {buf=}", level="debug")

        argv = buf.split(" ")
        if argv[0] not in lib.commands:
            known_bbs_games = [
                "murdermotel",
                "empyre",
                "con",
                "repo",
                "weather",
                "banderole",
                "moneyday",
            ]
            if argv[0] in known_bbs_games:
                io.echo(
                    f"'{argv[0]}' is not installed or not accessible. Run: sudo pip install {argv[0]}",
                    level="error",
                )
            else:
                io.echo(f"unknown command '{argv[0]}'", level="error")
            continue

        v = lib.commands[argv[0]]
        if args.debug is True:
            io.echo(f"{v=}", level="debug")
        prg = v["prg"]
        if args.debug is True:
            io.echo(f"shell.100: {argv=}", level="debug")
        try:
            module.runmodule(args, prg, argv=argv, pool=kwargs.get("pool"))
        except EOFError:
            raise
        except KeyboardInterrupt:
            raise
        except Exception as e:
            io.echo_traceback(f"shell.main: {e}")
