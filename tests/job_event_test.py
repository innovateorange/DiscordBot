import unittest
from unittest.mock import patch, AsyncMock, MagicMock, mock_open
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_processing.job_event import (
    paste_jobs_command,
    filter_jobs,
    format_jobs_message,
    getJobs
)


class TestJobEventFunctions(unittest.TestCase):
    """Test class for job_event.py functions"""

    def setUp(self):
        self.sample_jobs = [
            {
                "Type": "Internship",
                "Title": "Pizza Quality Assurance Intern",
                "Description": "Help us ensure our pizza reaches peak deliciousness. Must love cheese and have strong opinions about pineapple.",
                "Company": "Cheesy Dreams Inc",
                "Location": "Napoli, Italy",
                "whenDate": "Summer 2025",
                "pubDate": "2025-07-01",
                "link": "http://cheesydreams.com/apply",
                "entryDate": "2025-07-07",
            },
            {
                "Type": "Full-time",
                "Title": "Senior Cat Behavior Analyst",
                "Description": "Decode the mysterious ways of felines. Remote work encouraged (cats don't commute).",
                "Company": "Whiskers & Co",
                "Location": "Remote",
                "whenDate": "",
                "pubDate": "2025-06-28",
                "link": "http://whiskersco.com/careers",
                "entryDate": "2025-07-06",
            },
            {
                "Type": "Part-time",
                "Title": "Professional Bubble Wrap Popper",
                "Description": "Join our stress-relief team. Must have excellent finger dexterity and appreciation for satisfying sounds.",
                "Company": "Pop Culture Studios",
                "Location": "San Francisco, CA",
                "whenDate": "Fall 2025",
                "pubDate": "2025-07-05",
                "link": "http://popculture.com/jobs",
                "entryDate": "2025-07-05",
            },
            {
                "Type": "Co-op",
                "Title": "Unicorn Grooming Specialist",
                "Description": "Maintain the magical appearance of our unicorn fleet. Glitter allergy is a dealbreaker.",
                "Company": "Mythical Creatures Ltd",
                "Location": "Portland, OR",
                "whenDate": "Spring 2025",
                "pubDate": "2025-07-02",
                "link": "http://mythicalcreatures.com/apply",
                "entryDate": "2025-07-04",
            },
            {
                "Type": "Internship",
                "Title": "Cloud Whisperer Intern",
                "Description": "Interpret weather patterns and cloud formations. Must be comfortable working at high altitudes.",
                "Company": "Sky High Analytics",
                "Location": "Denver, CO",
                "whenDate": "Summer 2025",
                "pubDate": "2025-07-03",
                "link": "http://skyhigh.com/intern",
                "entryDate": "2025-07-03",
            }
        ]

    def test_paste_jobs_command_empty_args(self):
        """empty command arguments"""
        result = paste_jobs_command("")
        expected = {
            "role": None,
            "type": None,
            "season": None,
            "company": None,
            "location": None,
            "general_search": None,
        }
        self.assertEqual(result, expected)

    def test_paste_jobs_command_whitespace_only(self):
        """whitespace-only arguments"""
        result = paste_jobs_command("   \t  \n  ")
        expected = {
            "role": None,
            "type": None,
            "season": None,
            "company": None,
            "location": None,
            "general_search": None,
        }
        self.assertEqual(result, expected)

    def test_paste_jobs_command_bracket_notation_full(self):
        """bracket notation with all fields"""
        command = "[pizza tester] [internship] [summer] [cheesy dreams] [italy]"
        result = paste_jobs_command(command)
        expected = {
            "role": "pizza tester",
            "type": "internship",
            "season": "summer",
            "company": "cheesy dreams",
            "location": "italy",
            "general_search": None,
        }
        self.assertEqual(result, expected)

    def test_paste_jobs_command_bracket_notation_partial(self):
        """bracket notation with empty brackets"""
        command = "[cat whisperer] [] [fall] [] [remote]"
        result = paste_jobs_command(command)
        expected = {
            "role": "cat whisperer",
            "type": None,
            "season": "fall",
            "company": None,
            "location": "remote",
            "general_search": None,
        }
        self.assertEqual(result, expected)

    def test_paste_jobs_command_bracket_notation_spaces(self):
        """bracket notation with spaces in values"""
        command = "[bubble wrap popper] [part time] [fall season] [pop culture] [san francisco]"
        result = paste_jobs_command(command)
        expected = {
            "role": "bubble wrap popper",
            "type": "part time",
            "season": "fall season",
            "company": "pop culture",
            "location": "san francisco",
            "general_search": None,
        }
        self.assertEqual(result, expected)

    def test_paste_jobs_command_flag_notation_all_flags(self):
        """flag notation with all flags"""
        command = "unicorn -r grooming -t internship -s spring -c mythical -l portland"
        result = paste_jobs_command(command)
        expected = {
            "role": "grooming",
            "type": "internship",
            "season": "spring",
            "company": "mythical",
            "location": "portland",
            "general_search": "unicorn",
        }
        self.assertEqual(result, expected)

    def test_paste_jobs_command_flag_notation_long_flags(self):
        """flag notation with long flag names"""
        command = "cloud --role whisperer --type internship --season summer --company sky --location denver"
        result = paste_jobs_command(command)
        expected = {
            "role": "whisperer",
            "type": "internship",
            "season": "summer",
            "company": "sky",
            "location": "denver",
            "general_search": "cloud",
        }
        self.assertEqual(result, expected)

    def test_paste_jobs_command_flag_notation_general_search_only(self):
        """only general search terms"""
        command = "pizza quality assurance tester"
        result = paste_jobs_command(command)
        expected = {
            "role": None,
            "type": None,
            "season": None,
            "company": None,
            "location": None,
            "general_search": "pizza quality assurance tester",
        }
        self.assertEqual(result, expected)

    def test_paste_jobs_command_flag_notation_mixed_order(self):
        """flags in RaNDoM order"""
        command = "-c whiskers cat -l remote -t full-time behavior"
        result = paste_jobs_command(command)
        expected = {
            "role": None,
            "type": "full-time",
            "season": None,
            "company": "whiskers",
            "location": "remote",
            "general_search": "cat behavior",
        }
        self.assertEqual(result, expected)

    def test_filter_jobs_no_filters(self):
        """no filters"""
        filters = {}
        result = filter_jobs(self.sample_jobs, filters)
        self.assertEqual(len(result), 5)
        self.assertEqual(result, self.sample_jobs)

    def test_filter_jobs_general_search(self):
        """general search"""
        filters = {"general_search": "pizza"}
        result = filter_jobs(self.sample_jobs, filters)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["Title"], "Pizza Quality Assurance Intern")

    def test_filter_jobs_general_search_description(self):
        """matching in description"""
        filters = {"general_search": "glitter"}
        result = filter_jobs(self.sample_jobs, filters)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["Company"], "Mythical Creatures Ltd")

    def test_filter_jobs_role_filter(self):
        """role"""
        filters = {"role": "analyst"}
        result = filter_jobs(self.sample_jobs, filters)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["Title"], "Senior Cat Behavior Analyst")

    def test_filter_jobs_type_filter(self):
        """type"""
        filters = {"type": "internship"}
        result = filter_jobs(self.sample_jobs, filters)
        self.assertEqual(len(result), 2)
        titles = [job["Title"] for job in result]
        self.assertIn("Pizza Quality Assurance Intern", titles)
        self.assertIn("Cloud Whisperer Intern", titles)

    def test_filter_jobs_season_filter(self):
        """season"""
        filters = {"season": "summer"}
        result = filter_jobs(self.sample_jobs, filters)
        self.assertEqual(len(result), 2)
        titles = [job["Title"] for job in result]
        self.assertIn("Pizza Quality Assurance Intern", titles)
        self.assertIn("Cloud Whisperer Intern", titles)

    def test_filter_jobs_company_filter(self):
        """company"""
        filters = {"company": "whiskers"}
        result = filter_jobs(self.sample_jobs, filters)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["Company"], "Whiskers & Co")

    def test_filter_jobs_location_filter(self):
        """location"""
        filters = {"location": "remote"}
        result = filter_jobs(self.sample_jobs, filters)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["Location"], "Remote")

    def test_filter_jobs_multiple_filters(self):
        """multiple criteria"""
        filters = {
            "type": "Internship",
            "season": "summer"
        }
        result = filter_jobs(self.sample_jobs, filters)
        self.assertEqual(len(result), 2)
        for job in result:
            self.assertIn("Intern", job["Title"])

    def test_filter_jobs_complex_search(self):
        """role and location"""
        filters = {
            "role": "specialist",
            "location": "portland"
        }
        result = filter_jobs(self.sample_jobs, filters)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["Title"], "Unicorn Grooming Specialist")

    def test_format_jobs_message_empty_list(self):
        """empty job list"""
        result = format_jobs_message([])
        self.assertEqual(result, "💼 No jobs found matching your criteria.")

    def test_format_jobs_message_single_job(self):
        """single job return"""
        jobs = [self.sample_jobs[0]]
        result = format_jobs_message(jobs)
        
        self.assertIn("💼 **Found 1 job(s):**", result)
        self.assertIn("Pizza Quality Assurance Intern", result)
        self.assertIn("Cheesy Dreams Inc", result)
        self.assertIn("Napoli, Italy", result)
        self.assertIn("Summer 2025", result)
        self.assertIn("http://cheesydreams.com/apply", result)

    def test_format_jobs_message_multiple_jobs(self):
        """multiple job return"""
        jobs = self.sample_jobs[:3]
        result = format_jobs_message(jobs)
        
        self.assertIn("💼 **Found 3 job(s):**", result)
        self.assertIn("Pizza Quality Assurance Intern", result)
        self.assertIn("Senior Cat Behavior Analyst", result)
        self.assertIn("Professional Bubble Wrap Popper", result)

    def test_format_jobs_message_with_filters(self):
        """filter description"""
        jobs = [self.sample_jobs[0]]
        filters = {"company": "cheesy", "type": "internship"}
        result = format_jobs_message(jobs, filters)
        
        self.assertIn("(Filters: company: cheesy, type: internship)", result)

    def test_format_jobs_message_with_general_search_filter(self):
        """general search filter"""
        jobs = [self.sample_jobs[0]]
        filters = {"general_search": "pizza"}
        result = format_jobs_message(jobs, filters)
        
        self.assertIn("(Filters: search: pizza)", result)

    def test_format_jobs_message_limit_display(self):
        """message limits display to first 10 jobs"""
        # Create 15 jobs for testing
        many_jobs = self.sample_jobs * 3  # 15 jobs
        result = format_jobs_message(many_jobs)
        
        self.assertIn("💼 **Found 15 job(s):**", result)
        self.assertIn("... and 5 more jobs", result)


class TestGetJobs(unittest.TestCase):
    """Test class for getJobs function"""

    def setUp(self):
        self.sample_jobs = [
            {
                "Type": "Internship", 
                "Title": "Pizza Quality Assurance Intern",
                "Description": "Help us ensure our pizza reaches peak deliciousness.",
                "Company": "Cheesy Dreams Inc",
                "Location": "Napoli, Italy",
                "whenDate": "Summer 2025",
                "pubDate": "2025-07-01",
                "link": "http://cheesydreams.com/apply",
                "entryDate": "2025-07-07",
            },
            {
                "Type": "Full-time", 
                "Title": "Senior Cat Behavior Analyst",
                "Description": "Decode the mysterious ways of felines.",
                "Company": "Whiskers & Co",
                "Location": "Remote",
                "whenDate": "",
                "pubDate": "2025-06-28",
                "link": "http://whiskersco.com/careers",
                "entryDate": "2025-07-06",
            },
            {
                "Type": "Part-time", 
                "Title": "Professional Bubble Wrap Popper",
                "Description": "Join our stress-relief team.",
                "Company": "Pop Culture Studios",
                "Location": "San Francisco, CA",
                "whenDate": "Fall 2025",
                "pubDate": "2025-07-05",
                "link": "http://popculture.com/jobs",
                "entryDate": "2025-07-05",
            },
            {
                "Type": "Event", 
                "Title": "Company Picnic",
                "Description": "Annual company gathering",
                "Company": "Fun Corp",
                "Location": "Park",
                "whenDate": "2025-08-01",
                "pubDate": "2025-07-01",
                "link": "http://funcorp.com/picnic",
                "entryDate": "2025-07-01",
            }
        ]

    @patch("data_collections.csv_updater.extract_entries_from_csv")
    @patch("data_collections.csv_updater.remove_duplicates")
    def test_getJobs_error_handling(self, mock_remove_duplicates, mock_extract):
        """error handling in getJobs"""
        mock_extract.side_effect = Exception("CSV file not found")
        
        result = getJobs("meow.csv")
        
        self.assertEqual(result, [])

    @patch("data_collections.csv_updater.extract_entries_from_csv")
    @patch("data_collections.csv_updater.remove_duplicates")
    def test_getJobs_empty_csv(self, mock_remove_duplicates, mock_extract):
        """empty CSV file"""
        mock_extract.return_value = []
        mock_remove_duplicates.return_value = []
        
        result = getJobs("empty.csv")
        
        self.assertEqual(result, [])

if __name__ == "__main__":
    unittest.main()