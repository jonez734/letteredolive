"""The shell detects that it was started as a login shell (argv[0] begins with a dash).

A login shell shows one idle message that never mentions `shell`. A shell started from bash shows the
line that names `shell --login`.
"""

import importlib

import pytest

lib = importlib.import_module("shell.lib")


@pytest.mark.unit
@pytest.mark.parametrize("argv0", ["-letteredolive", "-/usr/bin/letteredolive", "-shell"])
def test_dash_prefixed_argv0_is_a_login_shell(argv0):
    assert lib.is_login_shell([argv0]) is True


@pytest.mark.unit
@pytest.mark.parametrize("argv0", ["letteredolive", "/usr/bin/letteredolive", "shell", ""])
def test_plain_argv0_is_not_a_login_shell(argv0):
    assert lib.is_login_shell([argv0]) is False


@pytest.mark.unit
def test_no_argv_is_not_a_login_shell():
    assert lib.is_login_shell([]) is False
