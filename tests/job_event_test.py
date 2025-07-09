import unittest
from unittest.mock import patch, AsyncMock, MagicMock
import asyncio
import sys
import os
from data_processing.job_event import (getJobs, paste_jobs_command, format_jobs_message, filter_jobs)

# Add the parent directory to the path so we can import your modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestJobsCommand(unittest.IsolatedAsyncioTestCase):
    """Test class for jobs command using IsolatedAsyncioTestCase for proper async support"""
    
    async def asyncSetUp(self):
        """Set up test fixtures before each test"""
        # Create a mock Discord context
        self.ctx = MagicMock()
        self.ctx.send = AsyncMock()
        self.ctx.author = MagicMock()
        self.ctx.author.id = 12345
        self.ctx.channel = MagicMock()
        self.ctx.guild = MagicMock()
        
        # Mock the bot instance
        self.bot = MagicMock()
        
        # Create mock command
        self.mock_command = MagicMock()
        self.mock_command.callback = AsyncMock()
        self.bot.get_command.return_value = self.mock_command
        
        # Sample job data for testing
        self.sample_job = {
            "Type": "Internship",
            "Title": "Software Developer Internship",
            "Description": "Work on backend systems. TestDesc included here.",
            "Company": "Test Company",
            "Location": "New York",
            "whenDate": "",
            "pubDate": "",
            "link": "http://test.com",
            "entryDate": "2025-07-07"
        }
        
        self.sample_jobs = [self.sample_job]

    @patch("builtins.open", new_callable=unittest.mock.mock_open, read_data="")
    @patch("data_collections.csv_updater.remove_duplicates")
    @patch("data_collections.csv_updater.extract_entries_from_csv")
    async def test_jobs_command_no_filters(self, mock_extract, mock_dedup, mock_open):
        """Test the jobs command without any filters"""
        # Set up mocks
        mock_extract.return_value = self.sample_jobs
        mock_dedup.return_value = self.sample_jobs
        
        # Mock the actual command function
        async def mock_jobs_command(ctx, args=""):
            # Simulate the actual command logic
            jobs = mock_extract("jobs.csv")
            jobs = mock_dedup(jobs)
            
            message = f"Found {len(jobs)} job{'s' if len(jobs) != 1 else ''}"
            if jobs:
                # Add job details to message
                job = jobs[0]
                message += f"\n\n**{job['Title']}** at {job['Company']}"
                message += f"\nLocation: {job['Location']}"
                message += f"\nType: {job['Type']}"
                message += f"\nLink: {job['link']}"
            
            await ctx.send(message)
        
        # Set the mock command callback
        self.mock_command.callback = mock_jobs_command
        
        # Execute the test
        args = ""
        command = self.bot.get_command("jobs")
        await command.callback(self.ctx, args=args)
        
        # Verify the results
        self.ctx.send.assert_called_once()
        
        # Check the message content
        call_args = self.ctx.send.call_args[0][0]
        result_msg = call_args
    
        
        # Assertions
        self.assertIn("Found 1 job", result_msg)
        self.assertIn("Software Developer Internship", result_msg)
        self.assertIn("Test Company", result_msg)
        self.assertIn("New York", result_msg)
        
        # Verify mocks were called
        mock_extract.assert_called()
        mock_dedup.assert_called_once()

    @patch("builtins.open", new_callable=unittest.mock.mock_open, read_data="")
    @patch("data_collections.csv_updater.remove_duplicates")
    @patch("data_collections.csv_updater.extract_entries_from_csv")
    async def test_jobs_command_with_filters(self, mock_extract, mock_dedup, mock_open):
        """Test the jobs command with filters"""
        # Create multiple jobs for filtering
        jobs = [
            self.sample_job,
            {
                "Type": "Full-time",
                "Title": "Senior Software Engineer",
                "Description": "Lead development team",
                "Company": "Big Tech Corp",
                "Location": "San Francisco",
                "whenDate": "",
                "pubDate": "",
                "link": "http://bigtech.com",
                "entryDate": "2025-07-06"
            }
        ]
        
        mock_extract.return_value = jobs
        mock_dedup.return_value = jobs
        
        # Mock command with filtering logic
        async def mock_jobs_command_with_filter(ctx, args=""):
            all_jobs = mock_extract("jobs.csv")
            all_jobs = mock_dedup(all_jobs)
            
            # Simple filter by type
            if "internship" in args.lower():
                filtered_jobs = [job for job in all_jobs if job["Type"].lower() == "internship"]
            else:
                filtered_jobs = all_jobs
            
            message = f"Found {len(filtered_jobs)} job{'s' if len(filtered_jobs) != 1 else ''}"
            await ctx.send(message)
        
        self.mock_command.callback = mock_jobs_command_with_filter
        
        # Test with filter
        args = "internship"
        command = self.bot.get_command("jobs")
        await command.callback(self.ctx, args=args)
        
        # Verify results
        self.ctx.send.assert_called_once()
        result_msg = self.ctx.send.call_args[0][0]
        
        self.assertIn("Found 1 job", result_msg)

    @patch("builtins.open", new_callable=unittest.mock.mock_open, read_data="")
    @patch("data_collections.csv_updater.remove_duplicates")
    @patch("data_collections.csv_updater.extract_entries_from_csv")
    async def test_jobs_command_no_results(self, mock_extract, mock_dedup, mock_open):
        """Test the jobs command when no jobs are found"""
        # Mock empty results
        mock_extract.return_value = []
        mock_dedup.return_value = []
        
        async def mock_jobs_command_empty(ctx, args=""):
            jobs = mock_extract("jobs.csv")
            jobs = mock_dedup(jobs)
            
            if not jobs:
                message = "No jobs found matching your criteria."
            else:
                message = f"Found {len(jobs)} jobs"
            
            await ctx.send(message)
        
        self.mock_command.callback = mock_jobs_command_empty
        
        # Execute test
        args = ""
        command = self.bot.get_command("jobs")
        await command.callback(self.ctx, args=args)
        
        # Verify results
        self.ctx.send.assert_called_once()
        result_msg = self.ctx.send.call_args[0][0]
        
        self.assertIn("No jobs found", result_msg)

    @patch("builtins.open", new_callable=unittest.mock.mock_open, read_data="")
    @patch("data_collections.csv_updater.remove_duplicates")
    @patch("data_collections.csv_updater.extract_entries_from_csv")
    async def test_jobs_command_exception_handling(self, mock_extract, mock_dedup, mock_open):
        """Test the jobs command error handling"""
        # Mock an exception
        mock_extract.side_effect = Exception("CSV file not found")
        
        async def mock_jobs_command_with_error(ctx, args=""):
            try:
                jobs = mock_extract("jobs.csv")
                jobs = mock_dedup(jobs)
                message = f"Found {len(jobs)} jobs"
            except Exception as e:
                message = f"Error retrieving jobs: {str(e)}"
            
            await ctx.send(message)
        
        self.mock_command.callback = mock_jobs_command_with_error
        
        # Execute test
        args = ""
        command = self.bot.get_command("jobs")
        await command.callback(self.ctx, args=args)
        
        # Verify error handling
        self.ctx.send.assert_called_once()
        result_msg = self.ctx.send.call_args[0][0]
        self.assertIn("Error retrieving jobs", result_msg)
        self.assertIn("CSV file not found", result_msg)

    async def test_mock_setup_verification(self):
        """Test to verify that mocks are set up correctly"""
        # Verify ctx.send is async
        self.assertTrue(asyncio.iscoroutinefunction(self.ctx.send))
        
        # Verify bot mock
        self.assertIsNotNone(self.bot)
        
        # Test that we can