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
