"""The letteredolive build version comes from the shared next_version.sh, not a minute clock.

Every project uses <prefix>YYYYMMDDHHMMSS (14-digit UTC, per build). A minute-resolution
VERSION lets two builds in one minute share a name, which is what this guards against.
"""

import pathlib
import re

import pytest

MAKEFILE = pathlib.Path(__file__).resolve().parents[3] / "Makefile"


@pytest.mark.unit
def test_makefile_version_calls_shared_next_version_script():
    text = MAKEFILE.read_text()
    assert "next_version.sh" in text


@pytest.mark.unit
def test_makefile_version_is_not_minute_resolution():
    text = MAKEFILE.read_text()
    assert not re.search(r"VERSION\s*=\s*0\.0\.0\.dev\$\(shell date \+%Y%m%d%H%M\)", text)


@pytest.mark.unit
def test_makefile_keeps_the_dev_prefix():
    text = MAKEFILE.read_text()
    assert "0.0.0.dev" in text
