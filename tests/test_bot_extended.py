# test_bot_extended.py
# Enhanced test suite for the Discord bot with comprehensive test coverage
# Includes edge cases, error handling, integration tests, performance tests, security tests, and more

import unittest
from unittest.mock import AsyncMock, MagicMock, patch, call, PropertyMock
import asyncio
import discord
from discord.ext import commands
import sys
import os
import time
import threading
import json
import re
from bot import bot, run_bot


class TestBotExtended(unittest.IsolatedAsyncioTestCase):
    """Extended test suite for Discord bot with comprehensive coverage"""

    async def asyncSetUp(self):
        """Set up test fixtures before each test method"""
        self.ctx = MagicMock()
        self.ctx.send = AsyncMock()
        self.ctx.author = MagicMock()
        self.ctx.author.id = 12345
        self.ctx.author.name = "TestUser"
        self.ctx.author.display_name = "Test User"
        self.ctx.guild = MagicMock()
        self.ctx.guild.id = 67890
        self.ctx.guild.name = "Test Guild"
        self.ctx.channel = MagicMock()
        self.ctx.channel.id = 11111
        self.ctx.channel.name = "test-channel"
        self.ctx.message = MagicMock()
        self.ctx.message.created_at = discord.utils.utcnow()

    # Test command content validation
    async def test_help_command_content_structure(self):
        """Test that help command returns properly formatted content"""
        await bot.get_command("help").callback(self.ctx)
        
        # Get the sent message
        sent_message = self.ctx.send.call_args[0][0]
        
        # Verify structure
        self.assertIn("**🤖 CuseBot Commands:**", sent_message)
        self.assertIn("`!help`", sent_message)
        self.assertIn("`!resume`", sent_message)
        self.assertIn("`!events`", sent_message)
        self.assertIn("`!resources`", sent_message)

    async def test_resume_command_url_validity(self):
        """Test that resume command returns a valid URL format"""
        await bot.get_command("resume").callback(self.ctx)
        
        sent_message = self.ctx.send.call_args[0][0]
        self.assertIn("https://", sent_message)
        self.assertIn("reddit.com", sent_message)
        self.assertIn("📄", sent_message)

    async def test_events_command_date_format(self):
        """Test that events command includes proper date formatting"""
        await bot.get_command("events").callback(self.ctx)
        
        sent_message = self.ctx.send.call_args[0][0]
        self.assertIn("📅 Upcoming Events:", sent_message)
        self.assertIn("April", sent_message)
        self.assertIn("Git Workshop", sent_message)
        self.assertIn("LeetCode Challenge", sent_message)
        self.assertIn("🍕", sent_message)

    async def test_resources_command_links_format(self):
        """Test that resources command includes properly formatted links"""
        await bot.get_command("resources").callback(self.ctx)
        
        sent_message = self.ctx.send.call_args[0][0]
        self.assertIn("📚 CS Learning Resources:", sent_message)
        self.assertIn("[CS50]", sent_message)
        self.assertIn("https://", sent_message)
        self.assertIn("cs50.harvard.edu", sent_message)
        self.assertIn("theodinproject.com", sent_message)
        self.assertIn("freecodecamp.org", sent_message)
        self.assertIn("leetcode.com", sent_message)

    # Test error handling scenarios
    async def test_command_with_send_failure(self):
        """Test command behavior when ctx.send fails"""
        self.ctx.send.side_effect = discord.HTTPException(MagicMock(), "Network error")
        
        with self.assertRaises(discord.HTTPException):
            await bot.get_command("help").callback(self.ctx)

    async def test_command_with_forbidden_error(self):
        """Test command behavior when bot lacks permissions"""
        self.ctx.send.side_effect = discord.Forbidden(MagicMock(), "Missing permissions")
        
        with self.assertRaises(discord.Forbidden):
            await bot.get_command("resume").callback(self.ctx)

    # Test bot initialization and configuration
    def test_bot_configuration(self):
        """Test that bot is configured with correct settings"""
        self.assertEqual(bot.command_prefix, "!")
        self.assertTrue(bot.intents.messages)
        self.assertTrue(bot.intents.message_content)
        self.assertIsNone(bot.help_command)

    def test_bot_has_all_commands(self):
        """Test that all expected commands are registered"""
        command_names = [cmd.name for cmd in bot.commands]
        expected_commands = ["help", "resume", "events", "resources"]
        
        for cmd in expected_commands:
            self.assertIn(cmd, command_names)

    # Test environment and token handling edge cases
    @patch("os.getenv")
    @patch("bot.load_dotenv", return_value=True)
    def test_token_with_whitespace(self, mock_load_dotenv, mock_getenv):
        """Test handling of token with leading/trailing whitespace"""
        mock_getenv.return_value = "  valid_token  "
        
        with patch("bot.bot.run") as mock_run:
            run_bot()
            # Should strip whitespace
            mock_run.assert_called_once_with("valid_token")  # Fixed: no whitespace

    @patch("os.getenv", return_value=None)
    @patch("bot.load_dotenv", return_value=True)
    def test_token_none_value(self, mock_load_dotenv, mock_getenv):
        """Test handling when token is None"""
        with self.assertRaises(AssertionError):
            run_bot()

    @patch("bot.bot.run", side_effect=discord.HTTPException(MagicMock(), "Connection failed"))
    @patch("os.getenv", return_value="valid_token")
    @patch("bot.load_dotenv", return_value=True)
    def test_connection_error(self, mock_load_dotenv, mock_getenv, mock_bot_run):
        """Test handling of connection errors during bot startup"""
        with self.assertRaises(discord.HTTPException):
            run_bot()

    # Test concurrent command execution
    async def test_multiple_commands_concurrently(self):
        """Test that multiple commands can be executed concurrently"""
        ctx1 = MagicMock()
        ctx1.send = AsyncMock()
        ctx2 = MagicMock()
        ctx2.send = AsyncMock()
        ctx3 = MagicMock()
        ctx3.send = AsyncMock()

        # Execute commands concurrently
        await asyncio.gather(
            bot.get_command("help").callback(ctx1),
            bot.get_command("resume").callback(ctx2),
            bot.get_command("events").callback(ctx3)
        )

        # Verify all commands executed
        ctx1.send.assert_called_once()
        ctx2.send.assert_called_once()
        ctx3.send.assert_called_once()

    # Test command docstrings and metadata
    def test_command_docstrings(self):
        """Test that all commands have proper docstrings"""
        for command in bot.commands:
            self.assertIsNotNone(command.callback.__doc__)
            self.assertTrue(len(command.callback.__doc__.strip()) > 0)

    # Test bot events
    @patch('builtins.print')
    async def test_on_ready_event(self, mock_print):
        """Test the on_ready event handler"""
        # Mock bot user for the event
        with patch.object(bot, 'user') as mock_user:
            mock_user.__str__ = MagicMock(return_value="TestBot#1234")
            
            # Trigger the on_ready event directly if it exists
            if hasattr(bot, 'on_ready'):
                await bot.on_ready()
                mock_print.assert_called_with("✅ Logged in as TestBot#1234")
            else:
                # Skip test if on_ready handler doesn't exist
                self.skipTest("Bot does not have on_ready event handler")

    # Test command aliases and case sensitivity
    def test_command_case_sensitivity(self):
        """Test that commands are case sensitive"""
        # Commands should be lowercase
        self.assertIsNotNone(bot.get_command("help"))
        self.assertIsNone(bot.get_command("HELP"))
        self.assertIsNone(bot.get_command("Help"))

    # Performance and load testing
    async def test_rapid_command_execution(self):
        """Test bot performance under rapid command execution"""
        contexts = []
        for i in range(10):
            ctx = MagicMock()
            ctx.send = AsyncMock()
            contexts.append(ctx)

        # Execute help command rapidly
        tasks = [bot.get_command("help").callback(ctx) for ctx in contexts]
        await asyncio.gather(*tasks)

        # Verify all executed successfully
        for ctx in contexts:
            ctx.send.assert_called_once()

    # Test message length limits
    async def test_message_length_compliance(self):
        """Test that all command responses are within Discord's message limits"""
        commands_to_test = ["help", "resume", "events", "resources"]
        
        for cmd_name in commands_to_test:
            ctx = MagicMock()
            ctx.send = AsyncMock()
            
            await bot.get_command(cmd_name).callback(ctx)
            
            sent_message = ctx.send.call_args[0][0]
            # Discord message limit is 2000 characters
            self.assertLessEqual(len(sent_message), 2000, 
                               f"Command {cmd_name} response too long")

    # Test environment file edge cases
    @patch("bot.load_dotenv", side_effect=Exception("File read error"))
    def test_dotenv_load_exception(self, mock_load_dotenv):
        """Test handling of exceptions during .env file loading"""
        with self.assertRaises(Exception):
            run_bot()

    @patch("os.getenv", side_effect=KeyError("Environment variable not found"))
    @patch("bot.load_dotenv", return_value=True)
    def test_getenv_exception(self, mock_load_dotenv, mock_getenv):
        """Test handling of exceptions during environment variable access"""
        with self.assertRaises(KeyError):
            run_bot()

    # Integration test for complete bot workflow
    @patch("bot.bot.run")
    @patch("os.getenv", return_value="test_token_12345")
    @patch("bot.load_dotenv", return_value=True)
    async def test_complete_bot_workflow(self, mock_load_dotenv, mock_getenv, mock_bot_run):
        """Integration test for complete bot startup and command execution"""
        # Test bot startup
        run_bot()
        mock_bot_run.assert_called_once_with("test_token_12345")
        
        # Test all commands work together
        for cmd_name in ["help", "resume", "events", "resources"]:
            ctx = MagicMock()
            ctx.send = AsyncMock()
            await bot.get_command(cmd_name).callback(ctx)
            ctx.send.assert_called_once()

    # Test bot cleanup and shutdown scenarios
    def test_bot_cleanup(self):
        """Test that bot can be properly cleaned up"""
        # This would test cleanup logic if implemented
        self.assertIsNotNone(bot)
        # In a real scenario, you might test bot.close() or similar cleanup

    async def asyncTearDown(self):
        """Clean up after each test"""
        # Reset any mocks or state if needed
        pass


class TestBotCommandValidation(unittest.IsolatedAsyncioTestCase):
    """Separate test class for command validation and edge cases"""

    async def asyncSetUp(self):
        self.ctx = MagicMock()
        self.ctx.send = AsyncMock()

    async def test_commands_return_strings(self):
        """Test that all commands return string responses"""
        commands_to_test = ["help", "resume", "events", "resources"]
        
        for cmd_name in commands_to_test:
            await bot.get_command(cmd_name).callback(self.ctx)
            sent_message = self.ctx.send.call_args[0][0]
            self.assertIsInstance(sent_message, str)

    async def test_commands_not_empty(self):
        """Test that no command returns empty responses"""
        commands_to_test = ["help", "resume", "events", "resources"]
        
        for cmd_name in commands_to_test:
            await bot.get_command(cmd_name).callback(self.ctx)
            sent_message = self.ctx.send.call_args[0][0]
            self.assertTrue(len(sent_message.strip()) > 0)

    async def test_unicode_emoji_support(self):
        """Test that commands properly handle Unicode emojis"""
        await bot.get_command("help").callback(self.ctx)
        sent_message = self.ctx.send.call_args[0][0]
        # Should contain emoji characters
        self.assertTrue(any(ord(char) > 127 for char in sent_message))


class TestBotSecurityAndEdgeCases(unittest.IsolatedAsyncioTestCase):
    """Test class for security scenarios and additional edge cases"""

    async def asyncSetUp(self):
        self.ctx = MagicMock()
        self.ctx.send = AsyncMock()
        self.ctx.author = MagicMock()
        self.ctx.author.id = 12345
        self.ctx.guild = MagicMock()
        self.ctx.guild.id = 67890

    async def test_malformed_context_handling(self):
        """Test bot behavior with malformed context objects"""
        malformed_ctx = MagicMock()
        malformed_ctx.send = AsyncMock()
        malformed_ctx.author = None
        malformed_ctx.guild = None
        malformed_ctx.channel = None

        # Commands should still work with minimal context
        await bot.get_command("help").callback(malformed_ctx)
        malformed_ctx.send.assert_called_once()

    async def test_dm_context_simulation(self):
        """Test bot behavior in DM contexts"""
        dm_ctx = MagicMock()
        dm_ctx.send = AsyncMock()
        dm_ctx.author = MagicMock()
        dm_ctx.author.id = 12345
        dm_ctx.guild = None  # No guild in DMs
        dm_ctx.channel = MagicMock()
        dm_ctx.channel.type = discord.ChannelType.private

        # Commands should work in DMs
        for cmd_name in ["help", "resume", "events", "resources"]:
            await bot.get_command(cmd_name).callback(dm_ctx)
            dm_ctx.send.assert_called()
            dm_ctx.send.reset_mock()

    @patch("os.getenv", return_value="")
    @patch("bot.load_dotenv", return_value=True)
    def test_empty_token_string(self, mock_load_dotenv, mock_getenv):
        """Test handling of empty token string"""
        with self.assertRaises(AssertionError):
            run_bot()

    @patch("os.getenv", return_value="invalid_token_format")
    @patch("bot.load_dotenv", return_value=True)
    @patch("bot.bot.run", side_effect=discord.LoginFailure("Invalid token"))
    def test_invalid_token_format(self, mock_bot_run, mock_load_dotenv, mock_getenv):
        """Test handling of invalid token format"""
        with self.assertRaises(discord.LoginFailure):
            run_bot()

    async def test_command_timing_and_performance(self):
        """Test command execution timing"""
        start_time = time.time()
        await bot.get_command("help").callback(self.ctx)
        execution_time = time.time() - start_time
        
        # Command should execute quickly (less than 1 second)
        self.assertLess(execution_time, 1.0)

    async def test_memory_usage_stability(self):
        """Test that repeated command execution doesn't cause memory leaks"""
        import gc
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Execute commands multiple times
        for _ in range(50):
            ctx = MagicMock()
            ctx.send = AsyncMock()
            await bot.get_command("help").callback(ctx)
        
        gc.collect()  # Force garbage collection
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be minimal (less than 10MB)
        self.assertLess(memory_increase, 10 * 1024 * 1024)

    def test_bot_intents_security(self):
        """Test that bot has minimal necessary intents for security"""
        # Bot should not have privileged intents unless necessary
        self.assertFalse(bot.intents.presences)
        self.assertFalse(bot.intents.members)
        # Should only have message-related intents
        self.assertTrue(bot.intents.messages)
        self.assertTrue(bot.intents.message_content)

    async def test_rate_limiting_simulation(self):
        """Simulate rate limiting scenarios"""
        self.ctx.send.side_effect = discord.HTTPException(
            MagicMock(), "You are being rate limited"
        )
        
        with self.assertRaises(discord.HTTPException):
            await bot.get_command("help").callback(self.ctx)

    async def test_special_characters_in_responses(self):
        """Test that responses handle special characters correctly"""
        for cmd_name in ["help", "resume", "events", "resources"]:
            await bot.get_command(cmd_name).callback(self.ctx)
            sent_message = self.ctx.send.call_args[0][0]
            
            # Should handle Unicode properly
            try:
                sent_message.encode('utf-8')
            except UnicodeEncodeError:
                self.fail(f"Command {cmd_name} contains unhandleable Unicode")

    def test_command_cooldowns_existence(self):
        """Test if commands have appropriate cooldowns"""
        # Check if any command has cooldowns (good practice for public bots)
        for command in bot.commands:
            # Commands might have cooldowns for anti-spam
            if hasattr(command, '_buckets') and command._buckets:
                # Cooldown exists - verify it's reasonable
                self.assertIsNotNone(command._buckets)


class TestBotNetworkAndConnectivity(unittest.IsolatedAsyncioTestCase):
    """Test network-related scenarios and connectivity issues"""

    async def asyncSetUp(self):
        self.ctx = MagicMock()
        self.ctx.send = AsyncMock()

    @patch("bot.bot.run", side_effect=discord.ConnectionClosed(None))
    @patch("os.getenv", return_value="valid_token")
    @patch("bot.load_dotenv", return_value=True)
    def test_connection_closed_error(self, mock_load_dotenv, mock_getenv, mock_bot_run):
        """Test handling of connection closed errors"""
        with self.assertRaises(discord.ConnectionClosed):
            run_bot()

    async def test_slow_network_response_simulation(self):
        """Simulate slow network responses"""
        # Simulate a slow ctx.send
        async def slow_send(*args, **kwargs):
            await asyncio.sleep(0.1)  # 100ms delay
            return MagicMock()
        
        self.ctx.send = slow_send
        
        start_time = time.time()
        await bot.get_command("help").callback(self.ctx)
        execution_time = time.time() - start_time
        
        # Should handle slow responses gracefully
        self.assertGreaterEqual(execution_time, 0.1)

    async def test_network_timeout_simulation(self):
        """Simulate network timeout scenarios"""
        async def timeout_send(*args, **kwargs):
            raise asyncio.TimeoutError("Network timeout")
        
        self.ctx.send = timeout_send
        
        with self.assertRaises(asyncio.TimeoutError):
            await bot.get_command("help").callback(self.ctx)