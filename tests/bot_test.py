# test_bot.py
# This file contains unit tests for the Discord bot commands
# It uses Python's unittest framework with async support for testing Discord.py commands

import unittest
from unittest.mock import AsyncMock, MagicMock, patch, mock_open
import tempfile
import os
from datetime import datetime
from bot import bot, run_bot, events_data  # Import the bot instance and global data
import discord
from models import Event, EventType, Resource, JobPosting, InterviewQuestion, NetworkingTip, Skill
from config import BotConfig
from utils import (
    parse_datetime,
    load_events_from_csv,
    get_upcoming_events,
    create_embed,
    add_field_to_embed,
    format_list_for_embed
)


class TestDataModels(unittest.TestCase):
    """Test suite for data model classes"""

    def test_event_creation(self):
        """Test Event dataclass creation and validation"""
        start_date = datetime.now()
        end_date = start_date.replace(hour=start_date.hour + 2)

        event = Event(
            title="Test Event",
            description="A test event",
            start_date=start_date,
            end_date=end_date,
            location="Test Location",
            link="https://example.com",
            event_type=EventType.WORKSHOP
        )

        self.assertEqual(event.title, "Test Event")
        self.assertEqual(event.location, "Test Location")
        self.assertTrue(event.is_upcoming)
        self.assertEqual(event.duration_hours, 2.0)

    def test_event_invalid_dates(self):
        """Test Event validation for invalid date ranges"""
        start_date = datetime.now()
        end_date = start_date.replace(hour=start_date.hour - 1)  # End before start

        with self.assertRaises(ValueError):
            Event(
                title="Invalid Event",
                description="This should fail",
                start_date=start_date,
                end_date=end_date
            )

    def test_resource_creation(self):
        """Test Resource dataclass creation"""
        resource = Resource(
            title="Test Resource",
            description="A test resource",
            url="https://example.com",
            category="Testing",
            difficulty="Beginner",
            tags=["test", "python"]
        )

        self.assertEqual(resource.title, "Test Resource")
        self.assertIn("test", resource.tags)
        formatted = resource.format_for_discord()
        self.assertIn("Test Resource", formatted)
        self.assertIn("🟢", formatted)  # Beginner emoji

    def test_job_posting_creation(self):
        """Test JobPosting dataclass creation"""
        job = JobPosting(
            title="Test Job",
            company="Test Corp",
            description="A test job",
            location="Remote",
            url="https://example.com/job",
            salary_range="$50k-70k"
        )

        self.assertEqual(job.title, "Test Job")
        formatted = job.format_for_discord()
        self.assertIn("Test Corp", formatted)
        self.assertIn("$50k-70k", formatted)

    def test_interview_question_creation(self):
        """Test InterviewQuestion dataclass creation"""
        question = InterviewQuestion(
            question="What is Python?",
            category="Programming",
            difficulty="Easy",
            hints=["It's a programming language", "Created by Guido van Rossum"],
            solution="Python is a high-level programming language"
        )

        self.assertEqual(question.question, "What is Python?")
        self.assertEqual(len(question.hints), 2)
        formatted = question.format_for_discord()
        self.assertIn("What is Python?", formatted)
        self.assertIn("🟢", formatted)  # Easy emoji


class TestUtils(unittest.TestCase):
    """Test suite for utility functions"""

    def test_parse_datetime(self):
        """Test datetime parsing from various formats"""
        # Test ISO format
        dt = parse_datetime("2025-04-25 18:00:00")
        self.assertIsInstance(dt, datetime)

        # Test Discord format
        dt = parse_datetime("Friday, April 25th 2025, 6:00 pm EDT")
        self.assertIsInstance(dt, datetime)

        # Test invalid format
        dt = parse_datetime("invalid date")
        self.assertIsNone(dt)

    def test_load_events_from_csv(self):
        """Test loading events from CSV"""
        csv_content = """Type,Title,Description,whenDate,pubDate,Location,link
Event,Test Event,Test Description,"Friday, April 25th 2025, 6:00 pm EDT","Tue, 15 Apr 2025 10:00:00 -0400",Test Location,https://example.com"""

        with patch('builtins.open', mock_open(read_data=csv_content)):
            events = load_events_from_csv("dummy.csv")
            self.assertEqual(len(events), 1)
            self.assertEqual(events[0].title, "Test Event")
            self.assertEqual(events[0].location, "Test Location")

    def test_get_upcoming_events(self):
        """Test filtering upcoming events"""
        past_event = Event(
            title="Past Event",
            description="Past",
            start_date=datetime.now().replace(day=datetime.now().day - 1)
        )
        future_event = Event(
            title="Future Event",
            description="Future",
            start_date=datetime.now().replace(day=datetime.now().day + 1)
        )

        events = [past_event, future_event]
        upcoming = get_upcoming_events(events)

        self.assertEqual(len(upcoming), 1)
        self.assertEqual(upcoming[0].title, "Future Event")

    def test_create_embed(self):
        """Test embed creation"""
        embed = create_embed("Test Title", "Test Description", 0xff0000)
        self.assertEqual(embed.title, "Test Title")
        self.assertEqual(embed.description, "Test Description")
        self.assertEqual(embed.color.value, 0xff0000)

    def test_format_list_for_embed(self):
        """Test list formatting for embeds"""
        items = ["item1", "item2", "item3"]
        formatted = format_list_for_embed(items, 2)
        self.assertIn("item1", formatted)
        self.assertIn("item2", formatted)
        self.assertIn("1 more", formatted)


class TestConfig(unittest.TestCase):
    """Test suite for configuration management"""

    def test_config_creation(self):
        """Test BotConfig creation and properties"""
        config = BotConfig()
        self.assertEqual(config.command_prefix, "!")
        self.assertEqual(config.bot_name, "CuseBot")
        self.assertIsInstance(config.resources, list)
        self.assertIsInstance(config.job_postings, list)

    def test_config_validation(self):
        """Test configuration validation"""
        config = BotConfig()
        issues = config.validate_config()
        # Should have issues since we're not in the project directory
        self.assertIsInstance(issues, list)

    def test_skill_search(self):
        """Test skill search functionality"""
        config = BotConfig()
        skill = config.get_skill_by_name("Python Programming")
        self.assertIsNotNone(skill)
        self.assertEqual(skill.name, "Python Programming")

        # Test case insensitive search
        skill = config.get_skill_by_name("python programming")
        self.assertIsNotNone(skill)

        # Test non-existent skill
        skill = config.get_skill_by_name("NonExistentSkill")
        self.assertIsNone(skill)


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
    def test_env_with_invalid_token(self, mock_exit, mock_load_dotenv, mock_getenv, mock_bot_run):
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

    @patch("bot.events_data", [])  # Mock empty events data
    async def test_events_command_no_data(self):
        """Test !events command when no data is available"""
        await bot.get_command("events").callback(self.ctx)
        self.ctx.send.assert_called_once()
        call_args = self.ctx.send.call_args[0][0]
        self.assertIn("No events data available", str(call_args))

    async def test_events_command_with_data(self):
        """Test !events command with mock data"""
        from models import Event, EventType
        from datetime import datetime

        # Create mock events data
        future_event = Event(
            title="Future Test Event",
            description="A test event",
            start_date=datetime.now().replace(day=datetime.now().day + 1),
            location="Test Location",
            event_type=EventType.EVENT
        )

        with patch("bot.events_data", [future_event]):
            await bot.get_command("events").callback(self.ctx)
            self.ctx.send.assert_called_once()
            # Check that embed was sent (not a plain string)
            call_args = self.ctx.send.call_args[0][0]
            self.assertTrue(hasattr(call_args, 'title'))  # It's an embed

    async def test_resources_command(self):
        """Test !resources command"""
        await bot.get_command("resources").callback(self.ctx)
        self.ctx.send.assert_called_once()
        call_args = self.ctx.send.call_args[0][0]
        self.assertTrue(hasattr(call_args, 'title'))  # It's an embed

    async def test_resources_command_with_category(self):
        """Test !resources command with category filter"""
        await bot.get_command("resources").callback(self.ctx, category="Web Development")
        self.ctx.send.assert_called_once()

    async def test_interview_command(self):
        """Test !interview command"""
        await bot.get_command("interview").callback(self.ctx)
        self.ctx.send.assert_called_once()
        call_args = self.ctx.send.call_args[0][0]
        self.assertTrue(hasattr(call_args, 'title'))  # It's an embed

    async def test_interview_command_with_difficulty(self):
        """Test !interview command with difficulty filter"""
        await bot.get_command("interview").callback(self.ctx, difficulty="Easy")
        self.ctx.send.assert_called_once()

    async def test_interview_command_invalid_difficulty(self):
        """Test !interview command with invalid difficulty"""
        await bot.get_command("interview").callback(self.ctx, difficulty="Invalid")
        self.ctx.send.assert_called_once()
        call_args = self.ctx.send.call_args[0][0]
        self.assertIn("No questions found", call_args)

    async def test_jobs_command(self):
        """Test !jobs command"""
        await bot.get_command("jobs").callback(self.ctx)
        self.ctx.send.assert_called_once()
        call_args = self.ctx.send.call_args[0][0]
        self.assertTrue(hasattr(call_args, 'title'))  # It's an embed

    async def test_jobs_command_with_type(self):
        """Test !jobs command with job type filter"""
        await bot.get_command("jobs").callback(self.ctx, job_type="Internship")
        self.ctx.send.assert_called_once()

    async def test_networking_command(self):
        """Test !networking command"""
        await bot.get_command("networking").callback(self.ctx)
        self.ctx.send.assert_called_once()
        call_args = self.ctx.send.call_args[0][0]
        self.assertTrue(hasattr(call_args, 'title'))  # It's an embed

    async def test_networking_command_with_category(self):
        """Test !networking command with category filter"""
        await bot.get_command("networking").callback(self.ctx, category="Events")
        self.ctx.send.assert_called_once()

    async def test_skills_command_overview(self):
        """Test !skills command overview"""
        await bot.get_command("skills").callback(self.ctx)
        self.ctx.send.assert_called_once()
        call_args = self.ctx.send.call_args[0][0]
        self.assertTrue(hasattr(call_args, 'title'))  # It's an embed

    async def test_skills_command_specific_skill(self):
        """Test !skills command with specific skill name"""
        await bot.get_command("skills").callback(self.ctx, skill_name="Python Programming")
        self.ctx.send.assert_called_once()

    async def test_skills_command_invalid_skill(self):
        """Test !skills command with invalid skill name"""
        await bot.get_command("skills").callback(self.ctx, skill_name="InvalidSkill")
        self.ctx.send.assert_called_once()
        call_args = self.ctx.send.call_args[0][0]
        self.assertIn("not found", call_args.lower())

    async def test_mentor_command(self):
        """Test !mentor command"""
        await bot.get_command("mentor").callback(self.ctx)
        self.ctx.send.assert_called_once()
        call_args = self.ctx.send.call_args[0][0]
        self.assertTrue(hasattr(call_args, 'title'))  # It's an embed


if __name__ == "__main__":
    # Run the tests when the file is executed directly
    unittest.main(verbosity=2)
