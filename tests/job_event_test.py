"""Unittests for job_event.py"""
import tempfile
import unittest
from unittest.mock import patch

from data_processing.job_event import (  # noqa: E501
    filter_jobs,
    get_jobs,
)


class TestJobEventFunctions(unittest.TestCase):
    """
    Tests for filter_jobs function
    """

    def setUp(self):
        self.sample_jobs = [
            {
                "Type": "Internship",
                "subType": "",
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
                "subType": "",
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
                "subType": "",
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
                "subType": "",
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
                "subType": "",
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

    def test_filter_jobs_no_filters(self):
        """
        Test that filter_jobs will return correct amount of jobs given no filters
        """
        filters = ""
        result = filter_jobs(self.sample_jobs, filters)
        self.assertEqual(len(result), 5)
        self.assertEqual(result, self.sample_jobs)

    def test_filter_jobs_role_filter(self):
        """
        Test that role filters resulting from inputs in command line will
            look through Title column of csv
        """
        filters = "analyst"
        result = filter_jobs(self.sample_jobs, filters)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["Title"], "Senior Cat Behavior Analyst")

    def test_filter_jobs_season_filter(self):
        """
        Test that season filters resulting from inputs in command line will
            look through whenDate column of csv
        """
        filters = "summer"
        result = filter_jobs(self.sample_jobs, filters)
        self.assertEqual(len(result), 2)
        titles = [job["Title"] for job in result]
        self.assertIn("Pizza Quality Assurance Intern", titles)
        self.assertIn("Cloud Whisperer Intern", titles)

    def test_filter_jobs_company_filter(self):
        """
        Test that company filters resulting from inputs in command line will
            look through Company column of csv
        """
        filters = "whiskers"
        result = filter_jobs(self.sample_jobs, filters)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["Company"], "Whiskers & Co")

    def test_filter_jobs_location_filter(self):
        """
        Test that location filters resulting from inputs in command line will
            look through Location column of csv
        """
        filters = "remote"
        result = filter_jobs(self.sample_jobs, filters)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["Location"], "Remote")

    def test_filter_jobs_multiple_filters(self):
        # TODO: implement test for multiple filters
        pass

    def test_filter_jobs_case_insensitive_matching(self):
        """
        Test that filter_jobs performs case-insensitive matching
        """
        # Test uppercase filter
        filters = "PIZZA"
        result = filter_jobs(self.sample_jobs, filters)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["Title"], "Pizza Quality Assurance Intern")

        # Test mixed case filter
        filters = "WhIsKeRs"
        result = filter_jobs(self.sample_jobs, filters)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["Company"], "Whiskers & Co")

    # ... remaining tests unchanged ...


class TestGetJobs(unittest.TestCase):

    def tearDown(self):
        """Clean up temporary files after each test"""
        import os
        if hasattr(self, "temp_file_path") and os.path.exists(self.temp_file_path):
            from contextlib import suppress
            with suppress(BaseException):
                os.remove(self.temp_file_path)

    """
    Tests for get_jobs function
    """

    def setUp(self):
        """
        Create a temporary CSV file for testing
        """
        with tempfile.NamedTemporaryFile(
            delete=False, mode="w", suffix=".csv", encoding="utf8"
        ) as temp_file:
            temp_file.write(
                "Type,subType,Title,Description,Company,Location,whenDate,pubDate,link,entryDate\n"
            )
            temp_file.write(
                "Internship,,Pizza Intern,Help wanted,Cheesy Dreams Inc,Italy,Summer 2025,2025-07-01,http://cheesydreams.com/apply,2025-07-07\n"  # noqa: E501
            )
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
        # TODO: implement test for get_jobs filter-matching behavior
        pass

    @patch("data_collections.csv_updater.extract_entries_from_csv")
    def test_get_jobs_filters_correct_types(self, mock_extract):
        """
        Test that get_jobs only includes job-related types
        """
        mock_extract.return_value = [
            {"Type": "Internship", "Title": "Intern 1"},
            {"Type": "job", "Title": "Job 1"},
            {"Type": "Full-time intern", "Title": "FT Intern"},
            {"Type": "Event", "Title": "Not a job"},
            {"Type": "Workshop", "Title": "Also not a job"},
            {"Type": "JOB OPENING", "Title": "Job 2"},
            {"Type": "internship position", "Title": "Intern 2"},
        ]
        results = get_jobs(self.temp_file_path)

        # Should include only job-related types
        self.assertEqual(len(results), 5)
        titles = [r["Title"] for r in results]
        self.assertIn("Intern 1", titles)
        self.assertIn("Job 1", titles)
        self.assertIn("FT Intern", titles)
        self.assertIn("Job 2", titles)
        self.assertIn("Intern 2", titles)
        self.assertNotIn("Not a job", titles)
        self.assertNotIn("Also not a job", titles)

    # ... remaining tests unchanged ...


if __name__ == "__main__":
    unittest.main()