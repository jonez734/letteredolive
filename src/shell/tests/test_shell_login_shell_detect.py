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


@pytest.mark.unit
def test_process_name_comes_from_proc_name_not_proc(monkeypatch):
    # The launcher passes its own name as --proc-name. The shell reads it from there, so a login
    # session is detected without relying on /proc/self/cmdline.
    from shell import lib
    monkeypatch.setattr(lib, "_PROC_NAME", "-letteredolive")
    assert lib.process_name() == "-letteredolive"
    assert lib.is_login_shell_process() is True
    monkeypatch.setattr(lib, "_PROC_NAME", "letteredolive")
    assert lib.is_login_shell_process() is False


@pytest.mark.unit
def test_process_argv0_falls_back_to_sys_argv(monkeypatch):
    monkeypatch.setattr("builtins.open", lambda *a, **k: (_ for _ in ()).throw(OSError("no proc")))
    monkeypatch.setattr("sys.argv", ["-letteredolive"])
    assert lib.process_argv0() == "-letteredolive"
