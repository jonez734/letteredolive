"""The shell's entry point connects to 'zoid6' by default, never to the NEEDINFO sentinel.

bbsengine6's database.buildargs falls back to BBSENGINE6_DBNAME_DEFAULT ("NEEDINFO")
when no name is given. The shell must supply its own default, so a plain `shell`
run connects to zoid6 instead of the unconfigured sentinel.
"""

import os
from unittest.mock import patch

import pytest

from shell import __main__ as shell_main


@pytest.mark.unit
def test_entry_point_parser_defaults_to_zoid6(monkeypatch):
    monkeypatch.delenv("BBSENGINE6_DBNAME", raising=False)
    args = shell_main.buildargs(None).parse_args([])
    assert args.databasename == "zoid6"


@pytest.mark.unit
def test_entry_point_parser_never_resolves_to_the_sentinel(monkeypatch):
    from bbsengine6.database import BBSENGINE6_DBNAME_DEFAULT

    monkeypatch.delenv("BBSENGINE6_DBNAME", raising=False)
    args = shell_main.buildargs(None).parse_args([])
    assert args.databasename != BBSENGINE6_DBNAME_DEFAULT


@pytest.mark.unit
def test_explicit_databasename_still_wins(monkeypatch):
    monkeypatch.delenv("BBSENGINE6_DBNAME", raising=False)
    args = shell_main.buildargs(None).parse_args(["--databasename", "zoid6test"])
    assert args.databasename == "zoid6test"


@pytest.mark.unit
def test_environment_override_still_wins(monkeypatch):
    monkeypatch.setenv("BBSENGINE6_DBNAME", "zoid6test")
    args = shell_main.buildargs(None).parse_args([])
    assert args.databasename == "zoid6test"
