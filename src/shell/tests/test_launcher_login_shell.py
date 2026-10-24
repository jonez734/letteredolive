"""The three launchers (letteredolive, shell, bbs) start the shell package with argv[0] kept.

A login shell is started with a leading dash on argv[0]. Each launcher must exec python so that name
reaches the process, and must run the shell package, not an old module name.
"""

import pathlib

import pytest

BIN = pathlib.Path(__file__).resolve().parents[3] / "bin"
LAUNCHERS = ["letteredolive", "shell", "bbs"]


@pytest.mark.unit
@pytest.mark.parametrize("name", LAUNCHERS)
def test_launcher_execs_python_with_argv0_kept(name):
    text = (BIN / name).read_text()
    assert 'exec -a "$0" python3' in text, f"{name} must exec with its own argv[0]"


@pytest.mark.unit
@pytest.mark.parametrize("name", LAUNCHERS)
def test_launcher_runs_the_shell_package(name):
    text = (BIN / name).read_text()
    assert "-m shell" in text, f"{name} must run the shell package"
    assert "-m letteredolive" not in text, f"{name} must not name the old module"


@pytest.mark.unit
@pytest.mark.parametrize("name", LAUNCHERS)
def test_launchers_are_identical_apart_from_name(name):
    base = (BIN / "letteredolive").read_text()
    assert (BIN / name).read_text() == base
