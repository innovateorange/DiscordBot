"""
File `get_type_data.py` is responsible for retrieving specific types of data
    from a CSV file.
"""

import datetime
from typing import Any

from data_collections.csv_updater import (
    extract_entries_from_csv,
)


def get_type_data(csv_file_path: str, data_type: str) -> list[dict[str, Any]]:
    """
    Retrieves data of a specific type from a CSV file and returns it as a
        list of dictionaries.

    Args:
        csv_file_path (str): Path to the CSV file containing data.
        data_type (str): Type of data to retrieve (e.g., "event").

    Returns:
        list[dict[str, Any]]: List of dictionaries containing the specified
            type of data.
    """
    items = []
    for entry in extract_entries_from_csv(csv_file_path):
        if entry.get("Type") == data_type:
            item = {
                "Type": entry.get("Type", ""),
                "subType": entry.get("subType", ""),
                "Company": entry.get("Company", ""),
                "Title": entry.get("Title", ""),
                "Description": entry.get("Description", ""),
                "whenDate": entry.get("whenDate", ""),
                "pubDate": entry.get("pubDate", ""),
                "Location": entry.get("Location", ""),
                "link": entry.get("link", ""),
                "entryDate": datetime.datetime.now(tz=datetime.timezone.utc),
            }
            items.append(item)
    return items
