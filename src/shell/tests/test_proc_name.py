"""The shell's process name comes from the launcher, not from exec -a.

exec -a set argv[0] to the launcher path, and Python then found the wrong venv (sys.prefix fell
back to /usr). The launcher now runs the venv's python directly and passes its own name as
--proc-name. The shell sets the kernel name (what ps shows) with prctl on Linux only, and treats a
leading dash as a login session.
"""

import pathlib
import re
from unittest.mock import patch

import pytest

from shell import lib

ROOT = pathlib.Path(__file__).resolve().parents[3]
LAUNCHERS = [ROOT / "bin" / "letteredolive", ROOT / "bin" / "shell", ROOT / "bin" / "bbs"]


@pytest.mark.unit
@pytest.mark.parametrize("path", LAUNCHERS, ids=lambda p: p.name)
def test_launcher_does_not_use_exec_a(path):
    assert "exec -a" not in path.read_text(), path


@pytest.mark.unit
@pytest.mark.parametrize("path", LAUNCHERS, ids=lambda p: p.name)
def test_launcher_passes_its_name_as_proc_name(path):
    assert re.search(r'--proc-name\s+"\$0"', path.read_text()), path


@pytest.mark.unit
@pytest.mark.parametrize("path", LAUNCHERS, ids=lambda p: p.name)
def test_launcher_runs_the_venv_python_by_path(path):
    assert re.search(r"exec\s+/var/lib/zoid6/venv/bin/python\b", path.read_text()), path


@pytest.mark.unit
def test_leading_dash_in_proc_name_marks_a_login_session():
    assert lib.is_login_shell(["-letteredolive"]) is True
    assert lib.is_login_shell(["letteredolive"]) is False


@pytest.mark.unit
def test_set_proc_name_truncates_to_the_kernel_limit():
    captured = {}

    class _Libc:
        def prctl(self, option, arg, *rest):
            captured["option"] = option
            captured["name"] = arg
            return 0

    with patch.object(lib.sys, "platform", "linux"), \
         patch.object(lib, "_load_libc", return_value=_Libc()):
        lib.set_proc_name("-letteredolive-and-more-than-fifteen")
    assert captured["option"] == 15  # PR_SET_NAME
    assert len(captured["name"]) <= 15


@pytest.mark.unit
def test_set_proc_name_is_not_called_off_linux():
    with patch.object(lib.sys, "platform", "darwin"), \
         patch.object(lib, "_load_libc") as load:
        lib.set_proc_name("letteredolive")
    load.assert_not_called()


@pytest.mark.unit
def test_set_proc_name_survives_a_missing_libc():
    with patch.object(lib.sys, "platform", "linux"), \
         patch.object(lib, "_load_libc", side_effect=OSError("no libc")):
        lib.set_proc_name("letteredolive")
