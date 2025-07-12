"""Unittests for job_event.py"""

import unittest
from unittest.mock import patch
import tempfile
from data_processing.job_event import (  # noqa: E501
    paste_jobs_command,
    filter_jobs,
    format_jobs_message,
    get_jobs,
)


class TestJobEventFunctions(unittest.TestCase):
    """
    Tests for paste_jobs_command
    """
    def setUp(self):
        self.sample_jobs = [
            {
                "Type": "Internship",
                "Title": "Pizza Quality Assurance Intern",
                "Description": "Help us ensure our pizza reaches peak deliciousness. Must love cheese and have strong opinions about pineapple.",  # noqa: E501
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
                "Description": "Decode the mysterious ways of felines. Remote work encouraged (cats don't commute).",  # noqa: E501
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
                "Description": "Join our stress-relief team. Must have excellent finger dexterity and appreciation for satisfying sounds.",  # noqa: E501
                "Company": "Pop Culture Studios",
                "Location": "San Francisco, CA",
                "whenDate": "Fall 2025",
                "pubDate": "2025-07-05",
                "link": "http://popculture.com/jobs",
                "entryDate": "2025-07-05",
            },
            {
                "Type": "Internship",
                "Title": "Unicorn Grooming Specialist",
                "Description": "Maintain the magical appearance of our unicorn fleet. Glitter allergy is a dealbreaker.",  # noqa: E501
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
                "Description": "Interpret weather patterns and cloud formations. Must be comfortable working at high altitudes.",  # noqa: E501
                "Company": "Sky High Analytics",
                "Location": "Denver, CO",
                "whenDate": "Summer 2025",
                "pubDate": "2025-07-03",
                "link": "http://skyhigh.com/intern",
                "entryDate": "2025-07-03",
            },
        ]
        
    def test_paste_jobs_command_empty_args(self):
        """
        Test that no imputs in command line will return no filters
        """
        result = paste_jobs_command("")
        expected = ""
        self.assertEqual(result, expected)

    def test_paste_jobs_command_search(self):
        """
        Test command line inputs to return as filters
        """
        command = "pizza quality assurance tester"
        result = paste_jobs_command(command)
        expected = "pizza quality assurance tester"
        self.assertEqual(result, expected)

    def test_filter_jobs_no_filters(self):
        """
        Test that filter_jobs will return correct amount of jobs given no filters
        """
        filters = ""
        result = filter_jobs(self.sample_jobs, filters)
        self.assertEqual(len(result), 5)
        self.assertEqual(result, self.sample_jobs)

    def test_filter_jobs_general_search(self):
        """
        Test that general search terms will look through Title column of csv
        """
        filters = "pizza"
        result = filter_jobs(self.sample_jobs, filters)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["Title"], "Pizza Quality Assurance Intern")

    def test_filter_jobs_general_search_description(self):
        """
        Test that general search terms will look through Company column of csv
        """
        filters = "glitter"
        result = filter_jobs(self.sample_jobs, filters)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["Company"], "Mythical Creatures Ltd")

    def test_filter_jobs_role_filter(self):
        """
        Test that role filters resulting from flags in command line will
            look through Title column of csv
        """
        filters = "analyst"
        result = filter_jobs(self.sample_jobs, filters)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["Title"], "Senior Cat Behavior Analyst")

    def test_filter_jobs_season_filter(self):
        """
        Test that season filters resulting from flags in command line will
            look through Season column of csv
        """
        filters = "summer"
        result = filter_jobs(self.sample_jobs, filters)
        self.assertEqual(len(result), 2)
        titles = [job["Title"] for job in result]
        self.assertIn("Pizza Quality Assurance Intern", titles)
        self.assertIn("Cloud Whisperer Intern", titles)

    def test_filter_jobs_company_filter(self):
        """
        Test that company filters resulting from flags in command line will
            look through Company column of csv
        """
        filters = "whiskers"
        result = filter_jobs(self.sample_jobs, filters)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["Company"], "Whiskers & Co")

    def test_filter_jobs_location_filter(self):
        """
        Test that location filters resulting from flags in command line will
            look through Location column of csv
        """
        filters = "remote"
        result = filter_jobs(self.sample_jobs, filters)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["Location"], "Remote")

    def test_filter_jobs_multiple_filters(self):
        """
        Test that multiple filters from flags in command line will
            accurately look through respective columns of csv
        """
        filters = "Intern summer"
        result = filter_jobs(self.sample_jobs, filters)
        self.assertEqual(len(result), 2)
        for job in result:
            self.assertIn("Intern", job["Title"])

    def test_filter_jobs_complex_search(self):
        """
        Test that multiple filters from flags in command line will
            accurately look through respective columns of csv
        """
        filters = "whiskers portland"
        result = filter_jobs(self.sample_jobs, filters)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["Company"], "Whiskers & Co")
        self.assertEqual(result[1]["Title"], "Unicorn Grooming Specialist")

    def test_format_jobs_message_empty_list(self):
        """
        Test that given the input of no matching jobs,
            response will be printed
        """
        result = format_jobs_message([], "")
        self.assertEqual(result, "💼 No jobs found matching your criteria.")

    def test_format_jobs_message_single_job(self):
        """
        Test that given the input of a singular matching job,
            response will be printed
        """
        jobs = [self.sample_jobs[0]]
        result = format_jobs_message(jobs, "")
        self.assertIn("💼 **Found 1 job(s):**", result)
        self.assertIn("Pizza Quality Assurance Intern", result)
        self.assertIn("Cheesy Dreams Inc", result)
        self.assertIn("Napoli, Italy", result)
        self.assertIn("Summer 2025", result)
        self.assertIn("http://cheesydreams.com/apply", result)

    def test_format_jobs_message_multiple_jobs(self):
        """
        Test that given the input of multiple matching jobs,
            response will be printed
        """
        jobs = self.sample_jobs[:3]
        result = format_jobs_message(jobs, "")
        self.assertIn("💼 **Found 3 job(s):**", result)
        self.assertIn("Pizza Quality Assurance Intern", result)
        self.assertIn("Senior Cat Behavior Analyst", result)
        self.assertIn("Professional Bubble Wrap Popper", result)

    def test_format_jobs_message_with_filters(self):
        """
        Test that given filters in command line,
            response will print the filters
        """
        jobs = [self.sample_jobs[0]]
        filters = "cheesy internship"
        result = format_jobs_message(jobs, filters)
        self.assertIn("(Filters: cheesy internship)", result)

    def test_format_jobs_message_with_general_search_filter(self):
        """
        Test that given general search terms in command line,
            response will print the filters
        """
        jobs = [self.sample_jobs[0]]
        filters = "pizza"
        result = format_jobs_message(jobs, filters)
        self.assertIn("(Filters: pizza)", result)

    def test_format_jobs_message_limit_display(self):
        """
        Test that the message is limitted to 10 jobs per !job event
        """
        many_jobs = self.sample_jobs * 3
        result = format_jobs_message(many_jobs, "")
        self.assertIn("💼 **Found 15 job(s):**", result)
        self.assertIn("... and 5 more jobs", result)


class TestGetJobs(unittest.TestCase):
    """
    Tests for get_jobs function
    """

    def setUp(self):
        # Create a temporary CSV file for testing
        with tempfile.NamedTemporaryFile(
            delete=False, mode="w", suffix=".csv", encoding="utf8"
        ) as temp_file:
            temp_file.write(
                "Type,Title,Description,Company,Location,whenDate,pubDate,link,entryDate\n"
            )
            temp_file.write(
                "Internship,Pizza Intern,Help wanted,Cheesy Dreams Inc,Italy,Summer 2025,2025-07-01,http://cheesydreams.com/apply,2025-07-07\n"
            )  # noqa: E501
            self.temp_file_path = temp_file.name

    @patch("data_collections.csv_updater.extract_entries_from_csv")
    def test_get_jobs_error_handling(self, mock_extract):
        """
        Test for error handling given not found csv file
        """
        mock_extract.side_effect = RuntimeError("No such file or directory")
        with self.assertRaises(RuntimeError):
            get_jobs("missing.csv")

    @patch("data_collections.csv_updater.extract_entries_from_csv")
    def test_get_jobs_filter_find_match(self, mock_extract):
        """
        Test for successful filtering of jobs
        """
        mock_extract.return_value = [
            {
                "Type": "Internship",
                "Title": "Test Job",
                "Company": "Test Co",
                "Location": "Test City",
                "Description": "Test description",
            }
        ]
        results = get_jobs(self.temp_file_path)
        self.assertEqual(len(results), 1)


if __name__ == "__main__":
    unittest.main()
