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


@pytest.mark.unit
def test_prod_does_not_depend_on_the_user_venv():
    """Under sudo HOME is /root, so prod must not run $(HOME)/.venv/bin/python (build does)."""
    r = subprocess.run(["make", "-n", "-C", str(ROOT), "prod", "HOME=/root"],
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    assert "/root/.venv" not in r.stdout
    assert "/.venv/bin/python" not in r.stdout


@pytest.mark.unit
def test_prod_builds_with_the_system_python():
    r = subprocess.run(["make", "-n", "-C", str(ROOT), "prod"], capture_output=True, text=True, timeout=60)
    setup_lines = [l for l in r.stdout.splitlines() if "setup.py" in l]
    assert setup_lines, "prod must build the wheel"
    assert all("/usr/bin/python3" in l for l in setup_lines), setup_lines


@pytest.mark.unit
def test_prod_checks_root_before_building():
    r = subprocess.run(["make", "-n", "-C", str(ROOT), "prod"], capture_output=True, text=True, timeout=60)
    lines = r.stdout.splitlines()
    root_line = next(i for i, l in enumerate(lines) if "id -u" in l)
    build_line = next(i for i, l in enumerate(lines) if "setup.py" in l)
    assert root_line < build_line, "the root guard must run before any build step"


@pytest.mark.unit
def test_prod_builds_with_python_312_not_the_default_python3():
    """bbsengine6 requires <3.13, so prod must build with /usr/bin/python3.12 explicitly."""
    r = subprocess.run(["make", "-n", "-C", str(ROOT), "prod"], capture_output=True, text=True, timeout=60)
    setup_lines = [l for l in r.stdout.splitlines() if "setup.py" in l]
    assert setup_lines, "prod must build the wheel"
    assert all("/usr/bin/python3.12" in l for l in setup_lines), setup_lines
    assert "/usr/bin/python3 " not in r.stdout
