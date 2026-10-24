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
def test_process_argv0_is_read_from_proc_when_available(monkeypatch, tmp_path):
    # python -m replaces sys.argv[0] with the module path, so the process name (set by exec -a) is
    # read from /proc/self/cmdline instead.
    cmdline = tmp_path / "cmdline"
    cmdline.write_bytes(b"-letteredolive\0--databaseport=5432\0")
    real_open = open

    def fake_open(path, *a, **k):
        if str(path) == "/proc/self/cmdline":
            return real_open(cmdline, *a, **k)
        return real_open(path, *a, **k)

    monkeypatch.setattr("builtins.open", fake_open)
    assert lib.process_argv0() == "-letteredolive"
    assert lib.is_login_shell_process() is True


@pytest.mark.unit
def test_process_argv0_falls_back_to_sys_argv(monkeypatch):
    monkeypatch.setattr("builtins.open", lambda *a, **k: (_ for _ in ()).throw(OSError("no proc")))
    monkeypatch.setattr("sys.argv", ["-letteredolive"])
    assert lib.process_argv0() == "-letteredolive"
