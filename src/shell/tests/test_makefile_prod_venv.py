"""letteredolive's Makefile: `venv` and `prod` install into the prefix (DEPLOY_PREFIX, default zoid6).

`prod` must be root-only, must not create the venv, must not use --break-system-packages, and must write
the three launchers with the prefix's interpreter. `venv` keeps installing into $(HOME)/.venv.
"""

import pathlib
import re
import subprocess

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[3]


def _dry(target, *extra):
    cmd = ["make", "-n", "-C", str(ROOT), target, *extra]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=60)


@pytest.mark.unit
def test_default_prefix_is_the_zoid6_venv():
    r = _dry("prod")
    assert r.returncode == 0, r.stderr
    assert "/var/lib/zoid6/venv" in r.stdout


@pytest.mark.unit
def test_prefix_is_taken_from_deploy_prefix():
    r = _dry("prod", "DEPLOY_PREFIX=/var/lib/other/venv")
    assert r.returncode == 0, r.stderr
    assert "/var/lib/other/venv" in r.stdout
    assert "/var/lib/zoid6/venv" not in r.stdout


@pytest.mark.unit
def test_prod_never_creates_the_venv():
    # The only mention of `-m venv` is the hint printed when the venv is missing; no executed command.
    r = _dry("prod")
    executed = [line for line in r.stdout.splitlines() if "-m venv" in line and "echo" not in line]
    assert executed == [], executed


@pytest.mark.unit
def test_prod_never_breaks_system_packages():
    r = _dry("prod")
    assert "--break-system-packages" not in r.stdout


@pytest.mark.unit
def test_prod_is_root_only():
    text = (ROOT / "Makefile").read_text()
    assert re.search(r"id -u", text), "prod must check for root"


@pytest.mark.unit
def test_venv_keeps_installing_to_home():
    r = _dry("venv")
    assert r.returncode == 0, r.stderr
    assert "$(HOME)" not in r.stdout
    assert "/.venv/" in r.stdout or ".venv" in r.stdout


@pytest.mark.unit
def test_prod_writes_launchers_with_the_prefix_interpreter():
    r = _dry("prod")
    assert "/bin/python" in r.stdout
    assert "exec -a" in r.stdout
