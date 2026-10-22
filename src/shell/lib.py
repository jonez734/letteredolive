import asyncio
import os
import sys
import types
from typing import Any, List, Optional

from bbsengine6 import io, member, module, util
from bbsengine6 import bottombar as _bottombar
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


_screen_initialized: bool = False


def init_screen(args: Any = None) -> None:
    """Set the terminal scroll region once, so the bottom bar stays on the last line.

    Same pattern as casino: the margins are set before the first setbottombar call.
    """
    global _screen_initialized
    if _screen_initialized:
        return
    from bbsengine6.io import terminal

    _screen_initialized = True
    io.echo("{f6:3}{cursorup:3}", end="", flush=True)
    h = terminal.lines() - 1
    io.echo("{savecursor}", end="")
    io.echo("{decstbm:%s,%s}" % (1, h), end="")
    io.echo("{restorecursor}", flush=True, end="")


def setbottombar(args, left="", stack=False):
    def right(**kwargs):
        # bottombar.render calls each fragment with keyword arguments (args, player,
        # pool). Use the args it passes, else the args this shell was started with.
        render_args = kwargs.get("args", args)
        moniker = member.getcurrentmoniker(render_args)
        if moniker is None:
            return ""
        balance = member.getbalance(render_args, moniker, pool=kwargs.get("pool"))
        if balance is None:
            return ""
        rightbuf = "| %s | %d %s" % (
            moniker,
            balance,
            "credit" if balance == 1 else "credits",
        )
        if render_args.debug is True:
            rightbuf += " | debug"
        return rightbuf

    if args.debug is True:
        io.echo(
            f"shell.lib.setarea.right.100: left={left!r} stack={stack!r}",
            level="debug",
        )
    _bottombar.register_bottombar_fragment(right)
    _bottombar.setbottombar(args, left)


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
        "disabled": True,
    },
    "banderole": {
        "prg": "banderole",
        "help": "print short string in large letters (from figlet)",
        "disabled": True,
    },
    #    "votingbooth": {"prg": "votingbooth", "help": "vote on various topics", "aka":"vb"},
    #    "blackjack":   {"prg": "casino.blackjack",   "help": "the game of blackjack, no gambling"},
    "repo": {"prg": "repo", "help": "software repository", "disabled": True},
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
        if spec.get("disabled") is True:
            continue
        prg = spec.get("prg")
        if prg is None or module.check(args, prg) is not False:
            out.append(name)
    return out


def dispatch_message(name: str) -> str:
    """Decide what a typed command does: 'run', 'not_installed', or 'unknown'."""
    if name not in commands:
        return "unknown"
    spec = commands[name]
    if spec.get("disabled") is True:
        io.echo(f"'{name}' is disabled (not installed).", level="error")
        return "disabled"
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
    """Ask for moniker and password. A blank field asks again. The password is never echoed.

    Ctrl-D raises EOFError, which the caller treats as cancel.
    """
    moniker = ""
    while not moniker:
        moniker = io.inputstring("moniker: ", "").strip()
    password = ""
    while not password:
        password = util.inputpassword("password: ")
    return moniker, password


def _set_session(moniker: str, args: Any = None) -> str:
    """Record the logged-in moniker for the session.

    The member is looked up by moniker (member.getcurrentmoniker and getbalance),
    so no member id is kept here.
    """
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
    """Log in through bed (server-side check), then save the token. None on refusal.

    The login and the connection close run in one coroutine, on one event loop.
    Closing after asyncio.run has ended that loop fails with "attached to a different loop".
    """
    conn = open_login_connection(args)

    async def _login_and_close() -> dict:
        try:
            return await password_login_client(conn).login(moniker, password)
        finally:
            # Await the websocket close on this loop. bed's force_close would
            # schedule the close on another loop and fail with "attached to a
            # different loop".
            ws = getattr(conn, "_ws", None)
            conn._ws = None
            if ws is not None:
                try:
                    await ws.close()
                except Exception:
                    pass

    reply = asyncio.run(_login_and_close())
    if not reply.get("ok"):
        io.echo("login refused", level="error")
        return None
    if not (reply.get("token") or "").strip():
        io.echo("bed returned no token; login aborted", level="error")
        return None
    persist_token(reply, args)
    _LAST_LOGIN["value"] = reply.get("last_login")
    return reply.get("moniker") or moniker


_LAST_LOGIN: dict = {"value": None}


def _last_login_for(moniker: str):
    """The previous password login (ISO time) bed reported for this login, or None."""
    return _LAST_LOGIN.get("value")


def _welcome(moniker: str, last_login, info: dict) -> None:
    """Print the welcome line: moniker, last login, and the balance with its source.

    Never includes the password or the token.
    """
    if info["source"] == "credits":
        balance_text = f"credits: {info['balance']}"
    else:
        balance_text = f"bank balance: {info['balance']}"
    when = last_login if last_login else "never (first login)"
    io.echo(f"welcome back {moniker}! last login: {when}, {balance_text}", level="ok")


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
        return _set_session(moniker, args)

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
        _show_welcome(args, logged_in)
        return _set_session(logged_in, args)


def _show_welcome(args: Any, moniker: str) -> None:
    """Show the welcome line for a password login.

    The welcome is informational. A failed balance lookup is reported and skipped, so the
    login itself is never affected.
    """
    try:
        info = member.getbalance_info(args, moniker)
    except Exception as e:
        io.echo(f"welcome: balance unavailable ({e.__class__.__name__}); login is unaffected", level="warning")
        return
    if info is None:
        return
    _welcome(moniker, _last_login_for(moniker), info)
