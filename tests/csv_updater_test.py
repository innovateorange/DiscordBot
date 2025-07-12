import os
import tempfile
import unittest
from unittest.mock import mock_open, patch

import pandas as pd

from data_collections.csv_updater import (
    extract_entries_from_csv,
    items_to_csv,
    remove_duplicates,
)

FAKE_CSV = """Type,Title,Description,whenDate,pubDate,Location,link,entryDate
Event,dummy_Title,dummy_Description,dummy_whenDate,dummy_pubDate,dummy_Location,dummy_Link,dummy_entryDate
Event,test_Title,test_Description,test_whenDate,test_pubDate,test_Location,test_Link,test_entryDate
"""


class TestExtractFromCSV(unittest.TestCase):
    """Testing suite for the extract_entries_from_csv() method"""

    def test_missing_path(self):
        path = ""
        with self.assertRaises(RuntimeError) as context:
            extract_entries_from_csv(path)
        self.assertIn("Failed to read CSV file:", str(context.exception))

    def test_no_data_in_csv(self):
        path = "test.csv"
        empty_csv = """"""
        with patch("builtins.open", mock_open(read_data=empty_csv)):
            result = extract_entries_from_csv(path)
        self.assertEqual(result, [])

    def test_data_in_csv(self):
        path = "test.csv"
        with patch("builtins.open", mock_open(read_data=FAKE_CSV)):
            result = extract_entries_from_csv(path)
        expected = [
            {
                "Type": "Event",
                "Title": "dummy_Title",
                "Description": "dummy_Description",
                "whenDate": "dummy_whenDate",
                "pubDate": "dummy_pubDate",
                "Location": "dummy_Location",
                "link": "dummy_Link",
                "entryDate": "dummy_entryDate",
            },
            {
                "Type": "Event",
                "Title": "test_Title",
                "Description": "test_Description",
                "whenDate": "test_whenDate",
                "pubDate": "test_pubDate",
                "Location": "test_Location",
                "link": "test_Link",
                "entryDate": "test_entryDate",
            },
        ]
        self.assertEqual(expected, result)


class TestRemoveDuplicates(unittest.TestCase):
    """Testing suite for the remove_duplicates() method"""

    def test_missing_data(self):
        data = []
        result = remove_duplicates(data)
        self.assertEqual(result, [])

    def test_no_duplicates(self):
        data = [
            {
                "Type": "Event",
                "Title": "dummy_Title",
                "Description": "dummy_Description",
                "whenDate": "dummy_whenDate",
                "pubDate": "dummy_pubDate",
                "Location": "dummy_Location",
                "link": "dummy_Link",
                "entryDate": "dummy_entryDate",
            },
            {
                "Type": "Event",
                "Title": "test_Title",
                "Description": "test_Description",
                "whenDate": "test_whenDate",
                "pubDate": "test_pubDate",
                "Location": "test_Location",
                "link": "test_Link",
                "entryDate": "test_entryDate",
            },
        ]
        result = remove_duplicates(data)
        self.assertEqual(data, result)

    def test_contains_duplicates(self):
        data = [
            {
                "Type": "Event",
                "Title": "dummy_Title",
                "Description": "dummy_Description",
                "whenDate": "dummy_whenDate",
                "pubDate": "dummy_pubDate",
                "Location": "dummy_Location",
                "link": "dummy_Link",
                "entryDate": "dummy_entryDate",
            },
            {
                "Type": "Event",
                "Title": "dummy_Title",
                "Description": "dummy_Description",
                "whenDate": "dummy_whenDate",
                "pubDate": "dummy_pubDate",
                "Location": "dummy_Location",
                "link": "dummy_Link",
                "entryDate": "dummy_entryDate",
            },
        ]
        result = remove_duplicates(data)

        expected = [
            {
                "Type": "Event",
                "Title": "dummy_Title",
                "Description": "dummy_Description",
                "whenDate": "dummy_whenDate",
                "pubDate": "dummy_pubDate",
                "Location": "dummy_Location",
                "link": "dummy_Link",
                "entryDate": "dummy_entryDate",
            }
        ]
        self.assertEqual(result, expected)


class TestItemsToCSV(unittest.TestCase):
    """Testing suite for the items_to_csv() method."""

    def test_no_path_to_file(self):
        mock_data = [{"title": "Event 1", "date": "2024-01-01"}]
        non_existent_path = "non_existent_file.csv"
        with patch("os.path.isfile", return_value=False):

            with self.assertRaises(RuntimeError) as context:
                items_to_csv(mock_data, non_existent_path)

            self.assertIn("path_to_csv not found", str(context.exception))

    def test_no_data(self):
        mock_data = []
        dummy_path = "test.csv"

        with (
            patch("pandas.DataFrame.to_csv") as mocked_csv,
            patch("os.path.isfile", return_value=True),
        ):
            items_to_csv(mock_data, dummy_path)

        mocked_csv.assert_not_called()

    @patch("data_collections.csv_updater.remove_duplicates")
    @patch("data_collections.csv_updater.extract_entries_from_csv")
    @patch("data_collections.csv_updater.os.path.isfile")
    def test_successful_items_to_csv_with_prior_data(
        self, mock_isfile, mock_extract_entries, mock_remove_duplicates
    ):

        prior_csv_data = [
            {
                "Type": "Event",
                "Title": "test_Title",
                "Description": "test_Description",
                "whenDate": "test_whenDate",
                "pubDate": "test_pubDate",
                "Location": "test_Location",
                "link": "test_Link",
                "entryDate": "test_entryDate",
            }
        ]

        incoming_data = [
            {
                "Type": "Event",
                "Title": "dummy_Title",
                "Description": "dummy_Description",
                "whenDate": "dummy_whenDate",
                "pubDate": "dummy_pubDate",
                "Location": "dummy_Location",
                "link": "dummy_Link",
                "entryDate": "dummy_entryDate",
            }
        ]

        mock_isfile.return_value = True
        mock_extract_entries.return_value = prior_csv_data
        mock_remove_duplicates.side_effect = lambda x: x

        expected_data = prior_csv_data + incoming_data

        with tempfile.TemporaryDirectory() as temp_dir:
            dummy_path = os.path.join(temp_dir, "test.csv")
            expected_df = pd.DataFrame(expected_data)

            items_to_csv(incoming_data, dummy_path)

            result_df = pd.read_csv(dummy_path)
            pd.testing.assert_frame_equal(
                expected_df.sort_values(list(expected_df.columns)).reset_index(
                    drop=True
                ),
                result_df.sort_values(list(expected_df.columns)).reset_index(drop=True),
            )

    @patch("data_collections.csv_updater.remove_duplicates")
    @patch("data_collections.csv_updater.extract_entries_from_csv")
    @patch("data_collections.csv_updater.os.path.isfile")
    def test_successful_items_to_csv_with_no_prior_data(
        self, mock_isfile, mock_extract_entries, mock_remove_duplicates
    ):

        mock_isfile.return_value = True
        mock_extract_entries.return_value = []
        mock_remove_duplicates.side_effect = lambda x: x

        data = [
            {
                "Type": "Event",
                "Title": "dummy_Title",
                "Description": "dummy_Description",
                "whenDate": "dummy_whenDate",
                "pubDate": "dummy_pubDate",
                "Location": "dummy_Location",
                "link": "dummy_Link",
                "entryDate": "dummy_entryDate",
            },
            {
                "Type": "Event",
                "Title": "test_Title",
                "Description": "test_Description",
                "whenDate": "test_whenDate",
                "pubDate": "test_pubDate",
                "Location": "test_Location",
                "link": "test_Link",
                "entryDate": "test_entryDate",
            },
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            dummy_path = os.path.join(temp_dir, "test.csv")
            expected = pd.DataFrame(data)
            items_to_csv(data, dummy_path)

            result = pd.read_csv(dummy_path)
            pd.testing.assert_frame_equal(expected, result)

    @patch("data_collections.csv_updater.remove_duplicates")
    @patch("data_collections.csv_updater.extract_entries_from_csv")
    @patch("data_collections.csv_updater.os.path.isfile")
    def test_successful_items_to_csv_with_prior_data_duplicates(
        self, mock_isfile, mock_extract_entries, mock_remove_duplicates
    ):

        prior_csv_data = [
            {
                "Type": "Event",
                "Title": "test_Title",
                "Description": "test_Description",
                "whenDate": "test_whenDate",
                "pubDate": "test_pubDate",
                "Location": "test_Location",
                "link": "test_Link",
                "entryDate": "test_entryDate",
            }
        ]

        incoming_data = [
            {
                "Type": "Event",
                "Title": "test_Title",
                "Description": "test_Description",
                "whenDate": "test_whenDate",
                "pubDate": "test_pubDate",
                "Location": "test_Location",
                "link": "test_Link",
                "entryDate": "test_entryDate",
            }
        ]

        mock_isfile.return_value = True
        mock_extract_entries.return_value = prior_csv_data
        mock_remove_duplicates.side_effect = remove_duplicates

        combined_data = prior_csv_data + incoming_data

        expected_data = remove_duplicates(combined_data)

        with tempfile.TemporaryDirectory() as temp_dir:
            dummy_path = os.path.join(temp_dir, "test.csv")
            expected_df = pd.DataFrame(expected_data)

            items_to_csv(incoming_data, dummy_path)

            result_df = pd.read_csv(dummy_path)
            pd.testing.assert_frame_equal(
                expected_df.sort_values(list(expected_df.columns)).reset_index(
                    drop=True
                ),
                result_df.sort_values(list(expected_df.columns)).reset_index(drop=True),
            )
