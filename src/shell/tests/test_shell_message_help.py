"""`message --help` (or -h) prints the usage and sends nothing."""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from shell import lib


def _args():
    return SimpleNamespace(debug=False, token_file="/tmp/none.token", bed_host="127.0.0.1",
                           bed_port=8765, bed_probe_timeout=0.25)


@pytest.mark.unit
@pytest.mark.parametrize("flag", ["--help", "-h"])
def test_help_prints_usage_and_returns_true(flag):
    client = MagicMock()
    with patch.object(lib, "_message_client", return_value=client), patch.object(lib.io, "echo") as echo:
        assert lib.run_message(_args(), ["message", flag]) is True
    client.send_message.assert_not_called()
    text = " ".join(str(c.args[0]) for c in echo.call_args_list if c.args)
    assert "usage: message --to" in text
    assert "--body" in text


@pytest.mark.unit
def test_help_is_listed_for_the_command():
    assert "--help" in lib.commands["message"]["help"] or "usage" in lib.commands["message"]["help"]
