# test_bot.py
# This file contains unit tests for the Discord bot commands
# It uses Python's unittest framework with async support for testing Discord.py commands

import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from bot import bot, run_bot  # Import the bot instance directly
import discord


class TestCSClubBot(unittest.IsolatedAsyncioTestCase):
    """Test suite for the CS Club Discord Bot commands"""

    async def asyncSetUp(self):
        """Set up test fixtures before each test method
        Creates a mock context that simulates Discord's message context"""
        self.ctx = MagicMock()
        self.ctx.send = AsyncMock()  # Mock the send method to test message sending

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


if __name__ == "__main__":
    # Run the tests when the file is executed directly
    unittest.main(verbosity=2)
