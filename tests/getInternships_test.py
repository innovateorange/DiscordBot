from data_collections.internships import getInternships, _parse_internship_sections, _extract_internship_data
from unittest.mock import MagicMock, patch
import unittest


class TestGetInternships(unittest.TestCase):
    """Test suite for the getInternships function"""

    @patch("requests.get")
    def test_successful_fetch_and_parse(self, mock_get):
        """Test successful fetching and parsing of internship data"""
        mock_response = MagicMock()
        mock_response.text = """
# Google
**Software Engineering Intern**
Location: Mountain View, CA
Posted: 2024-01-15
Apply: https://careers.google.com/intern

# Microsoft
**Data Science Intern**
Location: Seattle, WA
Posted: 2024-01-20
Apply: https://careers.microsoft.com/intern
        """
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = getInternships("https://example.com/internships.md")
        
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        
        # Check first internship
        first_internship = result[0]
        self.assertEqual(first_internship["Type"], "Internship")
        self.assertIn("Google", first_internship["Title"])
        self.assertIn("Software Engineering", first_internship["Description"])
        self.assertEqual(first_internship["whenDate"], "")  # Should be blank
        self.assertIn("2024-01-15", first_internship["pubDate"])
        self.assertIn("Mountain View", first_internship["Location"])
        self.assertIn("google.com", first_internship["link"])
        self.assertIn("entryDate", first_internship)

    @patch("requests.get")
    def test_network_error(self, mock_get):
        """Test handling of network errors"""
        mock_get.side_effect = Exception("Network error")
        
        with self.assertRaises(RuntimeError) as context:
            getInternships("https://example.com/internships.md")
        
        self.assertIn("Failed to fetch the markdown file", str(context.exception))

    @patch("requests.get")
    def test_empty_content(self, mock_get):
        """Test handling of empty markdown content"""
        mock_response = MagicMock()
        mock_response.text = ""
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        with self.assertRaises(RuntimeError) as context:
            getInternships("https://example.com/internships.md")
        
        self.assertIn("Empty markdown file", str(context.exception))

    @patch("requests.get")
    def test_no_valid_internships(self, mock_get):
        """Test when no valid internship data is found"""
        mock_response = MagicMock()
        mock_response.text = "This is just some random text without internship data."
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = getInternships("https://example.com/internships.md")
        self.assertEqual(result, [])

    @patch("requests.get")
    def test_http_error(self, mock_get):
        """Test handling of HTTP errors"""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("404 Not Found")
        mock_get.return_value = mock_response
        
        with self.assertRaises(RuntimeError) as context:
            getInternships("https://example.com/internships.md")
        
        self.assertIn("Failed to fetch the markdown file", str(context.exception))


class TestParseInternshipSections(unittest.TestCase):
    """Test suite for the _parse_internship_sections function"""

    def test_section_parsing_with_headers(self):
        """Test parsing sections separated by markdown headers"""
        content = """
# Company A
This is a much longer section that should be included in the results because it has enough content to be meaningful and contains important internship information.

## Company B
This is another longer section with substantial content that meets the minimum length requirement for parsing and extraction.

### Company C
This section also has enough content to be considered valid for internship data extraction and processing.
        """
        
        sections = _parse_internship_sections(content)
        self.assertGreater(len(sections), 0)
        self.assertTrue(all(len(section) > 50 for section in sections))

    def test_section_parsing_with_horizontal_rules(self):
        """Test parsing sections separated by horizontal rules"""
        content = """
Company A content here with substantial information about internship opportunities and detailed role descriptions that meet the minimum length requirement.
---
Company B content here with comprehensive details about their internship program including location, requirements, and application process information.
***
Company C content here with extensive information about their summer internship opportunities and detailed program descriptions.
        """
        
        sections = _parse_internship_sections(content)
        self.assertGreater(len(sections), 0)

    def test_filtering_short_sections(self):
        """Test that very short sections are filtered out"""
        content = """
# Short
Hi

# Long enough
This is a much longer section that should be included in the results because it has enough content to be meaningful.
        """
        
        sections = _parse_internship_sections(content)
        # Should only include the longer section
        self.assertEqual(len(sections), 1)


class TestExtractInternshipData(unittest.TestCase):
    """Test suite for the _extract_internship_data function"""

    def test_company_extraction(self):
        """Test extraction of company names"""
        section = "Company: Google\nRole: Software Engineer"
        result = _extract_internship_data(section)
        
        self.assertIsNotNone(result)
        self.assertEqual(result["Title"], "Google")
        self.assertEqual(result["Type"], "Internship")

    def test_role_extraction(self):
        """Test extraction of role/position"""
        section = "Company: Microsoft\nRole: Data Scientist"
        result = _extract_internship_data(section)
        
        self.assertIsNotNone(result)
        self.assertEqual(result["Description"], "Data Scientist")

    def test_date_extraction(self):
        """Test extraction of posted date"""
        section = "Posted: 2024-01-15\nCompany: Apple"
        result = _extract_internship_data(section)
        
        self.assertIsNotNone(result)
        self.assertEqual(result["pubDate"], "2024-01-15")

    def test_location_extraction(self):
        """Test extraction of location"""
        section = "Location: San Francisco, CA\nCompany: Twitter"
        result = _extract_internship_data(section)
        
        self.assertIsNotNone(result)
        self.assertEqual(result["Location"], "San Francisco, CA")

    def test_link_extraction(self):
        """Test extraction of application links"""
        section = "Apply: https://example.com/apply\nCompany: Test"
        result = _extract_internship_data(section)
        
        self.assertIsNotNone(result)
        self.assertEqual(result["link"], "https://example.com/apply")

    def test_markdown_link_extraction(self):
        """Test extraction of markdown format links"""
        section = "[Apply Here](https://example.com/apply)\nCompany: Test"
        result = _extract_internship_data(section)
        
        self.assertIsNotNone(result)
        self.assertEqual(result["link"], "https://example.com/apply")

    def test_no_valid_data(self):
        """Test when no valid internship data is found"""
        section = "This is just some random text without any internship information."
        result = _extract_internship_data(section)
        
        self.assertIsNone(result)

    def test_when_date_blank(self):
        """Test that whenDate is always blank as per requirements"""
        section = "Company: Test\nRole: Intern"
        result = _extract_internship_data(section)
        
        self.assertIsNotNone(result)
        self.assertEqual(result["whenDate"], "")

    def test_complete_internship_extraction(self):
        """Test extraction of all fields for a complete internship"""
        section = """
Company: Amazon
Role: Software Development Engineer Intern
Posted: 2024-02-01
Location: Seattle, WA
Apply: https://amazon.com/careers/intern
        """
        
        result = _extract_internship_data(section)
        
        self.assertIsNotNone(result)
        self.assertEqual(result["Type"], "Internship")
        self.assertEqual(result["Title"], "Amazon")
        self.assertEqual(result["Description"], "Software Development Engineer Intern")
        self.assertEqual(result["whenDate"], "")
        self.assertEqual(result["pubDate"], "2024-02-01")
        self.assertEqual(result["Location"], "Seattle, WA")
        self.assertEqual(result["link"], "https://amazon.com/careers/intern")


if __name__ == "__main__":
    unittest.main() 