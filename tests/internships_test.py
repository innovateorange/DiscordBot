from data_collections.internships import getInternships
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

    @patch("requests.get")
    def test_various_markdown_formats(self, mock_get):
        """Test extraction with different markdown formats through public interface"""
        test_cases = [
            {
                "content": """
# Google
Company: Google
Role: Software Engineer
Location: Mountain View, CA
Posted: 2024-01-15
Apply: https://careers.google.com/intern
                """,
                "expected_title": "Google",
                "expected_description": "Software Engineer",
                "expected_date": "2024-01-15"
            },
            {
                "content": """
# Microsoft
Company: Microsoft
Role: Data Scientist
Location: Seattle, WA
Posted: 2024-01-20
[Apply Here](https://careers.microsoft.com/intern)
                """,
                "expected_title": "Microsoft",
                "expected_description": "Data Scientist",
                "expected_date": "2024-01-20"
            },
            {
                "content": """
# Amazon
Company: Amazon
Role: Software Development Engineer Intern
Location: Seattle, WA
Posted: 2024-02-01
Apply: https://amazon.com/careers/intern
                """,
                "expected_title": "Amazon",
                "expected_description": "Software Development Engineer Intern",
                "expected_date": "2024-02-01"
            }
        ]
        
        for i, test_case in enumerate(test_cases):
            with self.subTest(case=i):
                mock_response = MagicMock()
                mock_response.text = test_case["content"]
                mock_response.raise_for_status.return_value = None
                mock_get.return_value = mock_response
                
                result = getInternships("https://example.com/internships.md")
                
                self.assertGreater(len(result), 0)
                internship = result[0]
                self.assertEqual(internship["Title"], test_case["expected_title"])
                self.assertEqual(internship["Description"], test_case["expected_description"])
                self.assertEqual(internship["pubDate"], test_case["expected_date"])
                self.assertEqual(internship["Type"], "Internship")
                self.assertEqual(internship["whenDate"], "")

    @patch("requests.get")
    def test_section_parsing_with_headers(self, mock_get):
        """Test parsing sections separated by markdown headers through public interface"""
        content = """
# Company A
Company: Company A
Role: Software Engineer
Location: San Francisco, CA
Posted: 2024-01-15
Apply: https://companya.com/apply

## Company B
Company: Company B
Role: Data Scientist
Location: New York, NY
Posted: 2024-01-20
Apply: https://companyb.com/apply

### Company C
Company: Company C
Role: Product Manager
Location: Austin, TX
Posted: 2024-01-25
Apply: https://companyc.com/apply
        """
        
        mock_response = MagicMock()
        mock_response.text = content
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = getInternships("https://example.com/internships.md")
        
        self.assertEqual(len(result), 3)
        companies = [internship["Title"] for internship in result]
        self.assertIn("Company A", companies)
        self.assertIn("Company B", companies)
        self.assertIn("Company C", companies)

    @patch("requests.get")
    def test_section_parsing_with_horizontal_rules(self, mock_get):
        """Test parsing sections separated by horizontal rules through public interface"""
        content = """
Company: Company A
Role: Software Engineer
Location: San Francisco, CA
Posted: 2024-01-15
Apply: https://companya.com/apply

---

Company: Company B
Role: Data Scientist
Location: New York, NY
Posted: 2024-01-20
Apply: https://companyb.com/apply

***

Company: Company C
Role: Product Manager
Location: Austin, TX
Posted: 2024-01-25
Apply: https://companyc.com/apply
        """
        
        mock_response = MagicMock()
        mock_response.text = content
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = getInternships("https://example.com/internships.md")
        
        self.assertEqual(len(result), 3)
        companies = [internship["Title"] for internship in result]
        self.assertIn("Company A", companies)
        self.assertIn("Company B", companies)
        self.assertIn("Company C", companies)

    @patch("requests.get")
    def test_filtering_short_sections(self, mock_get):
        """Test that very short sections are filtered out through public interface"""
        content = """
# Short Section
Company: Short
Role: Intern

# Long Section
Company: Long Company
Role: Software Engineer
Location: San Francisco, CA
Posted: 2024-01-15
Apply: https://longcompany.com/apply
This is a much longer section that should be included in the results because it has enough content to be meaningful and contains important internship information.
        """
        
        mock_response = MagicMock()
        mock_response.text = content
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = getInternships("https://example.com/internships.md")
        
        # Should only include the longer section
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["Title"], "Long Company")

    @patch("requests.get")
    def test_markdown_link_extraction(self, mock_get):
        """Test extraction of markdown format links through public interface"""
        content = """
# Test Company
Company: Test Company
Role: Software Engineer
Location: Remote
Posted: 2024-01-15
[Apply Here](https://testcompany.com/apply)
        """
        
        mock_response = MagicMock()
        mock_response.text = content
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = getInternships("https://example.com/internships.md")
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["link"], "https://testcompany.com/apply")

    @patch("requests.get")
    def test_complete_internship_extraction(self, mock_get):
        """Test extraction of all fields for a complete internship through public interface"""
        content = """
# Amazon
Company: Amazon
Role: Software Development Engineer Intern
Posted: 2024-02-01
Location: Seattle, WA
Apply: https://amazon.com/careers/intern
        """
        
        mock_response = MagicMock()
        mock_response.text = content
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = getInternships("https://example.com/internships.md")
        
        self.assertEqual(len(result), 1)
        internship = result[0]
        self.assertEqual(internship["Type"], "Internship")
        self.assertEqual(internship["Title"], "Amazon")
        self.assertEqual(internship["Description"], "Software Development Engineer Intern")
        self.assertEqual(internship["whenDate"], "")
        self.assertEqual(internship["pubDate"], "2024-02-01")
        self.assertEqual(internship["Location"], "Seattle, WA")
        self.assertEqual(internship["link"], "https://amazon.com/careers/intern")


if __name__ == "__main__":
    unittest.main()
