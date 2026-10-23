"""`message` parses its arguments with an argparse parser built by buildargs(), per the module contract.

buildargs(args, **kw) returns an ArgumentParser. --help is handled by argparse, the parser rejects
unknown flags with a usage line, and parse_message_args uses the same parser, so the help text and
the accepted flags cannot drift apart.
"""

import argparse
import importlib
import inspect

import pytest

lib = importlib.import_module("shell.lib")


@pytest.mark.unit
def test_message_module_exposes_buildargs_with_no_default_for_args():
    mod = importlib.import_module("shell.message")
    sig = inspect.signature(mod.buildargs)
    assert sig.parameters["args"].default is inspect.Parameter.empty


@pytest.mark.unit
def test_buildargs_returns_an_argparse_parser():
    mod = importlib.import_module("shell.message")
    assert isinstance(mod.buildargs(None), argparse.ArgumentParser)


@pytest.mark.unit
def test_parser_accepts_the_documented_flags():
    mod = importlib.import_module("shell.message")
    ns = mod.buildargs(None).parse_args(["--to", "bob,carol", "--body", "hi", "--urgency", "urgent", "--sender", "x"])
    assert ns.to == ["bob,carol"] or ns.to == "bob,carol"
    assert ns.body == "hi"
    assert ns.urgency.upper() == "URGENT"
    assert ns.sender == "x"


@pytest.mark.unit
def test_parser_help_names_every_flag():
    mod = importlib.import_module("shell.message")
    text = mod.buildargs(None).format_help()
    for flag in ("--to", "--body", "--urgency", "--sender"):
        assert flag in text


@pytest.mark.unit
def test_run_message_help_comes_from_the_parser(capsys):
    from unittest.mock import patch
    from types import SimpleNamespace
    mod = importlib.import_module("shell.message")
    with patch.object(lib.io, "echo") as echo:
        assert lib.run_message(SimpleNamespace(debug=False), ["message", "--help"]) is True
    text = " ".join(str(c.args[0]) for c in echo.call_args_list if c.args)
    for flag in ("--to", "--body", "--urgency", "--sender"):
        assert flag in text
