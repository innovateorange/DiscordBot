import unittest
from unittest.mock import MagicMock, patch

from data_collections.events import getEvents

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
    """Test suite for the getEvents function"""

    # Test that the function raises an error when the URL is malformed
    @patch("feedparser.parse")
    def test_malformed_url(self, mock_parse):
        mock_parse.side_effect = Exception("Malformed URL")
        with self.assertRaises(RuntimeError) as context:
            getEvents("http://malformed-url", "MOCK_TASK")
        self.assertIn("Failed to parse the RSS feed", str(context.exception))

    # Test that the function raises an error when the RSS feed is malformed
    @patch("feedparser.parse")
    def test_malformed_rss_feed(self, mock_parse):
        mock_parse.return_value = MagicMock(bozo=True, bozo_exception="Malformed feed")
        with self.assertRaises(RuntimeError) as context:
            getEvents("http://malformed-rss-feed.com/rss", "MOCK_TASK")
        self.assertIn("Malformed RSS feed", str(context.exception))

    # Test that the function returns an empty list when no entries are found
    @patch("feedparser.parse")
    def test_invalid_url(self, mock_parse):
        mock_parse.return_value = {"entries": []}
        result = getEvents("http://invalid-url.com/rss", "MOCK_TASK")
        self.assertEqual(result, [])

    # Test with a valid URL (Should have more than 0 entries returned)
    @patch("feedparser.parse")
    def test_valid_url(self, mock_parse):
        mock_parse.return_value = sample_return
        result = getEvents("http://valid-url.com/rss", "MOCK_TASK")
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
        result = getEvents("http://valid-url.com/rss", "MOCK_TASK")
        self.assertEqual(result[0]["whenDate"], "")
        self.assertEqual(result[0]["Description"], "Some Description")

    # Test that an event has no Location when the description lacks "Location:"
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
        result = getEvents("http://valid-url.com/rss", "MOCK_TASK")
        self.assertEqual(result[0]["Location"], "")
        self.assertEqual(result[0]["Description"], "Some Description")

    # Test that the link is correctly extracted from the entry
    @patch("feedparser.parse")
    def test_link_extraction(self, mock_parse):
        mock_parse.return_value = sample_return
        result = getEvents("http://valid-url.com/rss", "MOCK_TASK")
        self.assertEqual(result[0]["link"], "http://example.com/event1")

    # Test that the published date is correctly extracted from the entry
    @patch("feedparser.parse")
    def test_pubDate_extraction(self, mock_parse):
        mock_parse.return_value = sample_return
        result = getEvents("http://valid-url.com/rss", "MOCK_TASK")
        self.assertEqual(result[0]["pubDate"], "2023-09-30")

    # Test that the entryDate was recorded
    @patch("feedparser.parse")
    def test_entryDate_recorded(self, mock_parse):
        mock_parse.return_value = sample_return
        result = getEvents("http://valid-url.com/rss", "MOCK_TASK")
        self.assertIn("entryDate", result[0])

    # Test with multiple events in different formats
    @patch("feedparser.parse")
    def test_multiple_events_different_formats(self, mock_parse):
        """Test handling multiple events with varied formats"""
        mock_parse.return_value = {
            "entries": [
                {
                    "title": "Morning Workshop (Early Bird)",
                    "description": (
                        "When: 2024-01-15 09:00 AM\n"
                        "Location: Building A, Room 101\n"
                        "Bring your laptop"
                    ),
                    "published": "2024-01-01",
                    "link": "http://example.com/workshop",
                },
                {
                    "title": "Lunch & Learn Session",
                    "description": (
                        "Location: Cafeteria\n"
                        "When: 2024-01-15 12:00 PM\n"
                        "Free lunch provided"
                    ),
                    "published": "2024-01-01",
                    "link": "http://example.com/lunch",
                },
                {
                    "title": "Evening Networking (2024)",
                    "description": (
                        "Join us for networking\n"
                        "No specific time or location"
                    ),
                    "published": "2024-01-01",
                    "link": "http://example.com/networking",
                },
            ]
        }
        result = getEvents("http://valid-url.com/rss", "WORKSHOP")

        self.assertEqual(len(result), 3)
        # First event - standard format
        self.assertEqual(result[0]["Title"], "Morning Workshop")
        self.assertEqual(result[0]["whenDate"], "2024-01-15 09:00 AM")
        self.assertEqual(result[0]["Location"], "Building A, Room 101")

        # Second event - reversed order
        self.assertEqual(result[1]["Title"], "Lunch & Learn Session")
        self.assertEqual(result[1]["whenDate"], "2024-01-15 12:00 PM")
        self.assertEqual(result[1]["Location"], "Cafeteria")

        # Third event - no When/Location
        self.assertEqual(result[2]["Title"], "Evening Networking")
        self.assertEqual(result[2]["whenDate"], "")
        self.assertEqual(result[2]["Location"], "")

    # Test with Unicode and special characters
    @patch("feedparser.parse")
    def test_unicode_and_special_characters(self, mock_parse):
        """Test handling of Unicode and special characters in all fields"""
        mock_parse.return_value = {
            "entries": [
                {
                    "title": "Conférence Internationale 🌍 (2024)",
                    "description": (
                        "When: 15 janvier 2024 à 14h30\n"
                        "Location: Café Münchën & Co.\n"
                        "Déscription avec des caractères spéciaux: €, ©, ™"
                    ),
                    "published": "2024-01-01",
                    "link": "http://example.com/événement",
                }
            ]
        }
        result = getEvents("http://valid-url.com/rss", "international")

        self.assertEqual(result[0]["Title"], "Conférence Internationale 🌍")
        self.assertEqual(result[0]["whenDate"], "15 janvier 2024 à 14h30")
        self.assertEqual(result[0]["Location"], "Café Münchën & Co.")
        self.assertIn("€", result[0]["Description"])
        self.assertIn("©", result[0]["Description"])

    # Test with HTML entities in description
    @patch("feedparser.parse")
    def test_html_entities_handling(self, mock_parse):
        """Test proper handling of HTML entities"""
        mock_parse.return_value = {
            "entries": [
                {
                    "title": "Web &amp; Mobile Development",
                    "description": (
                        "When: 2024-01-15 &lt;Morning&gt;\n"
                        "Location: Room &quot;A&quot; &amp; &quot;B&quot;\n"
                        "&lt;p&gt;Description with HTML&lt;/p&gt;"
                    ),
                    "published": "2024-01-01",
                    "link": "http://example.com/web",
                }
            ]
        }
        result = getEvents("http://valid-url.com/rss", "tech")

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)

    # Test error propagation with custom exception
    @patch("feedparser.parse")
    def test_error_propagation(self, mock_parse):
        """Test that exceptions are properly wrapped in RuntimeError"""
        mock_parse.side_effect = ValueError("Invalid feed format")

        with self.assertRaises(RuntimeError) as context:
            getEvents("http://invalid.com/rss", "test")

        self.assertIn("Failed to parse the RSS feed", str(context.exception))
        self.assertIn("Invalid feed format", str(context.exception))

    # Test with extremely long text fields
    @patch("feedparser.parse")
    def test_extremely_long_fields(self, mock_parse):
        """Test handling of very long text in fields"""
        long_title = "Event " + "X" * 1000
        long_when = "2024-01-15 " + "details " * 100
        long_location = "Building " + "A" * 500
        long_description = "Description " * 1000

        mock_parse.return_value = {
            "entries": [
                {
                    "title": long_title + " (2024)",
                    "description": (
                        f"When: {long_when}\n"
                        f"Location: {long_location}\n"
                        f"{long_description}"
                    ),
                    "published": "2024-01-01",
                    "link": "http://example.com/long",
                }
            ]
        }
        result = getEvents("http://valid-url.com/rss", "test")

        self.assertEqual(result[0]["Title"], long_title)
        self.assertEqual(result[0]["whenDate"], long_when.strip())
        self.assertEqual(result[0]["Location"], long_location.strip())
        self.assertIn("Description", result[0]["Description"])

    # Test with None values in different fields
    @patch("feedparser.parse")
    def test_none_values_in_fields(self, mock_parse):
        """Test handling of None values in various fields"""
        mock_parse.return_value = {
            "entries": [
                {
                    "title": None,
                    "description": None,
                    "published": None,
                    "link": None,
                }
            ]
        }
        result = getEvents("http://valid-url.com/rss", "test")

        self.assertEqual(len(result), 1)
        self.assertIn("Title", result[0])
        self.assertIn("Description", result[0])
        self.assertIn("pubDate", result[0])
        self.assertIn("link", result[0])

    # Test with mixed data types
    @patch("feedparser.parse")
    def test_mixed_data_types(self, mock_parse):
        """Test handling of unexpected data types in fields"""
        mock_parse.return_value = {
            "entries": [
                {
                    "title": ["List", "Title"],
                    "description": {"key": "value"},
                    "published": 12345,
                    "link": True,
                }
            ]
        }
        # Should handle gracefully without crashing
        result = getEvents("http://valid-url.com/rss", "test")
        self.assertIsNotNone(result)

    # Test subType case variations
    @patch("feedparser.parse")
    def test_subtype_case_variations(self, mock_parse):
        """Test that subType is always lowercase regardless of input"""
        mock_parse.return_value = sample_return

        test_cases = ["UPPERCASE", "lowercase", "MiXeDcAsE", "CamelCase", "snake_case"]
        for subtype in test_cases:
            result = getEvents("http://valid-url.com/rss", subtype)
            self.assertEqual(result[0]["subType"], subtype.lower())

    # Test When/Location extraction with edge cases
    @patch("feedparser.parse")
    def test_when_location_extraction_edge_cases(self, mock_parse):
        """Test When/Location extraction with various edge cases"""
        test_cases = [
            {
                "description": "When:\nLocation:\nEmpty fields",
                "expected_when": "",
                "expected_location": "",
            },
            {
                "description": "When: \nLocation: \nSpaces only",
                "expected_when": "",
                "expected_location": "",
            },
            {
                "description": (
                    "When: Time with colon 10:30 AM\n"
                    "Location: Address: 123 Main St"
                ),
                "expected_when": "Time with colon 10:30 AM",
                "expected_location": "Address: 123 Main St",
            },
            {
                "description": "WHEN: UPPERCASE\nLOCATION: UPPERCASE",
                "expected_when": "",  # Case sensitive extraction
                "expected_location": "",
            },
        ]

        for i, test_case in enumerate(test_cases):
            mock_parse.return_value = {
                "entries": [
                    {
                        "title": f"Event {i}",
                        "description": test_case["description"],
                        "published": "2024-01-01",
                        "link": f"http://example.com/event{i}",
                    }
                ]
            }
            result = getEvents("http://valid-url.com/rss", "test")
            self.assertEqual(
                result[0]["whenDate"],
                test_case["expected_when"],
                f"Failed for test case {i}"
            )
            self.assertEqual(
                result[0]["Location"],
                test_case["expected_location"],
                f"Failed for test case {i}"
            )

    # Test title parentheses removal with nested parentheses
    @patch("feedparser.parse")
    def test_title_nested_parentheses(self, mock_parse):
        """Test title processing with nested and multiple parentheses"""
        test_cases = [
            ("Event (Part 1) (2024)", "Event (Part 1)"),
            ("Event ((nested))", "Event"),
            ("(Start) Event (End)", "(Start) Event"),
            ("Event ()", "Event"),
            ("(Event)", ""),
        ]

        for input_title, expected_title in test_cases:
            mock_parse.return_value = {
                "entries": [
                    {
                        "title": input_title,
                        "description": "",
                        "published": "2024-01-01",
                        "link": "http://example.com/event",
                    }
                ]
            }
            result = getEvents("http://valid-url.com/rss", "test")
            self.assertEqual(
                result[0]["Title"], expected_title, f"Failed for input: {input_title}"
            )

    # Test description regex with complex patterns
    @patch("feedparser.parse")
    def test_description_regex_complex_patterns(self, mock_parse):
        """Test description regex with complex When/Location patterns"""
        mock_parse.return_value = {
            "entries": [
                {
                    "title": "Complex Event",
                    "description": """Start text
When: January 15, 2024
Additional When: info on next line
Location: Main Hall
Additional Location: info
when: lowercase should be removed
location: lowercase should be removed
Middle text
When: Another date
End text""",
                    "published": "2024-01-01",
                    "link": "http://example.com/complex",
                }
            ]
        }
        result = getEvents("http://valid-url.com/rss", "test")

        # Check that only lines starting with When:/Location: are removed
        description = result[0]["Description"]
        self.assertIn("Start text", description)
        self.assertIn("Middle text", description)
        self.assertIn("End text", description)
        self.assertNotIn("When:", description)
        self.assertNotIn("Location:", description)
        self.assertNotIn("when:", description)
        self.assertNotIn("location:", description)

    # Test entryDate timezone handling
    @patch("feedparser.parse")
    def test_entry_date_timezone(self, mock_parse):
        """Test that entryDate includes proper UTC timezone"""
        import datetime

        mock_parse.return_value = sample_return

        # Capture time before and after
        before = datetime.datetime.now(tz=datetime.timezone.utc)
        result = getEvents("http://valid-url.com/rss", "test")
        after = datetime.datetime.now(tz=datetime.timezone.utc)

        entry_date = result[0]["entryDate"]
        self.assertIsInstance(entry_date, datetime.datetime)
        self.assertEqual(entry_date.tzinfo, datetime.timezone.utc)
        self.assertGreaterEqual(entry_date, before)
        self.assertLessEqual(entry_date, after)

    # Test Company field is always empty string
    @patch("feedparser.parse")
    def test_company_field_always_empty(self, mock_parse):
        """Test that Company field is consistently empty"""
        mock_parse.return_value = {
            "entries": [
                {
                    "title": "Event 1",
                    "description": "Company: ABC Corp",
                    "published": "2024-01-01",
                    "link": "http://example.com/1",
                },
                {
                    "title": "Event 2",
                    "description": "Employer: XYZ Inc",
                    "published": "2024-01-01",
                    "link": "http://example.com/2",
                },
                {
                    "title": "Event 3",
                    "description": "Organization: 123 Ltd",
                    "published": "2024-01-01",
                    "link": "http://example.com/3",
                },
            ]
        }
        result = getEvents("http://valid-url.com/rss", "test")

        for event in result:
            self.assertEqual(event["Company"], "")

    # Test with feedparser returning different structures
    @patch("feedparser.parse")
    def test_feedparser_different_structures(self, mock_parse):
        """Test handling of different feedparser return structures"""
        # Test with FeedParserDict-like structure
        mock_feed = MagicMock()
        mock_feed.get.return_value = [
            {
                "title": "Event",
                "description": "When: 2024-01-15\nLocation: Online",
                "published": "2024-01-01",
                "link": "http://example.com/event",
            }
        ]
        mock_parse.return_value = mock_feed

        result = getEvents("http://valid-url.com/rss", "test")
        self.assertIsNotNone(result)

    # Test with malformed RSS that sets bozo but still has entries
    @patch("feedparser.parse")
    def test_bozo_with_entries(self, mock_parse):
        """Test that bozo=True raises error even if entries exist"""
        mock_parse.return_value = MagicMock(
            bozo=True,
            bozo_exception="XML parsing error",
            entries=[
                {
                    "title": "Event",
                    "description": "Description",
                    "published": "2024-01-01",
                    "link": "http://example.com/event",
                }
            ],
        )

        with self.assertRaises(RuntimeError) as context:
            getEvents("http://malformed.com/rss", "test")
        self.assertIn("Malformed RSS feed", str(context.exception))

    # Test empty string URL
    @patch("feedparser.parse")
    def test_empty_string_url(self, mock_parse):
        """Test with empty string URL"""
        mock_parse.side_effect = Exception("Invalid URL")

        with self.assertRaises(RuntimeError) as context:
            getEvents("", "test")
        self.assertIn("Failed to parse", str(context.exception))

    # Test with whitespace-only fields
    @patch("feedparser.parse")
    def test_whitespace_only_fields(self, mock_parse):
        """Test handling of whitespace-only fields"""
        mock_parse.return_value = {
            "entries": [
                {
                    "title": "   \t\n   ",
                    "description": "   \t\n   ",
                    "published": "   \t\n   ",
                    "link": "   \t\n   ",
                }
            ]
        }
        result = getEvents("http://valid-url.com/rss", "test")

        self.assertEqual(result[0]["Title"], "")
        self.assertEqual(result[0]["Description"], "")

    # Test concurrent processing simulation
    @patch("feedparser.parse")
    def test_concurrent_processing_simulation(self, mock_parse):
        """Test that function handles concurrent calls correctly"""
        mock_parse.return_value = sample_return

        results = []
        for i in range(5):
            result = getEvents(f"http://feed{i}.com/rss", f"type{i}")
            results.append(result)

        self.assertEqual(len(results), 5)
        for i, result in enumerate(results):
            self.assertEqual(result[0]["subType"], f"type{i}")


class TestGetEventsEdgeCases(unittest.TestCase):
    """Additional edge case tests for getEvents function"""

    @patch("feedparser.parse")
    def test_when_location_multiline_values(self, mock_parse):
        """Test When and Location fields with multiline values"""
        mock_parse.return_value = {
            "entries": [
                {
                    "title": "Multi-day Event",
                    "description": """When: January 15-17, 2024
9:00 AM - 5:00 PM each day
Location: Convention Center
123 Main Street
Suite 500
Additional details here""",
                    "published": "2024-01-01",
                    "link": "http://example.com/multiday",
                }
            ]
        }
        result = getEvents("http://valid-url.com/rss", "conference")

        # Should only get first line after When: and Location:
        self.assertEqual(result[0]["whenDate"], "January 15-17, 2024")
        self.assertEqual(result[0]["Location"], "Convention Center")
        self.assertIn("Additional details", result[0]["Description"])

    @patch("feedparser.parse")
    def test_description_field_after_stripping(self, mock_parse):
        """Test description field content after When/Location removal"""
        mock_parse.return_value = {
            "entries": [
                {
                    "title": "Event",
                    "description": """When: 2024-01-15
Location: Online
When: This should stay as it's not at line start
The event will cover Location: topics
Regular description text""",
                    "published": "2024-01-01",
                    "link": "http://example.com/event",
                }
            ]
        }
        result = getEvents("http://valid-url.com/rss", "test")

        description = result[0]["Description"]
        self.assertIn("This should stay", description)
        self.assertIn("The event will cover Location: topics", description)
        self.assertIn("Regular description text", description)

    @patch("feedparser.parse")
    def test_special_characters_in_regex(self, mock_parse):
        """Test handling of regex special characters in content"""
        mock_parse.return_value = {
            "entries": [
                {
                    "title": "Event with $pecial (Ch@rs) [2024]",
                    "description": (
                        "When: 2024-01-15 (EST) [Tentative]\n"
                        "Location: Room A|B * Conference Center\n"
                        "$100 entry fee. Questions? Email us."
                    ),
                    "published": "2024-01-01",
                    "link": "http://example.com/special",
                }
            ]
        }
        result = getEvents("http://valid-url.com/rss", "test")

        # Title should have ending parentheses content removed
        self.assertNotIn("[2024]", result[0]["Title"])
        # Special characters in When/Location should be preserved
        self.assertIn("(EST)", result[0]["whenDate"])
        self.assertIn("|", result[0]["Location"])
        self.assertIn("$100", result[0]["Description"])

    @patch("feedparser.parse")
    def test_performance_with_many_entries(self, mock_parse):
        """Test performance with large number of entries"""
        entries = []
        for i in range(1000):
            entries.append({
                "title": f"Event {i} (2024)",
                "description": (
                    f"When: 2024-01-{(i % 28) + 1:02d}\n"
                    f"Location: Room {i}\n"
                    f"Description for event {i}"
                ),
                "published": "2024-01-01",
                "link": f"http://example.com/event{i}",
            })
        mock_parse.return_value = {"entries": entries}

        import time
        start_time = time.time()
        result = getEvents("http://valid-url.com/rss", "bulk")
        end_time = time.time()

        self.assertEqual(len(result), 1000)
        # Should process 1000 entries reasonably quickly (< 1 second)
        self.assertLess(end_time - start_time, 1.0)

    @patch("feedparser.parse")
    def test_when_location_case_preservation(self, mock_parse):
        """Test that When/Location values preserve original case"""
        mock_parse.return_value = {
            "entries": [
                {
                    "title": "Event",
                    "description": (
                        "When: JANUARY 15, 2024 AT 3PM\n"
                        "Location: McDonalds Conference Room\n"
                        "Details"
                    ),
                    "published": "2024-01-01",
                    "link": "http://example.com/event",
                }
            ]
        }
        result = getEvents("http://valid-url.com/rss", "test")

        self.assertEqual(result[0]["whenDate"], "JANUARY 15, 2024 AT 3PM")
        self.assertEqual(result[0]["Location"], "McDonalds Conference Room")

    @patch("feedparser.parse")
    def test_duplicate_when_location_fields(self, mock_parse):
        """Test handling of duplicate When/Location fields"""
        mock_parse.return_value = {
            "entries": [
                {
                    "title": "Event",
                    "description": """When: First Date
When: Second Date
When: Third Date
Location: First Location
Location: Second Location
Description text""",
                    "published": "2024-01-01",
                    "link": "http://example.com/event",
                }
            ]
        }
        result = getEvents("http://valid-url.com/rss", "test")

        # Should get first occurrence only
        self.assertEqual(result[0]["whenDate"], "First Date")
        self.assertEqual(result[0]["Location"], "First Location")

    @patch("feedparser.parse")
    def test_entries_as_generator(self, mock_parse):
        """Test handling of entries as a generator instead of list"""
        def entry_generator():
            yield {
                "title": "Event 1",
                "description": "When: 2024-01-15\nLocation: Online",
                "published": "2024-01-01",
                "link": "http://example.com/1",
            }
            yield {
                "title": "Event 2",
                "description": "When: 2024-01-16\nLocation: Onsite",
                "published": "2024-01-01",
                "link": "http://example.com/2",
            }

        mock_parse.return_value = {"entries": entry_generator()}

        result = getEvents("http://valid-url.com/rss", "test")
        self.assertEqual(len(result), 2)

    @patch("feedparser.parse")
    def test_numeric_subtype(self, mock_parse):
        """Test handling of numeric subType values"""
        mock_parse.return_value = sample_return

        # Test with numeric string
        result = getEvents("http://valid-url.com/rss", "123")
        self.assertEqual(result[0]["subType"], "123")

        # Test with mixed alphanumeric
        result = getEvents("http://valid-url.com/rss", "type123")
        self.assertEqual(result[0]["subType"], "type123")

    @patch("feedparser.parse")
    def test_url_in_description(self, mock_parse):
        """Test preservation of URLs in description"""
        mock_parse.return_value = {
            "entries": [
                {
                    "title": "Webinar",
                    "description": (
                        "When: 2024-01-15\n"
                        "Location: https://zoom.us/j/123456789\n"
                        "Join at https://example.com/register"
                    ),
                    "published": "2024-01-01",
                    "link": "http://example.com/webinar",
                }
            ]
        }
        result = getEvents("http://valid-url.com/rss", "webinar")

        self.assertEqual(result[0]["Location"], "https://zoom.us/j/123456789")
        self.assertIn("https://example.com/register", result[0]["Description"])


# Add test execution
if __name__ == "__main__":
    unittest.main()