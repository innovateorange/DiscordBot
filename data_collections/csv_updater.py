from data_collections.getEvents import getEvents
import os
import pandas as pd
from dotenv import load_dotenv


def items_to_csv(data: list[dict], path_to_file: str):
    """
    Save a list of dictionaries to a CSV file.

    Args:
        data (list[dict]): List of dictionaries containing the data to save
        path_to_file (str): Path where the CSV file should be saved

    Raises:
        RuntimeError: If there's an error during CSV creation or saving

    Example:
        >>> events = [{'title': 'Event 1', 'date': '2024-01-01'}]
        >>> items_to_csv(events, 'runningCSV.csv')
        Items Successfully saved to runningCSV.csv
    """
    if data:
        try:
            if not os.path.isfile(path_to_file):
                raise ValueError("path_to_csv not found")
            # Future Implementation Documented below
            # append data from running
            # remove the duplicates
            data_frame = pd.DataFrame(data)
            data_frame.to_csv(path_to_file, index=False)
            print(f"Items Successfully saved to {path_to_file}")
        except Exception as e:
            raise RuntimeError(f"Failed to save data to CSV: {e}") from e


if __name__ == "__main__":
    load_dotenv()
    url = os.getenv("EVENTS_RSS_URL")
    if not url:
        raise ValueError("EVENTS_RSS_URL variable not set")

    data = getEvents(url)
    items_to_csv(data, "data_collections/runningCSV.csv")
