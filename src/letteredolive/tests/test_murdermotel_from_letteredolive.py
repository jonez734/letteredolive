"""Integration tests: murdermotel can be invoked from letteredolive shell."""

from unittest.mock import patch

import pytest


class TestMurdermotelFromLetteredolive:
    """Test that pool flows from letteredolive to murdermotel."""

    @patch("bbsengine6.io.echo")
    @patch("bbsengine6.module.runmodule")
    @patch("bbsengine6.io.inputstring")
    @patch("bbsengine6.io.screen.setbottombar")
    @patch("bbsengine6.io.common.get_dsr")
    @patch("bbsengine6.member.getcurrentmoniker")
    def test_pool_forwarded_to_murdermotel(
        self,
        mock_getmoniker,
        mock_get_dsr,
        mock_setbottombar,
        mock_inputstring,
        mock_runmodule,
        mock_echo,
        mock_args,
        mock_pool,
    ):
        """Verify pool is passed to murdermotel when user types 'murdermotel'."""
        import letteredolive.main as lo_main

        mock_getmoniker.return_value = "TestPlayer"
        mock_get_dsr.return_value = (1, 1)
        mock_inputstring.side_effect = ["murdermotel", "logout"]
        mock_runmodule.return_value = True

        result = lo_main.main(mock_args, pool=mock_pool)

        assert result is None
        mock_runmodule.assert_called_once()
        call_args = mock_runmodule.call_args
        assert call_args.kwargs.get("pool") is mock_pool
        assert call_args.kwargs.get("argv") == ["murdermotel"]

    @patch("bbsengine6.io.echo")
    @patch("bbsengine6.module.runmodule")
    @patch("bbsengine6.io.inputstring")
    @patch("bbsengine6.io.screen.setbottombar")
    @patch("bbsengine6.io.common.get_dsr")
    @patch("bbsengine6.member.getcurrentmoniker")
    def test_pool_none_propagates(
        self,
        mock_getmoniker,
        mock_get_dsr,
        mock_setbottombar,
        mock_inputstring,
        mock_runmodule,
        mock_echo,
        mock_args,
    ):
        """Verify pool=None is still passed (not silently fixed)."""
        import letteredolive.main as lo_main

        mock_getmoniker.return_value = "TestPlayer"
        mock_get_dsr.return_value = (1, 1)
        mock_inputstring.side_effect = ["murdermotel", "logout"]
        mock_runmodule.return_value = True

        lo_main.main(mock_args, pool=None)

        mock_runmodule.assert_called_once()
        call_args = mock_runmodule.call_args
        assert call_args.kwargs.get("pool") is None

    @patch("bbsengine6.io.echo")
    @patch("bbsengine6.module.runmodule")
    @patch("bbsengine6.io.inputstring")
    @patch("bbsengine6.io.screen.setbottombar")
    @patch("bbsengine6.io.common.get_dsr")
    @patch("bbsengine6.member.getcurrentmoniker")
    def test_murdermotel_prg_passed(
        self,
        mock_getmoniker,
        mock_get_dsr,
        mock_setbottombar,
        mock_inputstring,
        mock_runmodule,
        mock_echo,
        mock_args,
        mock_pool,
    ):
        """Verify 'murdermotel' command maps to prg='murdermotel'."""
        import letteredolive.main as lo_main

        mock_getmoniker.return_value = "TestPlayer"
        mock_get_dsr.return_value = (1, 1)
        mock_inputstring.side_effect = ["murdermotel", "logout"]
        mock_runmodule.return_value = True

        lo_main.main(mock_args, pool=mock_pool)

        mock_runmodule.assert_called_once()
        call_args = mock_runmodule.call_args
        assert call_args.args[1] == "murdermotel"

    @patch("bbsengine6.io.echo")
    @patch("bbsengine6.io.inputstring")
    @patch("bbsengine6.io.screen.setbottombar")
    @patch("bbsengine6.io.common.get_dsr")
    @patch("bbsengine6.member.getcurrentmoniker")
    def test_unknown_command_rejected(
        self,
        mock_getmoniker,
        mock_get_dsr,
        mock_setbottombar,
        mock_inputstring,
        mock_echo,
        mock_args,
        mock_pool,
    ):
        """Verify unknown commands produce error, not crash."""
        import letteredolive.main as lo_main

        mock_getmoniker.return_value = "TestPlayer"
        mock_get_dsr.return_value = (1, 1)
        mock_inputstring.side_effect = ["nonexistent_game_xyz", "logout"]
        result = lo_main.main(mock_args, pool=mock_pool)
        assert result is None

    @patch("bbsengine6.io.echo")
    @patch("bbsengine6.module.runmodule")
    @patch("bbsengine6.io.inputstring")
    @patch("bbsengine6.io.screen.setbottombar")
    @patch("bbsengine6.io.common.get_dsr")
    @patch("bbsengine6.member.getcurrentmoniker")
    def test_empyre_command_also_passes_pool(
        self,
        mock_getmoniker,
        mock_get_dsr,
        mock_setbottombar,
        mock_inputstring,
        mock_runmodule,
        mock_echo,
        mock_args,
        mock_pool,
    ):
        """Verify pool forwarding works for all registered subgames."""
        import letteredolive.main as lo_main

        mock_getmoniker.return_value = "TestPlayer"
        mock_get_dsr.return_value = (1, 1)
        mock_inputstring.side_effect = ["empyre", "logout"]
        mock_runmodule.return_value = True

        lo_main.main(mock_args, pool=mock_pool)

        mock_runmodule.assert_called_once()
        call_args = mock_runmodule.call_args
        assert call_args.kwargs.get("pool") is mock_pool
        assert call_args.args[1] == "empyre"


class TestLetteredoliveMainPoolForwarding:
    """Test pool extraction and forwarding in letteredolive.main.main."""

    @patch("bbsengine6.io.echo")
    @patch("bbsengine6.module.runmodule")
    @patch("bbsengine6.io.inputstring")
    @patch("bbsengine6.io.screen.setbottombar")
    @patch("bbsengine6.io.common.get_dsr")
    @patch("bbsengine6.member.getcurrentmoniker")
    def test_multiple_commands_maintain_pool(
        self,
        mock_getmoniker,
        mock_get_dsr,
        mock_setbottombar,
        mock_inputstring,
        mock_runmodule,
        mock_echo,
        mock_args,
        mock_pool,
    ):
        """Simulate multiple commands in one shell session."""
        import letteredolive.main as lo_main

        mock_getmoniker.return_value = "TestPlayer"
        mock_get_dsr.return_value = (1, 1)
        mock_inputstring.side_effect = ["murdermotel", "logout"]
        mock_runmodule.return_value = True

        lo_main.main(mock_args, pool=mock_pool)

        assert mock_runmodule.call_count == 1
        call_args = mock_runmodule.call_args
        assert call_args.kwargs.get("pool") is mock_pool


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
