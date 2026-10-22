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
