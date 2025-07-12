# test_bot.py
# This file contains unit tests for the Discord bot commands
# It uses Python's unittest framework with async support for testing Discord.py commands

import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import discord

from bot import bot, run_bot  # Import the bot instance directly


class TestCSClubBot(unittest.IsolatedAsyncioTestCase):
    """Test suite for the CS Club Discord Bot commands"""

    async def asyncSetUp(self):
        """Set up test fixtures before each test method
        Creates a mock context that simulates Discord's message context"""
        self.ctx = MagicMock()
        self.ctx.send = AsyncMock()  # Mock the send method to test message sending
        bot.loop = asyncio.get_running_loop()

    async def test_help_command(self):
        """Test the !help command
        Verifies that:
        1. The command responds with a message
        2. The response includes information about the !resume command"""
        await bot.get_command("help").callback(self.ctx)
        self.ctx.send.assert_called()
        self.assertIn("!resume", self.ctx.send.call_args[0][0])

    async def test_resume_command(self):
        """Test the !resume command
        Verifies that the command returns the correct engineering resume resources URL
        """
        await bot.get_command("resume").callback(self.ctx)
        self.ctx.send.assert_called_with(
            "📄 Resume Resources: https://www.reddit.com/r/EngineeringResumes/wiki/index/"
        )

    async def test_events_command(self):
        """Test the !events command
        Verifies that:
        1. The command responds with a message
        2. The response includes information about the Git Workshop"""
        await bot.get_command("events").callback(self.ctx)
        self.ctx.send.assert_called()
        self.assertIn("Git Workshop", self.ctx.send.call_args[0][0])

    async def test_resources_command(self):
        """Test the !resources command
        Verifies that:
        1. The command responds with a message
        2. The response includes FreeCodeCamp in the learning resources"""
        await bot.get_command("resources").callback(self.ctx)
        self.ctx.send.assert_called()
        self.assertIn("FreeCodeCamp", self.ctx.send.call_args[0][0])

    @patch("bot.load_dotenv", return_value=False)
    def test_no_env(self, mock_load_dotenv):
        """Test if there is no environment file"""
        with self.assertRaises(SystemExit) as cm:
            run_bot()
        self.assertEqual(cm.exception.code, 1)

    @patch(
        "os.getenv", side_effect=lambda key: "" if key == "DISCORD_BOT_TOKEN" else None
    )
    @patch("bot.load_dotenv", return_value=True)
    def test_env_with_empty_token(self, mock_load_dotenv, mock_getenv):
        """Test if .env is found but DISCORD_BOT_TOKEN is empty"""
        with self.assertRaises(AssertionError) as cm:
            run_bot()
        self.assertIn("DISCORD_BOT_TOKEN can not be empty", str(cm.exception))

    @patch("bot.bot.run", side_effect=discord.LoginFailure("invalid_token"))
    @patch("os.getenv", return_value="invalid_token")
    @patch("bot.load_dotenv", return_value=True)
    @patch("sys.exit")
    def test_env_with_invalid_token(
        self, mock_exit, mock_load_dotenv, mock_getenv, mock_bot_run
    ):
        """Test if .env is found and DISCORD_BOT_TOKEN is invalid"""
        run_bot()
        mock_bot_run.assert_called_once_with("invalid_token")
        mock_exit.assert_called_once_with(1)

    @patch("bot.bot.run")
    @patch(
        "os.getenv",
        side_effect=lambda key: "valid_token" if key == "DISCORD_BOT_TOKEN" else None,
    )
    @patch("bot.load_dotenv", return_value=True)
    def test_env_with_token_success(self, mock_load_dotenv, mock_getenv, mock_bot_run):
        """Test if .env is found and DISCORD_BOT_TOKEN is valid"""
        run_bot()
        mock_bot_run.assert_called_once_with("valid_token")

    async def test_on_member_join_success(self):
        """Test on_member_join event sends welcome message successfully."""
        mock_member = MagicMock(spec=discord.Member)
        mock_member.mention = "<@12345>"
        mock_member.display_name = "TestUser"
        mock_member.guild = MagicMock(spec=discord.Guild)
        mock_member.guild.name = "Test Server"
        mock_member.guild.system_channel = None
        mock_member.send = AsyncMock()

        mock_welcome_channel = MagicMock(spec=discord.TextChannel)
        mock_welcome_channel.name = "welcome"
        mock_welcome_channel.send = AsyncMock()

        mock_networking_channel = MagicMock(spec=discord.TextChannel)
        mock_networking_channel.name = "networking"
        mock_networking_channel.id = "67890"

        mock_member.guild.text_channels = [
            mock_welcome_channel,
            mock_networking_channel,
        ]

        bot.dispatch("member_join", mock_member)
        await asyncio.sleep(0)

        expected_message = f"Welcome to **Test Server**, {mock_member.mention}! Feel free to introduce yourself in <#{mock_networking_channel.id}>"  # noqa: E501
        mock_welcome_channel.send.assert_called_once_with(expected_message)
        mock_member.send.assert_not_called()

    async def test_on_member_join_no_networking_channel(self):
        """Test on_member_join when no networking channel is found."""
        mock_member = MagicMock(spec=discord.Member)
        mock_member.mention = "<@12345>"
        mock_member.display_name = "TestUser"
        mock_member.guild = MagicMock(spec=discord.Guild)
        mock_member.guild.name = "Test Server"

        mock_welcome_channel = MagicMock(spec=discord.TextChannel)
        mock_welcome_channel.name = "welcome"
        mock_welcome_channel.send = AsyncMock()

        mock_member.guild.text_channels = [mock_welcome_channel]
        mock_member.guild.system_channel = None

        bot.dispatch("member_join", mock_member)
        await asyncio.sleep(0)

        expected_message = f"Welcome to **Test Server**, {mock_member.mention}! Feel free to introduce yourself in #networking"  # noqa: E501
        mock_welcome_channel.send.assert_called_once_with(expected_message)

    async def test_on_member_join_fallback_to_general(self):
        """Test on_member_join falls back to 'general' channel."""
        mock_member = MagicMock(spec=discord.Member)
        mock_member.mention = "<@12345>"
        mock_member.display_name = "TestUser"
        mock_member.guild = MagicMock(spec=discord.Guild)
        mock_member.guild.name = "Test Server"

        mock_general_channel = MagicMock(spec=discord.TextChannel)
        mock_general_channel.name = "general"
        mock_general_channel.send = AsyncMock()

        mock_member.guild.text_channels = [mock_general_channel]
        mock_member.guild.system_channel = None

        bot.dispatch("member_join", mock_member)
        await asyncio.sleep(0)

        mock_general_channel.send.assert_called_once()

    async def test_on_member_join_fallback_to_system_channel(self):
        """Test on_member_join falls back to system channel."""
        mock_member = MagicMock(spec=discord.Member)
        mock_member.display_name = "TestUser"
        mock_member.guild = MagicMock(spec=discord.Guild)

        mock_system_channel = MagicMock(spec=discord.TextChannel)
        mock_system_channel.send = AsyncMock()

        mock_member.guild.text_channels = []
        mock_member.guild.system_channel = mock_system_channel

        bot.dispatch("member_join", mock_member)
        await asyncio.sleep(0)

        mock_system_channel.send.assert_called_once()

    async def test_on_member_join_fallback_to_first_channel(self):
        """Test on_member_join falls back to the first available text channel."""
        mock_member = MagicMock(spec=discord.Member)
        mock_member.display_name = "TestUser"
        mock_member.guild = MagicMock(spec=discord.Guild)

        mock_first_channel = MagicMock(spec=discord.TextChannel)
        mock_first_channel.name = "random"
        mock_first_channel.send = AsyncMock()

        mock_member.guild.text_channels = [mock_first_channel]
        mock_member.guild.system_channel = None

        bot.dispatch("member_join", mock_member)
        await asyncio.sleep(0)

        mock_first_channel.send.assert_called_once()

    async def test_on_member_join_no_channels_fallback_to_dm(self):
        """Test on_member_join falls back to DM when no channels are available."""
        mock_member = MagicMock(spec=discord.Member)
        mock_member.display_name = "TestUser"
        mock_member.guild = MagicMock(spec=discord.Guild)
        mock_member.guild.name = "Test Server"
        mock_member.send = AsyncMock()

        mock_member.guild.text_channels = []
        mock_member.guild.system_channel = None

        bot.dispatch("member_join", mock_member)
        await asyncio.sleep(0)

        mock_member.send.assert_called_once()
        expected_dm = (
            f"🎉 Welcome to **{mock_member.guild.name}**!\n\n"
            f"I'm BugBot! Type `!help` in any channel to see what I can do. 🤖"
        )
        mock_member.send.assert_called_with(expected_dm)

    @patch("builtins.print")
    async def test_on_member_join_forbidden(self, mock_print):
        """Test on_member_join handles discord.Forbidden exception."""
        mock_member = MagicMock(spec=discord.Member)
        mock_member.display_name = "TestUser"
        mock_member.guild = MagicMock(spec=discord.Guild)

        mock_welcome_channel = MagicMock(spec=discord.TextChannel)
        mock_welcome_channel.name = "welcome"
        mock_welcome_channel.send = AsyncMock(
            side_effect=discord.Forbidden(MagicMock(), "missing permissions")
        )

        mock_member.guild.text_channels = [mock_welcome_channel]
        mock_member.guild.system_channel = None

        bot.dispatch("member_join", mock_member)
        await asyncio.sleep(0)

        mock_print.assert_any_call(
            f"❌ Could not send welcome message for {mock_member.display_name} - missing permissions"  # noqa: E501
        )

    @patch("builtins.print")
    async def test_on_member_join_exception(self, mock_print):
        """Test on_member_join handles generic Exception."""
        mock_member = MagicMock(spec=discord.Member)
        mock_member.display_name = "TestUser"
        mock_member.guild = MagicMock(spec=discord.Guild)

        mock_welcome_channel = MagicMock(spec=discord.TextChannel)
        mock_welcome_channel.name = "welcome"
        mock_welcome_channel.send = AsyncMock(side_effect=Exception("Test error"))

        mock_member.guild.text_channels = [mock_welcome_channel]
        mock_member.guild.system_channel = None

        bot.dispatch("member_join", mock_member)
        await asyncio.sleep(0)

        mock_print.assert_any_call(
            f"❌ Error sending welcome message for {mock_member.display_name}: Test error"  # noqa: E501
        )


if __name__ == "__main__":
    # Run the tests when the file is executed directly
    unittest.main(verbosity=2)
