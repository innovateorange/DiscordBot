import unittest
from unittest.mock import MagicMock, patch

from data_collections.internships import getInternships

sample_return = {
    "entries": [
        {
            "title": "Sample Internship at This Awesome Place",
            "description": "Employer: This Awesome Place \n\n"
            "Expires: 08/01/2025 \n\n"
            "This is a description"
            "Location: Boston, MA, Detriot, MI "
            "More information is here for some reason",
            "published": "Wed, 29 Jan 2025 20:13:44 +0000",
            "link": "http://example.com/event1",
        }
    ]
}


class TestGetInternships(unittest.TestCase):
    """Test suite for the getInternships method"""

    # Test that the function raises an error when the URL is malformed
    @patch("feedparser.parse")
    def test_malformed_url(self, mock_parse):
        mock_parse.side_effect = Exception("Malformed URL")
        with self.assertRaises(RuntimeError) as context:
            getInternships("http://malformed-url")
        self.assertIn("Failed to parse the RSS feed", str(context.exception))

    # Test that the function raises an error when the RSS feed is malformed
    @patch("feedparser.parse")
    def test_malformed_rss_feed(self, mock_parse):
        mock_parse.return_value = MagicMock(bozo=True, bozo_exception="Malformed feed")
        with self.assertRaises(RuntimeError) as context:
            getInternships("http://malformed-rss-feed.com/rss")
        self.assertIn("Malformed RSS feed", str(context.exception))

    # Test that the function returns an empty list when no entries are found
    @patch("feedparser.parse")
    def test_invalid_url(self, mock_parse):
        mock_parse.return_value = {"entries": []}
        result = getInternships("http://invalid-url.com/rss")
        self.assertEqual(result, [])

    # Test with a valid URL (Should have more than 0 entries returned)
    @patch("feedparser.parse")
    def test_valid_url(self, mock_parse):
        mock_parse.return_value = sample_return
        result = getInternships("http://valid-url.com/rss")
        self.assertGreater(len(result), 0)

    # Test successful extraction
    @patch("feedparser.parse")
    def test_successful_title_extraction(self, mock_parse):
        mock_parse.return_value = sample_return
        result = getInternships("http://valid-url.com/rss")
        self.assertEqual(result[0]["Type"], "Internship")
        self.assertEqual(result[0]["subType"], "")
        self.assertEqual(result[0]["Title"], "Sample Internship")
        self.assertEqual(result[0]["Company"], "This Awesome Place")
        self.assertEqual(result[0]["Description"], "")
        self.assertEqual(result[0]["whenDate"], "08/01/2025")
        self.assertEqual(result[0]["pubDate"], "Wed, 29 Jan 2025 20:13:44 +0000")
        self.assertIn("Boston, MA", result[0]["Location"])
        self.assertEqual(result[0]["link"], "http://example.com/event1")
