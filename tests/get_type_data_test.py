import tempfile
import unittest
from unittest.mock import patch

from data_processing.get_type_data import get_type_data


class TestGetTypeData(unittest.TestCase):
    def setUp(self):
        """
        Create a temporary CSV file for testing
        """
        with tempfile.NamedTemporaryFile(
            delete=False, mode="w", suffix=".csv", encoding="utf8"
        ) as temp_file:
            temp_file.write(
                "Type,subType,Title,Description,Company,Location,whenDate,pubDate,link,entryDate\n"
            ) # noqa: E501
            temp_file.write(
                "Internship,,Pizza Intern,Help wanted,Cheesy Dreams Inc,Italy,Summer 2025,2025-07-01,http://cheesydreams.com/apply,2025-07-07\n"
            )  # noqa: E501
            self.temp_file_path = temp_file.name

    @patch("data_collections.csv_updater.extract_entries_from_csv")
    def test_get_type_data_error_handling(self, mock_extract):
        """
        Test for error handling given not found csv file
        """
        mock_extract.side_effect = RuntimeError("No such file or directory")
        with self.assertRaises(RuntimeError):
            get_type_data("missing.csv", "Internship")

    @patch("data_collections.csv_updater.extract_entries_from_csv")
    def test_get_type_data_filter_find_match(self, mock_extract):
        """
        Test for successful filtering of Intership type data
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
        results = get_type_data(self.temp_file_path, "Internship")
        self.assertEqual(len(results), 1)
