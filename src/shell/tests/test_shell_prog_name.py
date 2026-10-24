"""The shell's usage line names the command it was started as (letteredolive, shell, or bbs).

argv[0] for a launched command is the launcher's name, so the parser's prog comes from the process
name, falling back to letteredolive when that is not available.
"""

import importlib
from unittest.mock import patch

import pytest

main_mod = importlib.import_module("shell.__main__")


@pytest.mark.unit
@pytest.mark.parametrize("name", ["letteredolive", "shell", "bbs"])
def test_usage_names_the_command_it_was_started_as(name):
    with patch.object(main_mod.lib, "process_argv0", return_value=f"-{name}"):
        assert main_mod.prog_name() == name


@pytest.mark.unit
def test_prog_name_falls_back_to_letteredolive():
    with patch.object(main_mod.lib, "process_argv0", return_value=""):
        assert main_mod.prog_name() == "letteredolive"
