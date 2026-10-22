"""The shell must not call bbsengine6.screen, which is a deprecated back-compat shim."""

import ast
from pathlib import Path

import pytest

SHELL = Path(__file__).resolve().parents[1]


@pytest.mark.unit
def test_shell_does_not_import_or_call_screen():
    offenders = []
    for path in SHELL.glob("*.py"):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module == "bbsengine6" and any(a.name == "screen" for a in node.names):
                offenders.append(f"{path.name}: from bbsengine6 import screen")
            if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "screen":
                offenders.append(f"{path.name}:{node.lineno}: screen.{node.attr}")
    assert offenders == [], offenders
