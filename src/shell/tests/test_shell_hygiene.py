"""Hygiene: no editor backups in the tree, and the unit marker is registered."""

from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_no_editor_backup_files_in_source_tree():
    backups = [p for p in SRC.rglob("*~") if ".git" not in p.parts]
    assert backups == [], f"remove editor backups: {backups}"


@pytest.mark.unit
def test_unit_marker_is_registered():
    cfg = (SRC / "pytest.ini").read_text()
    assert "markers" in cfg and "unit:" in cfg
