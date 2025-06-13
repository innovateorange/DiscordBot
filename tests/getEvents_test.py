from data_collections.getEvents import getEvents
from unittest.mock import patch
import unittest

sample_return = {
    "entries": [
        {
            "title": "Sample Event (2023)",
            "description": "When: 2023-10-01\nLocation: Online",
            "published": "2023-09-30",
            "link": "http://example.com/event1",
        }
    ]
}


class TestGetEvents(unittest.TestCase):
    # Test that the method returns an empty list when the URL is invalid

    @patch("feedparser.parse")
    def test_invalid_url(self, mock_parse):
        mock_parse.return_value = {"entries": []}
        result = getEvents("http://invalid-url.com/rss")
        self.assertEqual(result, [])

    # Test with a valid URL (Should have more than 0 entries returned)
    @patch("feedparser.parse")
    def test_valid_url(self, mock_parse):
        mock_parse.return_value = sample_return
        result = getEvents("http://valid-url.com/rss")
        self.assertGreater(len(result), 0)

    # Test that an event has no whenDate When the description does not contain "When:"
    @patch("feedparser.parse")
    def test_no_WhenDate_in_Description(self, mock_parse):
        mock_parse.return_value = {
            "entries": [
                {
                    "title": "Sample Event (2023)",
                    "description": "Location: Online\nSome Description",
                    "published": "2023-09-30",
                    "link": "http://example.com/event1",
                }
            ]
        }
        result = getEvents("http://valid-url.com/rss")
        self.assertEqual(result[0]["whenDate"], "")
        self.assertEqual(result[0]["Description"], "Some Description")

    # Test that an event has no Location When the description does not contain "Location:"
    @patch("feedparser.parse")
    def test_no_Location_in_Description(self, mock_parse):
        mock_parse.return_value = {
            "entries": [
                {
                    "title": "Sample Event (2023)",
                    "description": "When: 2023-10-01\nSome Description",
                    "published": "2023-09-30",
                    "link": "http://example.com/event1",
                }
            ]
        }
        result = getEvents("http://valid-url.com/rss")
        self.assertEqual(result[0]["Location"], "")
        self.assertEqual(result[0]["Description"], "Some Description")

    # Test that the link is correctly extracted from the entry
    @patch("feedparser.parse")
    def test_link_extraction(self, mock_parse):
        mock_parse.return_value = sample_return
        result = getEvents("http://valid-url.com/rss")
        self.assertEqual(result[0]["link"], "http://example.com/event1")

    # Test that the published date is correctly extracted from the entry
    @patch("feedparser.parse")
    def test_pubDate_extraction(self, mock_parse):
        mock_parse.return_value = sample_return
        result = getEvents("http://valid-url.com/rss")
        self.assertEqual(result[0]["pubDate"], "2023-09-30")

    # Test that the entryDate was recorded
    @patch("feedparser.parse")
    def test_entryDate_recorded(self, mock_parse):
        mock_parse.return_value = sample_return
        result = getEvents("http://valid-url.com/rss")
        self.assertIn("entryDate", result[0])
