"""letteredolive packaging metadata: a pyproject.toml with an SPDX license, no deprecated classifier, and
no setup.py-only fields. Building must not emit the setuptools deprecation warnings."""

import pathlib
import tomllib

import pytest

SRC = pathlib.Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_pyproject_exists_with_a_build_system():
    data = tomllib.loads((SRC / "pyproject.toml").read_text())
    assert data["build-system"]["build-backend"] == "setuptools.build_meta"


@pytest.mark.unit
def test_license_is_an_spdx_expression_not_a_classifier():
    data = tomllib.loads((SRC / "pyproject.toml").read_text())
    assert data["project"]["license"] == "GPL-2.0-or-later"
    assert not any(c.startswith("License ::") for c in data["project"]["classifiers"])


@pytest.mark.unit
def test_scripts_and_dependencies_are_declared():
    data = tomllib.loads((SRC / "pyproject.toml").read_text())
    scripts = data["tool"]["setuptools"]["script-files"]
    assert sorted(s.rsplit("/", 1)[-1] for s in scripts) == ["bbs", "letteredolive", "shell"]
    assert set(data["project"]["dependencies"]) == {"bbsengine6", "bed"}


@pytest.mark.unit
def test_setup_py_is_a_shim_with_no_metadata():
    text = (SRC / "setup.py").read_text()
    assert "setup(" not in text or "name=" not in text, "metadata must live in pyproject.toml"


@pytest.mark.unit
@pytest.mark.parametrize("project", ["bbsengine6/py", "bed"])
def test_sibling_projects_declare_the_same_license(project):
    """All zoid6-family projects are GPL-2.0-or-later; a drift would make the packages disagree."""
    meta_root = SRC.parents[1]
    path = meta_root / project / "pyproject.toml"
    if not path.exists():
        path = meta_root / project / "src" / "pyproject.toml"
    data = tomllib.loads(path.read_text())
    assert data["project"]["license"] == "GPL-2.0-or-later", path
