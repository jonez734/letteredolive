import asyncio
import getpass
import os
import sys
import types
from typing import Any, List, Optional

from bbsengine6 import io, screen, member, module, util
from bbsengine6.member import _threadlocal

from bed.client.probe import probe_bed
from bed.client.authservice import BedAuthServiceClient
from bed.client import get_bed_connection
from bed.tools import _token
from bed.client.connection import BedConnection


PACKAGENAME = "shell"
LOGIN_EXIT_CODE = 1
# @see https://sites.google.com/site/xiangyangsite/home/technical-tips/software-development/python/python-readline-completions
# @see https://docs.python.org/3.3/howto/argparse.html#introducing-positional-arguments
# @see https://docs.python.org/3.3/library/argparse.html#module-argparse
# @see https://pymotw.com/3/importlib/
#


def setbottombar(args, left="", stack=False):
    def right():
        currentmember = member.getcurrent(args)
        if currentmember is None:
            return ""
        rightbuf = "| %s | %s" % (
            currentmember["moniker"],
            util.pluralize(currentmember["credits"], "credit", "credits"),
        )
        if args.debug is True:
            rightbuf += " | debug"
        return rightbuf

    if args.debug is True:
        io.echo(
            f"shell.lib.setarea.right.100: left={left!r} right={right!r} stack={stack!r}",
            level="debug",
        )
    screen.setbottombar(left, right)


commands = {
    #    "baghdad":     {"prg": "baghdad",     "help": "maintain zoidweb5 sigs"},
    #    "teos":        {"prg": "teos",        "help": "zoid6 sig view"},
    #    "socrates":    {"prg": "socrates",    "help": "threaded discussion system"},
    #    "vulcan":      {"prg": "vulcan",      "help": "link database"},
    #    "ogun":        {"prg": "ogun",        "help": "zoidweb5 link database"},
    #    "glossary":    {"prg": "glossary",    "help": "glossary of terms"},
    "empyre": {"prg": "empyre", "help": "run the game empyre"},
    #    "achilles":    {"prg": "achilles",    "help": "achilles: a study of msg and related flavor enhancers"},
    "con": {"prg": "con", "help": "system operations console"},
    "weather": {
        "prg": "almanac.weather",
        "help": "weather report for a given location",
    },
    "banderole": {
        "prg": "banderole",
        "help": "print short string in large letters (from figlet)",
    },
    #    "votingbooth": {"prg": "votingbooth", "help": "vote on various topics", "aka":"vb"},
    #    "blackjack":   {"prg": "casino.blackjack",   "help": "the game of blackjack, no gambling"},
    "repo": {"prg": "repo", "help": "software repository"},
    #    "casino":      {"prg": "casino",      "help": "use the casino"},
    "murdermotel": {
        "prg": "murdermotel",
        "help": "murder motel -- assassination game",
    },
    "moneyday": {
        "prg": "moneyday",
        "help": "displays a calendar showing e.g. the 2nd wednesday of a month",
    },
    "logout": {"help": "logout of the system"},
    "exit": {"help": "exit shell"},
}


def visible_commands(args: Any) -> List[str]:
    """Commands the user may run: listed in the registry and installed.

    A command whose module is missing stays in ``commands`` but is hidden here,
    so help and tab completion show only what can run. ``logout`` and ``exit``
    have no module and are always visible.
    """
    out: List[str] = []
    for name, spec in commands.items():
        prg = spec.get("prg")
        if prg is None or module.check(args, prg) is not False:
            out.append(name)
    return out


def dispatch_message(name: str) -> str:
    """Decide what a typed command does: 'run', 'not_installed', or 'unknown'."""
    if name not in commands:
        return "unknown"
    spec = commands[name]
    prg = spec.get("prg")
    if prg is None:
        return "run"
    if module.check(None, prg) is False:
        io.echo(f"'{name}' is not installed on this system.", level="error")
        return "not_installed"
    return "run"


class shellCommandCompleter:
    def __init__(self, args: Any) -> None:
        self._args = args

    @classmethod
    def complete(cls, text: str, state: int) -> Optional[str]:
        vocab = visible_commands(None)
        results = [x for x in vocab if x.startswith(text)] + [None]
        return results[state]


def help(**kwargs: Any) -> None:
    args: Any = kwargs.get("args")

    io.echo("help")

    maxlen = 0
    for k in commands:
        klen = len(k) + 2
        if klen > maxlen:
            maxlen = klen

    util.heading("shell commands")
    shown = set(visible_commands(args))
    for k, v in commands.items():
        if k not in shown:
            continue
        n = k.ljust(maxlen)
        if "help" in v:
            io.echo(f"{{var:optioncolor}} {n}{{var:labelcolor}} {v['help']}")
        else:
            io.echo(f"{{var:optioncolor}} {n}")
    io.echo("{/all}")
    return


def checkmodule(args: Any, modulename: str, **kwargs: Any) -> bool:
    x = f"{PACKAGENAME}.{modulename}"
    return module.check(args, x, **kwargs)


def runmodule(args: Any, modulename: str, **kwargs: Any) -> bool:
    x = f"{PACKAGENAME}.{modulename}"
    if args.debug is True:
        io.echo(f"shell.100: {x=}", level="debug")

    if module.check(args, x, **kwargs) is False:
        io.echo(f"shell.120: module {x} not available", level="error")
        return False

    return module.runmodule(args, x, **kwargs)


def default_token_file() -> str:
    """Token path: $XDG_RUNTIME_DIR/bed.token, else /tmp/bed-<uid>/bed.token."""
    runtime = os.environ.get("XDG_RUNTIME_DIR", "").strip()
    if runtime and os.path.isdir(runtime) and os.access(runtime, os.W_OK):
        return os.path.join(runtime, "bed.token")
    return f"/tmp/bed-{os.getuid()}/bed.token"


def reconnect(args: Any, token: str) -> dict:
    """Ask bed to validate ``token``. Returns bed's reply dict."""
    svc = BedAuthServiceClient(get_bed_connection(args))
    return asyncio.run(svc.reconnect(token))


def prompt_credentials() -> tuple:
    """Ask for moniker and password. The password is never echoed."""
    moniker = input("moniker: ").strip()
    password = getpass.getpass("password: ")
    return moniker, password


def _set_session(moniker: str) -> str:
    _threadlocal.moniker = moniker
    return moniker


def clear_session() -> None:
    """Forget the logged-in moniker (logout / exit)."""
    if hasattr(_threadlocal, "moniker"):
        del _threadlocal.moniker


def _bed_unreachable(args: Any) -> None:
    host = getattr(args, "bed_host", "127.0.0.1")
    port = getattr(args, "bed_port", 8765)
    sys.stderr.write(
        f"bed is not reachable at {host}:{port}; the shell cannot start. "
        "Start the bed service and try again.\n"
    )


def _try_token(args: Any, token_path: str) -> Optional[str]:
    """Return the moniker a valid token logs in as, or None."""
    try:
        token = _token.read_token_file(token_path)
    except PermissionError as e:
        io.echo(f"token file refused: {e}", level="error")
        return None
    except OSError:
        return None
    if not token:
        return None
    try:
        reply = reconnect(args, token)
    except (OSError, ConnectionError, TimeoutError) as e:
        _bed_unreachable(args)
        raise _BedDown() from e
    if reply.get("ok") and reply.get("moniker"):
        return reply["moniker"]
    # Rejected token: remove it so it is not retried on every start.
    try:
        os.remove(token_path)
    except OSError:
        pass
    return None


class _BedDown(Exception):
    """bed stopped answering during the token check."""


def open_login_connection(args: Any):
    """A one-shot bed connection for a password login (closed by the caller)."""
    return BedConnection(args)


def password_login_client(conn: Any) -> BedAuthServiceClient:
    return BedAuthServiceClient(conn)


def persist_token(reply: dict, args: Any) -> bool:
    """Save the token from a successful login, as casino does."""
    from bed.tools import auth as _bed_auth_tool

    bed_args = types.SimpleNamespace(
        token_file=getattr(args, "token_file", None) or default_token_file(),
        debug=False,
    )
    return _bed_auth_tool._persist_token(reply, bed_args)


def _password_login(args: Any, moniker: str, password: str) -> Optional[str]:
    """Log in through bed (server-side check), then save the token. None on refusal."""
    conn = open_login_connection(args)
    try:
        reply = asyncio.run(password_login_client(conn).login(moniker, password))
    finally:
        try:
            conn.force_close()
        except Exception:
            pass
    if not reply.get("ok"):
        io.echo("login refused", level="error")
        return None
    if not (reply.get("token") or "").strip():
        io.echo("bed returned no token; login aborted", level="error")
        return None
    persist_token(reply, args)
    return reply.get("moniker") or moniker


def shell_login(args: Any) -> Optional[str]:
    """Gate the shell: bed must be up; a valid token logs in; else a password.

    Returns the moniker on success, or None when the shell must not start.
    A blank moniker or password re-prompts. Ctrl-D cancels the login. Nothing
    sensitive is printed.
    """
    if not probe_bed(args):
        _bed_unreachable(args)
        return None

    token_path = getattr(args, "token_file", None) or default_token_file()
    try:
        moniker = _try_token(args, token_path)
    except _BedDown:
        return None
    if moniker is not None:
        return _set_session(moniker)

    while True:
        try:
            moniker, password = prompt_credentials()
        except EOFError:
            sys.stderr.write("login cancelled\n")
            return None
        if not moniker or not password:
            continue
        logged_in = _password_login(args, moniker, password)
        if logged_in is None:
            return None
        return _set_session(logged_in)
