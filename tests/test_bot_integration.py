# test_bot_integration.py
# Integration and end-to-end testing for the Discord bot
# Tests real-world scenarios, Discord API interactions, and workflow testing

import unittest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch, PropertyMock
import discord
from discord.ext import commands
from bot import bot, run_bot
import json
import tempfile
import os


class TestBotIntegration(unittest.IsolatedAsyncioTestCase):
    """Integration tests for Discord bot end-to-end scenarios"""

    async def asyncSetUp(self):
        """Set up integration test fixtures"""
        # Create realistic Discord context mock
        self.guild = MagicMock()
        self.guild.id = 123456789
        self.guild.name = "Test Server"
        
        self.channel = MagicMock()
        self.channel.id = 987654321
        self.channel.name = "general"
        self.channel.guild = self.guild
        
        self.author = MagicMock()
        self.author.id = 555666777
        self.author.name = "TestUser"
        self.author.discriminator = "1234"
        self.author.display_name = "TestUser"
        
        self.ctx = MagicMock()
        self.ctx.send = AsyncMock()
        self.ctx.guild = self.guild
        self.ctx.channel = self.channel
        self.ctx.author = self.author
        self.ctx.message = MagicMock()
        self.ctx.bot = bot

    async def test_complete_user_workflow_help_to_resources(self):
        """Test complete user workflow: help -> specific command -> resources"""
        # Step 1: User asks for help
        await bot.get_command("help").callback(self.ctx)
        help_message = self.ctx.send.call_args[0][0]
        self.assertIn("!resources", help_message)
        
        # Step 2: User requests resources
        await bot.get_command("resources").callback(self.ctx)

        # Verify both calls were made and check their contents
        self.assertEqual(self.ctx.send.call_count, 2)
        resources_message = self.ctx.send.call_args_list[1].args[0]
        self.assertIn("CS50", resources_message)

    async def test_bot_responds_to_different_user_types(self):
        """Test bot responds appropriately to different types of Discord users"""
        user_scenarios = [
            {"name": "RegularUser", "roles": [], "is_bot": False},
            {"name": "ModeratorUser", "roles": ["Moderator"], "is_bot": False},
            {"name": "AdminUser", "roles": ["Admin"], "is_bot": False},
        ]
        
        for scenario in user_scenarios:
            # Create user-specific context
            ctx = MagicMock()
            ctx.send = AsyncMock()
            ctx.author = MagicMock()
            ctx.author.name = scenario["name"]
            ctx.author.bot = scenario["is_bot"]
            
            # Test command execution
            await bot.get_command("help").callback(ctx)
            
            # Should respond to all user types
            ctx.send.assert_called_once()
            response = ctx.send.call_args[0][0]
            self.assertIsInstance(response, str)
            self.assertGreater(len(response), 0)

    async def test_command_chaining_scenario(self):
        """Test realistic scenario where user chains multiple commands"""
        commands_sequence = ["help", "events", "resume", "resources"]
        responses = []
        
        for cmd_name in commands_sequence:
            ctx = MagicMock()
            ctx.send = AsyncMock()
            
            await bot.get_command(cmd_name).callback(ctx)
            response = ctx.send.call_args[0][0]
            responses.append(response)
        
        # Verify each response is unique and appropriate
        self.assertEqual(len(responses), 4)
        self.assertIn("Commands:", responses[0])  # help
        self.assertIn("Events:", responses[1])    # events
        self.assertIn("Resume", responses[2])     # resume
        self.assertIn("Resources:", responses[3]) # resources

    async def test_bot_handles_discord_rate_limits(self):
        """Test bot behavior when Discord rate limits are hit"""
        # Simulate rate limit exception
        self.ctx.send.side_effect = discord.HTTPException(
            MagicMock(), "429 Too Many Requests"
        )
        
        with self.assertRaises(discord.HTTPException):
            await bot.get_command("help").callback(self.ctx)

    async def test_bot_handles_network_interruption(self):
        """Test bot behavior during network interruptions"""
        # Simulate network error
        self.ctx.send.side_effect = discord.ConnectionClosed(None)
        
        with self.assertRaises(discord.ConnectionClosed):
            await bot.get_command("help").callback(self.ctx)

    @patch.dict(os.environ, {}, clear=True)
    def test_production_environment_simulation(self):
        """Test bot behavior in production-like environment"""
        # Simulate production environment without .env file
        with patch("bot.load_dotenv", return_value=False):
            with patch("sys.exit") as mock_exit:
                run_bot()
                mock_exit.assert_called_with(1)

    async def test_concurrent_users_different_commands(self):
        """Test multiple users executing different commands simultaneously"""
        users = [
            {"name": "User1", "command": "help"},
            {"name": "User2", "command": "events"},
            {"name": "User3", "command": "resume"},
            {"name": "User4", "command": "resources"},
        ]
        
        tasks = []
        contexts = {}
        
        for user in users:
            ctx = MagicMock()
            ctx.send = AsyncMock()
            ctx.author = MagicMock()
            ctx.author.name = user["name"]
            contexts[user["name"]] = ctx
            
            task = bot.get_command(user["command"]).callback(ctx)
            tasks.append(task)
        
        # Execute all commands concurrently
        await asyncio.gather(*tasks)
        
        # Verify all users got responses
        for user in users:
            contexts[user["name"]].send.assert_called_once()

    async def test_bot_command_error_recovery(self):
        """Test bot recovers gracefully from command errors"""
        # First command fails
        ctx1 = MagicMock()
        ctx1.send = AsyncMock(side_effect=Exception("Network error"))
        
        with self.assertRaises(Exception):
            await bot.get_command("help").callback(ctx1)
        
        # Second command should still work
        ctx2 = MagicMock()
        ctx2.send = AsyncMock()
        
        await bot.get_command("help").callback(ctx2)
        ctx2.send.assert_called_once()

    def test_bot_configuration_validation(self):
        """Test that bot configuration is valid for production use"""
        # Check intents
        self.assertTrue(bot.intents.messages)
        self.assertTrue(bot.intents.message_content)
        
        # Check command prefix
        self.assertEqual(bot.command_prefix, "!")
        
        # Check help command is disabled (we have custom one)
        self.assertIsNone(bot.help_command)
        
        # Verify all commands are properly registered
        command_names = [cmd.name for cmd in bot.commands]
        expected_commands = ["help", "resume", "events", "resources"]
        for cmd in expected_commands:
            self.assertIn(cmd, command_names)


class TestBotDiscordAPIIntegration(unittest.IsolatedAsyncioTestCase):
    """Test Discord API specific integration scenarios"""

    async def asyncSetUp(self):
        self.ctx = MagicMock()
        self.ctx.send = AsyncMock()

    async def test_message_formatting_compatibility(self):
        """Test that bot messages are compatible with Discord formatting"""
        commands_to_test = ["help", "resume", "events", "resources"]
        
        for cmd_name in commands_to_test:
            ctx = MagicMock()
            ctx.send = AsyncMock()
            
            await bot.get_command(cmd_name).callback(ctx)
            message = ctx.send.call_args[0][0]
            
            # Check Discord markdown compatibility
            if "**" in message:  # Bold text
                bold_count = message.count("**")
                self.assertEqual(bold_count % 2, 0, f"Unmatched bold markers in {cmd_name}")
            
            if "`" in message:  # Code blocks
                code_count = message.count("`")
                # Allow both single ` and triple ``` code blocks
                single_backticks = message.count("`") - message.count("```") * 3
                self.assertTrue(single_backticks % 2 == 0 or "```" in message,
                               f"Unmatched code markers in {cmd_name}")

    async def test_embed_compatibility(self):
        """Test that messages would work if converted to embeds"""
        await bot.get_command("help").callback(self.ctx)
        message = self.ctx.send.call_args[0][0]
        
        # Should be short enough for embed title/description
        lines = message.split('\n')
        for line in lines:
            self.assertLessEqual(len(line), 256, "Line too long for embed field")

    async def test_unicode_emoji_rendering(self):
        """Test that Unicode emojis render correctly"""
        commands_with_emojis = ["help", "resume", "events", "resources"]
        
        for cmd_name in commands_with_emojis:
            ctx = MagicMock()
            ctx.send = AsyncMock()
            
            await bot.get_command(cmd_name).callback(ctx)
            message = ctx.send.call_args[0][0]
            
            # Check for emoji characters
            has_emoji = any(ord(char) > 127 for char in message)
            self.assertTrue(has_emoji, f"Command {cmd_name} should contain emojis")

    async def test_message_length_discord_limits(self):
        """Test messages comply with Discord's character limits"""
        commands_to_test = ["help", "resume", "events", "resources"]
        
        for cmd_name in commands_to_test:
            ctx = MagicMock()
            ctx.send = AsyncMock()
            
            await bot.get_command(cmd_name).callback(ctx)
            message = ctx.send.call_args[0][0]
            
            # Discord message limit is 2000 characters
            self.assertLessEqual(len(message), 2000,
                               f"Message from {cmd_name} exceeds Discord limit")
            
            # Should also not be empty
            self.assertGreater(len(message.strip()), 0,
                             f"Message from {cmd_name} is empty")


class TestBotWorkflowScenarios(unittest.IsolatedAsyncioTestCase):
    """Test realistic Discord bot usage workflows"""

    async def test_new_user_onboarding_flow(self):
        """Test typical new user interaction flow"""
        ctx = MagicMock()
        ctx.send = AsyncMock()
        
        # New user typically starts with help
        await bot.get_command("help").callback(ctx)
        help_response = ctx.send.call_args[0][0]
        
        # Should mention all available commands
        self.assertIn("!resume", help_response)
        self.assertIn("!events", help_response)
        self.assertIn("!resources", help_response)
        
        # User then typically asks for resources
        ctx.send.reset_mock()
        await bot.get_command("resources").callback(ctx)
        resources_response = ctx.send.call_args[0][0]
        
        # Should provide useful learning resources
        self.assertIn("CS50", resources_response)
        self.assertIn("FreeCodeCamp", resources_response)

    async def test_event_planning_workflow(self):
        """Test workflow for users planning to attend events"""
        ctx = MagicMock()
        ctx.send = AsyncMock()
        
        # User checks events
        await bot.get_command("events").callback(ctx)
        events_response = ctx.send.call_args[0][0]
        
        # Should contain upcoming events with dates
        self.assertIn("April", events_response)
        self.assertIn("Workshop", events_response)
        
        # User might then check resources for preparation
        ctx.send.reset_mock()
        await bot.get_command("resources").callback(ctx)
        
        # Should get learning resources
        ctx.send.assert_called_once()

    async def test_job_seeking_workflow(self):
        """Test workflow for users seeking job-related help"""
        ctx = MagicMock()
        ctx.send = AsyncMock()
        
        # User asks for resume help
        await bot.get_command("resume").callback(ctx)
        resume_response = ctx.send.call_args[0][0]
        
        # Should provide resume resources
        self.assertIn("Resume Resources", resume_response)
        self.assertIn("https://", resume_response)
        
        # User might then check for events
        ctx.send.reset_mock()
        await bot.get_command("events").callback(ctx)
        
        # Should show relevant events
        ctx.send.assert_called_once()

    async def test_study_group_workflow(self):
        """Test workflow for study group coordination"""
        # Multiple users checking resources and events
        users = ["Student1", "Student2", "Student3"]
        
        for user in users:
            ctx = MagicMock()
            ctx.send = AsyncMock()
            ctx.author = MagicMock()
            ctx.author.name = user
            
            # Each user checks resources
            await bot.get_command("resources").callback(ctx)
            ctx.send.assert_called_once()
            
            # Reset and check events
            ctx.send.reset_mock()
            await bot.get_command("events").callback(ctx)
            ctx.send.assert_called_once()


class TestBotMaintenanceScenarios(unittest.TestCase):
    """Test scenarios related to bot maintenance and monitoring"""

    def test_command_registration_integrity(self):
        """Test that all commands are properly registered"""
        expected_commands = {"help", "resume", "events", "resources"}
        actual_commands = {cmd.name for cmd in bot.commands}
        
        self.assertEqual(expected_commands, actual_commands,
                        "Command registration mismatch")

    def test_bot_ready_for_deployment(self):
        """Test that bot is ready for deployment"""
        # Check bot has required attributes
        self.assertIsNotNone(bot.command_prefix)
        self.assertIsNotNone(bot.intents)
        self.assertTrue(len(list(bot.commands)) > 0)
        
        # Check each command has proper callback
        for command in bot.commands:
            self.assertIsNotNone(command.callback)
            self.assertTrue(callable(command.callback))

    @patch("bot.load_dotenv")
    @patch("os.getenv")
    def test_environment_configuration_validation(self, mock_getenv, mock_load_dotenv):
        """Test environment configuration scenarios"""
        # Test valid configuration
        mock_load_dotenv.return_value = True
        mock_getenv.return_value = "valid_token_here"
        
        with patch("bot.bot.run") as mock_run:
            run_bot()
            mock_run.assert_called_once_with("valid_token_here")


if __name__ == "__main__":
    # Run integration tests
    unittest.main(verbosity=2) 