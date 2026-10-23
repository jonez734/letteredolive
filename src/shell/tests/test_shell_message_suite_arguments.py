"""The argument matrix for the shell `message` command, parsed through the real split and parser.

Each case is a typed line. It goes through the same split the loop uses, then the parser.
"""

import importlib

import pytest

from shell import lib

shell_main = importlib.import_module("shell.main")


def _parse(line):
    argv = shell_main.split_input(line)
    assert argv is not None, f"line did not split: {line!r}"
    return lib.parse_message_args(argv)


@pytest.mark.unit
@pytest.mark.parametrize("line,body", [
    ('message --to bob --body "x test"', "x test"),
    ("message --to bob --body 'x test'", "x test"),
    ('message --to bob --body "it\'s fine"', "it's fine"),
    ('message --to bob --body "say \\"hi\\""', 'say "hi"'),
    ("message --to bob --body hi", "hi"),
    ('message --to bob --body ""', None),
])
def test_body_forms(line, body):
    if body is None:
        with pytest.raises(ValueError, match="--body"):
            _parse(line)
        return
    assert _parse(line)["body"] == body


@pytest.mark.unit
def test_comma_separated_recipients():
    assert _parse('message --to bob,carol --body "x"')["recipients"] == ["bob", "carol"]


@pytest.mark.unit
def test_repeated_to_flags():
    assert _parse('message --to bob --to carol --body "x"')["recipients"] == ["bob", "carol"]


@pytest.mark.unit
def test_urgency_is_uppercased():
    assert _parse('message --to bob --body "x" --urgency urgent')["urgency"] == "URGENT"


@pytest.mark.unit
def test_default_urgency_is_routine():
    assert _parse('message --to bob --body "x"')["urgency"] == "ROUTINE"


@pytest.mark.unit
def test_sender_flag_is_parsed():
    assert _parse('message --to bob --body "x" --sender carol')["sender"] == "carol"


@pytest.mark.unit
def test_missing_to_is_refused():
    with pytest.raises(ValueError, match="--to"):
        _parse('message --body "x"')


@pytest.mark.unit
def test_missing_body_is_refused():
    with pytest.raises(ValueError, match="--body"):
        _parse("message --to bob")


@pytest.mark.unit
def test_unknown_flag_is_refused():
    with pytest.raises(ValueError, match="unrecognized arguments"):
        _parse('message --to bob --body "x" --bogus 1')


@pytest.mark.unit
def test_flag_without_a_value_is_refused():
    with pytest.raises(ValueError, match="expected one argument"):
        _parse('message --to bob --body')


@pytest.mark.unit
def test_unmatched_quote_does_not_split():
    assert shell_main.split_input('message --to bob --body "oops') is None
