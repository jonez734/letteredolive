"""The shell's buildargs must match bbsengine6's module signature.

bbsengine6's module loader rejects a buildargs whose ``args`` parameter has a
default. The reference is ``buildargs(args, **kwargs)``.
"""

import inspect
import importlib

import pytest

MODULES = ["shell.main", "shell.__main__", "shell.module", "shell"]


@pytest.mark.unit
@pytest.mark.parametrize("name", MODULES)
def test_buildargs_args_has_no_default(name):
    mod = importlib.import_module(name)
    sig = inspect.signature(mod.buildargs)
    assert sig.parameters["args"].default is inspect.Parameter.empty, name


@pytest.mark.unit
def test_entry_point_main_builds_its_parser_without_arguments():
    import inspect
    import shell.__main__ as entry
    src = inspect.getsource(entry.main)
    # main() has no args of its own; it must hand buildargs an args value.
    assert "parser = buildargs()" not in src
    assert "buildargs(" in src


@pytest.mark.unit
def test_gate_refusal_exits_1_without_terminal_queries(capsys):
    from unittest.mock import MagicMock, patch
    import shell.__main__ as entry
    with patch.object(entry, "buildargs") as b, \
         patch.object(entry.database, "getpool") as gp, \
         patch.object(entry.lib, "shell_login", return_value=None), \
         patch.object(entry.io, "terminal") as term, \
         patch.object(entry.io, "echo") as echo:
        b.return_value.parse_args.return_value = MagicMock()
        with pytest.raises(SystemExit) as ex:
            entry.main()
    assert ex.value.code == 1
    term.height.assert_not_called()
    assert not any("savecursor" in str(c.args[0]) for c in echo.call_args_list)
