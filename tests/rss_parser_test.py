#!/usr/bin/env python3
"""
Comprehensive unit tests for RSS Parser module

Testing Framework: unittest (Python standard library)
Mocking: unittest.mock

This test suite covers:
- Happy path scenarios for job and internship parsing
- Edge cases including malformed data, missing fields, and invalid inputs
- Error handling for network issues and feed parsing failures
- Location extraction with state validation
- Data validation and sanitization
- Performance testing with large feeds
- Integration-like scenarios with realistic data
"""

import unittest
from unittest.mock import MagicMock, patch

from data_collections.rss_parser import (
    getInternships,
    getJobs,
    parse_rss_feed,
    extract_locations,
)

# Sample data for testing
sample_internship_return = {
    "entries": [
        {
            "title": "Sample Internship at This Awesome Place",
            "description": "Employer: This Awesome Place \n\n"
            "Expires: 08/01/2025 \n\n"
            "This is a description"
            "Location: Boston, MA, Detroit, MI "
            "More information is here for some reason",
            "published": "Wed, 29 Jan 2025 20:13:44 +0000",
            "link": "http://example.com/event1",
        }
    ]
}

sample_job_return = {
    "entries": [
        {
            "title": "Sample Job at This Awesome Place",
            "description": "Employer: This Awesome Place \n\n"
            "Expires: 08/01/2025 \n\n"
            "This is a description"
            "Location: Boston, MA, Detroit, MI, Remote, Hybrid "
            "More information is here for some reason",
            "published": "Wed, 29 Jan 2025 20:13:44 +0000",
            "link": "http://example.com/event1",
        }
    ]
}


class TestParseRSSFeed(unittest.TestCase):
    """Test suite for the parse_rss_feed function"""

    # Test that the function raises an error when the URL is malformed
    @patch("feedparser.parse")
    def test_malformed_url(self, mock_parse):
        mock_parse.side_effect = Exception("Malformed URL")
        with self.assertRaises(RuntimeError) as context:
            parse_rss_feed("http://malformed-url", "Job")
        self.assertIn("Failed to parse the RSS feed", str(context.exception))

    # Test that the function raises an error when the RSS feed is malformed
    @patch("feedparser.parse")
    def test_malformed_rss_feed(self, mock_parse):
        mock_parse.return_value = MagicMock(bozo=True, bozo_exception="Malformed feed")
        with self.assertRaises(RuntimeError) as context:
            parse_rss_feed("http://malformed-rss-feed.com/rss", "Job")
        self.assertIn("Malformed RSS feed", str(context.exception))

    # Test that the function returns an empty list when no entries are found
    @patch("feedparser.parse")
    def test_invalid_url(self, mock_parse):
        mock_parse.return_value = {"entries": []}
        result = parse_rss_feed("http://invalid-url.com/rss", "Job")
        self.assertEqual(result, [])

    # Test with a valid URL (Should have more than 0 entries returned)
    @patch("feedparser.parse")
    def test_valid_url(self, mock_parse):
        mock_parse.return_value = sample_internship_return
        result = parse_rss_feed("http://valid-url.com/rss", "Job")
        self.assertGreater(len(result), 0)
    
    # Test network errors
    @patch("feedparser.parse")
    def test_connection_error(self, mock_parse):
        mock_parse.side_effect = ConnectionError("Connection refused")
        with self.assertRaises(RuntimeError) as context:
            parse_rss_feed("http://unreachable.com/rss", "Job")
        self.assertIn("Network error", str(context.exception))
    
    @patch("feedparser.parse")
    def test_timeout_error(self, mock_parse):
        mock_parse.side_effect = TimeoutError("Request timed out")
        with self.assertRaises(RuntimeError) as context:
            parse_rss_feed("http://slow.com/rss", "Job")
        self.assertIn("Network error", str(context.exception))

    # Test with multiple entries
    @patch("feedparser.parse")
    def test_multiple_entries(self, mock_parse):
        mock_parse.return_value = {
            "entries": [
                {
                    "title": "Job 1",
                    "description": "Description 1",
                    "published": "Mon, 01 Jan 2025 10:00:00 +0000",
                    "link": "http://example.com/job1",
                },
                {
                    "title": "Job 2",
                    "description": "Description 2",
                    "published": "Tue, 02 Jan 2025 10:00:00 +0000",
                    "link": "http://example.com/job2",
                },
                {
                    "title": "Job 3",
                    "description": "Description 3",
                    "published": "Wed, 03 Jan 2025 10:00:00 +0000",
                    "link": "http://example.com/job3",
                }
            ]
        }
        result = parse_rss_feed("http://test.com/rss", "Job")
        self.assertEqual(len(result), 3)
    
    # Test with missing fields in entries
    @patch("feedparser.parse")
    def test_missing_entry_fields(self, mock_parse):
        mock_parse.return_value = {
            "entries": [
                {
                    "title": "Incomplete Job",
                    # Missing description, published, and link
                }
            ]
        }
        result = parse_rss_feed("http://test.com/rss", "Job")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["Company"], "Unknown")
        self.assertEqual(result[0]["whenDate"], "Unknown")
        self.assertEqual(result[0]["Location"], ["Unknown"])
    
    # Test item type is correctly set
    @patch("feedparser.parse")
    def test_item_type_setting(self, mock_parse):
        mock_parse.return_value = {
            "entries": [
                {
                    "title": "Test Title",
                    "description": "Test Description",
                    "published": "Mon, 01 Jan 2025 10:00:00 +0000",
                    "link": "http://example.com/item",
                }
            ]
        }
        
        # Test with Job type
        result = parse_rss_feed("http://test.com/rss", "Job")
        self.assertEqual(result[0]["Type"], "Job")
        
        # Test with Internship type
        result = parse_rss_feed("http://test.com/rss", "Internship")
        self.assertEqual(result[0]["Type"], "Internship")


class TestGetInternships(unittest.TestCase):
    """Test suite for the getInternships function"""
    
    # Test successful extraction
    @patch("feedparser.parse")
    def test_successful_title_extraction(self, mock_parse):
        mock_parse.return_value = sample_internship_return
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
    
    # Test with various title formats
    @patch("feedparser.parse")
    def test_title_with_special_characters(self, mock_parse):
        mock_parse.return_value = {
            "entries": [
                {
                    "title": "Software Engineer - Internship @ Tech Co. "
                    "(Remote/Hybrid)",
                    "description": "Employer: Tech Co.\n\nExpires: 12/31/2025\n\n"
                    "Great opportunity",
                    "published": "Mon, 01 Jan 2025 10:00:00 +0000",
                    "link": "http://example.com/internship1",
                }
            ]
        }
        result = getInternships("http://test.com/rss")
        self.assertIsNotNone(result)
        self.assertEqual(result[0]["Type"], "Internship")
    
    # Test empty feed
    @patch("feedparser.parse")
    def test_empty_feed(self, mock_parse):
        mock_parse.return_value = {"entries": []}
        result = getInternships("http://empty.com/rss")
        self.assertEqual(result, [])


class TestGetJobs(unittest.TestCase):
    """Test suite for the getJobs function"""
    
    # Test successful extraction
    @patch("feedparser.parse")
    def test_successful_title_extraction(self, mock_parse):
        mock_parse.return_value = sample_job_return
        result = getJobs("http://valid-url.com/rss")
        self.assertEqual(result[0]["Type"], "Job")
        self.assertEqual(result[0]["subType"], "")
        self.assertEqual(result[0]["Title"], "Sample Job")
        self.assertEqual(result[0]["Company"], "This Awesome Place")
        self.assertEqual(result[0]["Description"], "")
        self.assertEqual(result[0]["whenDate"], "08/01/2025")
        self.assertEqual(result[0]["pubDate"], "Wed, 29 Jan 2025 20:13:44 +0000")
        self.assertIn("Boston, MA", result[0]["Location"])
        self.assertIn("Remote", result[0]["Location"])
        self.assertEqual(result[0]["link"], "http://example.com/event1")
    
    # Test with remote-only jobs
    @patch("feedparser.parse")
    def test_remote_only_job(self, mock_parse):
        mock_parse.return_value = {
            "entries": [
                {
                    "title": "Senior Developer at Remote First",
                    "description": "Employer: Remote First\n\n"
                    "Expires: 10/01/2025\n\n"
                    "Location: Remote",
                    "published": "Mon, 01 Jan 2025 10:00:00 +0000",
                    "link": "http://example.com/job1",
                }
            ]
        }
        result = getJobs("http://test.com/rss")
        self.assertEqual(result[0]["Type"], "Job")
        self.assertIn("Remote", result[0]["Location"])


class TestExtractLocations(unittest.TestCase):
    """Test suite for the extract_locations helper function"""
    
    def test_extract_remote_location(self):
        """Test extraction of remote work locations"""
        description = "Great opportunity for remote work"
        result = extract_locations(description)
        self.assertIn("Remote", result)
        
        description = "Work from home - telecommute position"
        result = extract_locations(description)
        self.assertIn("Remote", result)
    
    def test_extract_hybrid_location(self):
        """Test extraction of hybrid work locations"""
        description = "Hybrid work arrangement available"
        result = extract_locations(description)
        self.assertIn("Hybrid", result)
    
    def test_extract_city_state_locations(self):
        """Test extraction of city, state locations"""
        description = "Location: San Francisco, CA"
        result = extract_locations(description)
        self.assertIn("San Francisco, CA", result)
        
        description = "Location: New York, NY, Boston, MA, Austin, TX"
        result = extract_locations(description)
        self.assertIn("New York, NY", result)
        self.assertIn("Boston, MA", result)
        self.assertIn("Austin, TX", result)
    
    def test_extract_no_location(self):
        """Test when no location is specified"""
        description = "Great job opportunity with competitive salary"
        result = extract_locations(description)
        self.assertEqual(result, ["Unknown"])
    
    def test_extract_empty_description(self):
        """Test with empty or None description"""
        result = extract_locations("")
        self.assertEqual(result, ["Unknown"])
        
        result = extract_locations(None)
        self.assertEqual(result, ["Unknown"])
    
    def test_valid_state_codes(self):
        """Test extraction with valid US state codes"""
        description = "Location: Portland, OR"
        result = extract_locations(description)
        self.assertIn("Portland, OR", result)
        
        description = "Location: Miami, FL, Seattle, WA, Denver, CO"
        result = extract_locations(description)
        self.assertIn("Miami, FL", result)
        self.assertIn("Seattle, WA", result)
        self.assertIn("Denver, CO", result)
    
    def test_invalid_state_codes(self):
        """Test that invalid state codes are filtered out"""
        description = "Location: SomeCity, XX"  # XX is not a valid state
        result = extract_locations(description)
        self.assertNotIn("SomeCity, XX", result)
        
        description = "Location: Paris, FR"  # FR is not a US state
        result = extract_locations(description)
        self.assertNotIn("Paris, FR", result)
    
    def test_word_count_filter(self):
        """Test that locations with too many words are filtered"""
        # This should be filtered due to word count > 4
        description = "Location: Main Office Downtown Boston Building, MA"
        result = extract_locations(description)
        self.assertNotIn("Main Office Downtown Boston Building, MA", result)
        
        # This should pass (word count <= 4)
        description = "Location: San Francisco Bay Area, CA"
        result = extract_locations(description)
        self.assertIn("San Francisco Bay Area, CA", result)
    
    def test_location_with_special_characters(self):
        """Test locations with apostrophes, hyphens, and dots"""
        description = "Location: O'Fallon, IL"
        result = extract_locations(description)
        self.assertIn("O'Fallon, IL", result)
        
        description = "Location: St. Louis, MO"
        result = extract_locations(description)
        self.assertIn("St. Louis, MO", result)
        
        description = "Location: Winston-Salem, NC"
        result = extract_locations(description)
        self.assertIn("Winston-Salem, NC", result)
    
    def test_case_insensitive_keywords(self):
        """Test case insensitive matching for remote/hybrid"""
        description = "REMOTE position available"
        result = extract_locations(description)
        self.assertIn("Remote", result)
        
        description = "HyBrId work environment"
        result = extract_locations(description)
        self.assertIn("Hybrid", result)
    
    def test_extract_mixed_location_types(self):
        """Test extraction with both remote and physical locations"""
        description = "Location: Chicago, IL, Remote, Hybrid options available"
        result = extract_locations(description)
        self.assertIn("Chicago, IL", result)
        self.assertIn("Remote", result)
        self.assertIn("Hybrid", result)


class TestTitleProcessing(unittest.TestCase):
    """Test suite for title processing logic"""
    
    @patch("feedparser.parse")
    def test_title_company_removal(self, mock_parse):
        """Test that company name is removed from title"""
        mock_parse.return_value = {
            "entries": [
                {
                    "title": "Software Engineer at Google",
                    "description": "Employer: Google\n\nExpires: 12/31/2025",
                    "published": "Mon, 01 Jan 2025 10:00:00 +0000",
                    "link": "http://example.com/job",
                }
            ]
        }
        result = getJobs("http://test.com/rss")
        self.assertEqual(result[0]["Title"], "Software Engineer")
        self.assertEqual(result[0]["Company"], "Google")
    
    @patch("feedparser.parse")
    def test_title_case_insensitive_at(self, mock_parse):
        """Test case insensitive 'at' removal in title"""
        mock_parse.return_value = {
            "entries": [
                {
                    "title": "Data Analyst AT Microsoft",
                    "description": "Employer: Microsoft\n\nExpires: 12/31/2025",
                    "published": "Mon, 01 Jan 2025 10:00:00 +0000",
                    "link": "http://example.com/job",
                }
            ]
        }
        result = getJobs("http://test.com/rss")
        self.assertEqual(result[0]["Title"], "Data Analyst")
    
    @patch("feedparser.parse")
    def test_title_whitespace_handling(self, mock_parse):
        """Test whitespace handling in titles"""
        mock_parse.return_value = {
            "entries": [
                {
                    "title": "  Product Manager   at   Apple  ",
                    "description": "Employer: Apple\n\nExpires: 12/31/2025",
                    "published": "Mon, 01 Jan 2025 10:00:00 +0000",
                    "link": "http://example.com/job",
                }
            ]
        }
        result = getJobs("http://test.com/rss")
        self.assertEqual(result[0]["Title"], "Product Manager")


class TestDateExtraction(unittest.TestCase):
    """Test suite for date extraction from descriptions"""
    
    @patch("feedparser.parse")
    def test_standard_date_format(self, mock_parse):
        """Test extraction of standard MM/DD/YYYY format"""
        mock_parse.return_value = {
            "entries": [
                {
                    "title": "Job Title",
                    "description": "Employer: Company\n\nExpires: 12/31/2025\n\n"
                    "Description",
                    "published": "Mon, 01 Jan 2025 10:00:00 +0000",
                    "link": "http://example.com/job",
                }
            ]
        }
        result = getJobs("http://test.com/rss")
        self.assertEqual(result[0]["whenDate"], "12/31/2025")
    
    @patch("feedparser.parse")
    def test_missing_expiry_date(self, mock_parse):
        """Test when expiry date is missing"""
        mock_parse.return_value = {
            "entries": [
                {
                    "title": "Job Title",
                    "description": "Employer: Company\n\nNo expiry mentioned",
                    "published": "Mon, 01 Jan 2025 10:00:00 +0000",
                    "link": "http://example.com/job",
                }
            ]
        }
        result = getJobs("http://test.com/rss")
        self.assertEqual(result[0]["whenDate"], "Unknown")
    
    @patch("feedparser.parse")
    def test_expires_with_extra_spaces(self, mock_parse):
        """Test date extraction with extra spaces around Expires"""
        mock_parse.return_value = {
            "entries": [
                {
                    "title": "Job Title",
                    "description": "Employer: Company\n\nExpires :  01/15/2026  \n\n",
                    "published": "Mon, 01 Jan 2025 10:00:00 +0000",
                    "link": "http://example.com/job",
                }
            ]
        }
        result = getJobs("http://test.com/rss")
        self.assertEqual(result[0]["whenDate"], "01/15/2026")


class TestCompanyExtraction(unittest.TestCase):
    """Test suite for company name extraction"""
    
    @patch("feedparser.parse")
    def test_standard_employer_format(self, mock_parse):
        """Test extraction of standard employer format"""
        mock_parse.return_value = {
            "entries": [
                {
                    "title": "Job Title",
                    "description": "Employer: Tech Company Inc.\n\nExpires: 12/31/2025",
                    "published": "Mon, 01 Jan 2025 10:00:00 +0000",
                    "link": "http://example.com/job",
                }
            ]
        }
        result = getJobs("http://test.com/rss")
        self.assertEqual(result[0]["Company"], "Tech Company Inc.")
    
    @patch("feedparser.parse")
    def test_employer_with_special_chars(self, mock_parse):
        """Test employer extraction with special characters"""
        mock_parse.return_value = {
            "entries": [
                {
                    "title": "Job Title",
                    "description": "Employer: AT&T Communications (NYSE: T)\n\n"
                    "Expires: 12/31/2025",
                    "published": "Mon, 01 Jan 2025 10:00:00 +0000",
                    "link": "http://example.com/job",
                }
            ]
        }
        result = getJobs("http://test.com/rss")
        self.assertEqual(result[0]["Company"], "AT&T Communications (NYSE: T)")
    
    @patch("feedparser.parse")
    def test_missing_employer(self, mock_parse):
        """Test when employer is missing"""
        mock_parse.return_value = {
            "entries": [
                {
                    "title": "Job Title",
                    "description": "No employer information\n\nExpires: 12/31/2025",
                    "published": "Mon, 01 Jan 2025 10:00:00 +0000",
                    "link": "http://example.com/job",
                }
            ]
        }
        result = getJobs("http://test.com/rss")
        self.assertEqual(result[0]["Company"], "Unknown")
    
    @patch("feedparser.parse")
    def test_employer_followed_by_expires(self, mock_parse):
        """Test employer extraction when immediately followed by Expires"""
        mock_parse.return_value = {
            "entries": [
                {
                    "title": "Job Title",
                    "description": "Employer: Quick CompanyExpires: 12/31/2025",
                    "published": "Mon, 01 Jan 2025 10:00:00 +0000",
                    "link": "http://example.com/job",
                }
            ]
        }
        result = getJobs("http://test.com/rss")
        self.assertEqual(result[0]["Company"], "Quick Company")


class TestFieldDefaults(unittest.TestCase):
    """Test suite for default field values"""
    
    @patch("feedparser.parse")
    def test_all_fields_present(self, mock_parse):
        """Test that all expected fields are present in output"""
        mock_parse.return_value = {
            "entries": [
                {
                    "title": "Job Title",
                    "description": "Minimal description",
                    "published": "Mon, 01 Jan 2025 10:00:00 +0000",
                    "link": "http://example.com/job",
                }
            ]
        }
        result = getJobs("http://test.com/rss")
        
        expected_fields = [
            "Type", "subType", "Company", "Title", "Description",
            "whenDate", "pubDate", "Location", "link", "entryDate"
        ]
        
        for field in expected_fields:
            self.assertIn(field, result[0], f"Field {field} is missing")
    
    @patch("feedparser.parse")
    def test_empty_description_field(self, mock_parse):
        """Test that Description field is always empty string"""
        mock_parse.return_value = {
            "entries": [
                {
                    "title": "Job Title",
                    "description": "Employer: Company\n\n"
                    "Long detailed description here",
                    "published": "Mon, 01 Jan 2025 10:00:00 +0000",
                    "link": "http://example.com/job",
                }
            ]
        }
        result = getJobs("http://test.com/rss")
        self.assertEqual(result[0]["Description"], "")
    
    @patch("feedparser.parse")
    def test_empty_subtype_field(self, mock_parse):
        """Test that subType field is always empty string"""
        mock_parse.return_value = {
            "entries": [
                {
                    "title": "Job Title",
                    "description": "Employer: Company",
                    "published": "Mon, 01 Jan 2025 10:00:00 +0000",
                    "link": "http://example.com/job",
                }
            ]
        }
        result = getJobs("http://test.com/rss")
        self.assertEqual(result[0]["subType"], "")


class TestBozoFeedHandling(unittest.TestCase):
    """Test suite for malformed (bozo) feed handling"""
    
    @patch("feedparser.parse")
    def test_bozo_feed_with_exception(self, mock_parse):
        """Test handling of bozo feeds with exceptions"""
        mock_feed = MagicMock()
        mock_feed.bozo = True
        mock_feed.bozo_exception = "XML parsing error"
        mock_parse.return_value = mock_feed
        
        with self.assertRaises(RuntimeError) as context:
            parse_rss_feed("http://malformed.com/rss", "Job")
        self.assertIn("Malformed RSS feed", str(context.exception))
        self.assertIn("XML parsing error", str(context.exception))
    
    @patch("feedparser.parse")
    def test_bozo_feed_without_exception(self, mock_parse):
        """Test handling of bozo feeds without exception details"""
        mock_feed = MagicMock()
        mock_feed.bozo = True
        mock_feed.bozo_exception = None
        mock_parse.return_value = mock_feed
        
        with self.assertRaises(RuntimeError) as context:
            parse_rss_feed("http://malformed.com/rss", "Job")
        self.assertIn("Malformed RSS feed", str(context.exception))


class TestIntegrationScenarios(unittest.TestCase):
    """Integration-like tests for real-world scenarios"""
    
    @patch("feedparser.parse")
    def test_realistic_job_feed(self, mock_parse):
        """Test with realistic job feed data"""
        mock_parse.return_value = {
            "entries": [
                {
                    "title": "Senior Python Developer at TechCorp International",
                    "description": """Employer: TechCorp International
                    
Expires: 03/15/2025

We are seeking a Senior Python Developer to join our growing team.

Requirements:
- 5+ years of Python experience
- Knowledge of Django/Flask
- Experience with AWS

Location: San Francisco, CA, Austin, TX, Remote

Benefits:
- Competitive salary
- Health insurance
- 401k matching""",
                    "published": "Wed, 29 Jan 2025 14:30:00 +0000",
                    "link": "https://careers.techcorp.com/jobs/12345",
                },
                {
                    "title": "Data Scientist - Entry Level",
                    "description": """Employer: DataCo Analytics

Expires: 04/01/2025

Join our data science team as an entry-level data scientist.

Location: New York, NY, Hybrid

Contact: hr@dataco.com""",
                    "published": "Thu, 30 Jan 2025 09:00:00 +0000",
                    "link": "https://dataco.com/careers/ds-001",
                }
            ]
        }
        
        result = getJobs("http://test.com/rss")
        
        # Verify first job
        self.assertEqual(result[0]["Title"], "Senior Python Developer")
        self.assertEqual(result[0]["Company"], "TechCorp International")
        self.assertEqual(result[0]["whenDate"], "03/15/2025")
        self.assertIn("San Francisco, CA", result[0]["Location"])
        self.assertIn("Austin, TX", result[0]["Location"])
        self.assertIn("Remote", result[0]["Location"])
        
        # Verify second job
        self.assertEqual(result[1]["Title"], "Data Scientist - Entry Level")
        self.assertEqual(result[1]["Company"], "DataCo Analytics")
        self.assertEqual(result[1]["whenDate"], "04/01/2025")
        self.assertIn("New York, NY", result[1]["Location"])
        self.assertIn("Hybrid", result[1]["Location"])


class TestPerformanceAndStress(unittest.TestCase):
    """Test suite for performance and stress testing"""
    
    @patch("feedparser.parse")
    def test_large_batch_of_jobs(self, mock_parse):
        """Test batch processing of many jobs"""
        entries = []
        for i in range(100):
            entries.append({
                "title": f"Job {i}",
                "description": f"Employer: Company {i}\n\nExpires: 12/31/2025",
                "published": "Mon, 01 Jan 2025 10:00:00 +0000",
                "link": f"http://example.com/job{i}",
            })
        mock_parse.return_value = {"entries": entries}
        result = getJobs("http://test.com/rss")
        self.assertEqual(len(result), 100)
    
    @patch("feedparser.parse")
    def test_memory_efficiency(self, mock_parse):
        """Test memory efficiency with large feeds"""
        # Create a large feed with 1000 entries
        large_feed = {"entries": []}
        for i in range(1000):
            large_feed["entries"].append({
                "title": f"Job {i}",
                "description": f"Employer: Company {i}\n\nExpires: 12/31/2025\n\n"
                + "X" * 1000,
                "published": "Mon, 01 Jan 2025 10:00:00 +0000",
                "link": f"http://example.com/job{i}",
            })
        mock_parse.return_value = large_feed
        # Should handle large feeds without memory issues
        result = getJobs("http://test.com/rss")
        self.assertEqual(len(result), 1000)


if __name__ == "__main__":
    unittest.main()