"""The shell `message` command's arguments, parsed with argparse.

``buildargs(args, **kw)`` follows the module contract: it returns the parser, and ``args`` has no
default. The help text and the accepted flags come from this one parser.
"""

from __future__ import annotations

import argparse
from typing import Any

PROG = "message"


def buildargs(args: Any, **kw: Any) -> argparse.ArgumentParser:
    """The parser for ``message --to ... --body ...``."""
    parser = argparse.ArgumentParser(
        prog=PROG,
        description="Send a message as the signed-in member through the bed daemon.",
    )
    parser.add_argument(
        "--to",
        action="append",
        default=[],
        metavar="MONIKER[,MONIKER...]",
        help="recipient(s); comma-separated or repeated",
    )
    parser.add_argument("--body", default=None, help="the message text (quote it if it has spaces)")
    parser.add_argument(
        "--urgency",
        default="ROUTINE",
        type=str.upper,
        choices=["ROUTINE", "IMPORTANT", "URGENT", "CRITICAL"],
        help="urgency (default ROUTINE)",
    )
    parser.add_argument(
        "--sender",
        default=None,
        metavar="NAME",
        help="send as another member; only a sysop may, anyone else is refused",
    )
    return parser


def main(args: Any, **kw: Any) -> bool:
    """Not a standalone program: the shell runs `message` through lib.run_message."""
    return True
