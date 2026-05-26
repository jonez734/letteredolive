from typing import Any

from . import lib


def init(args: Any, **kw: Any) -> bool:
    return True


def access(args: Any, op: str, **kw: Any) -> bool:
    return True


def buildargs(args: Any, **kw: Any) -> None:
    return None


def main(args: Any, **kw: Any) -> bool:
    return lib.runmodule(args, "main", **kw)
