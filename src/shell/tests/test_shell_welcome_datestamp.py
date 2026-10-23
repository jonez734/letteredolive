"""The welcome line formats the last login with bbsengine6.util.datestamp().

bed reports the last login as an ISO-8601 string with an offset. The welcome line shows it as
a local datestamp (for example "2026-10-22 12:38pm EDT (Thu)"), never as the raw ISO text.
"""

from datetime import datetime
from unittest.mock import patch

import pytest

from shell import lib


def _echoed(fn, *a):
    with patch.object(lib.io, "echo") as echo:
        fn(*a)
    return " ".join(str(c.args[0]) for c in echo.call_args_list if c.args)


@pytest.mark.unit
def test_welcome_uses_util_datestamp_for_last_login():
    with patch.object(lib.util, "datestamp", return_value="STAMP") as ds:
        out = _echoed(lib._welcome, "jam", "2026-10-22T12:38:50.179783-04:00",
                      {"balance": 100, "source": "zoid6 bank"})
    ds.assert_called_once()
    assert "last login: STAMP" in out


@pytest.mark.unit
def test_welcome_shows_no_raw_iso_text():
    out = _echoed(lib._welcome, "jam", "2026-10-22T12:38:50.179783-04:00",
                  {"balance": 100, "source": "zoid6 bank"})
    assert "T12:38:50" not in out
    assert ".179783" not in out
    assert "last login: " in out


@pytest.mark.unit
def test_welcome_datestamp_is_in_local_time():
    # The instant 16:38 UTC is 12:38 EDT. The formatted local time must be the local clock time.
    out = _echoed(lib._welcome, "jam", "2026-10-22T16:38:50+00:00",
                  {"balance": 100, "source": "zoid6 bank"})
    from dateutil.tz import tzlocal

    local = lib.util.datestamp(datetime.fromisoformat("2026-10-22T16:38:50+00:00").astimezone(tzlocal()))
    assert f"last login: {local}" in out


@pytest.mark.unit
def test_first_login_still_says_never():
    out = _echoed(lib._welcome, "bob", None, {"balance": 100, "source": "bank"})
    assert "never (first login)" in out
    assert "datestamp" not in out


@pytest.mark.unit
def test_welcome_still_never_prints_password_or_token():
    out = _echoed(lib._welcome, "jam", "2026-10-22T12:38:50-04:00", {"balance": 1, "source": "bed"})
    assert "password" not in out.lower()
    assert "token" not in out.lower()
