"""The shell splits typed input with shell-style quoting, so a quoted value stays one argument.

--body "x test" must reach the message command as one argument, not as "x", test". An unmatched
quote is reported and the prompt is redrawn; it does not end the shell.
"""

import shlex

import pytest

import importlib

from shell import lib

shell_main = importlib.import_module("shell.main")


@pytest.mark.unit
def test_split_keeps_double_quoted_value_together():
    assert shell_main.split_input('message --to bob --body "x test"') == [
        "message", "--to", "bob", "--body", "x test"]


@pytest.mark.unit
def test_split_keeps_single_quoted_value_together():
    assert shell_main.split_input("message --to bob --body 'x test'") == [
        "message", "--to", "bob", "--body", "x test"]


@pytest.mark.unit
def test_split_plain_words_still_split_on_spaces():
    assert shell_main.split_input("message --to bob --body hi") == [
        "message", "--to", "bob", "--body", "hi"]


@pytest.mark.unit
def test_split_handles_apostrophe_inside_double_quotes():
    assert shell_main.split_input('message --to bob --body "it\'s fine"') == [
        "message", "--to", "bob", "--body", "it's fine"]


@pytest.mark.unit
def test_unmatched_quote_returns_none_and_does_not_raise():
    assert shell_main.split_input('message --to bob --body "oops') is None


@pytest.mark.unit
def test_quoted_body_reaches_the_parser_as_one_value():
    argv = shell_main.split_input('message --to bob --body "x test"')
    parsed = lib.parse_message_args(argv)
    assert parsed["body"] == "x test"
