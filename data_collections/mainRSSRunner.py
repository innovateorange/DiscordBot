""""""

import os

from dotenv import load_dotenv

from .csv_updater import items_to_csv
from .events import getEvents


def run_events_RSS(url):
    if not url:
        raise ValueError("EVENTS_RSS_URL variable not set")
    data = getEvents(url)
    return data


if __name__ == "__main__":
    load_dotenv()

    task_type = os.getenv("TASK_TYPE")
    if not task_type:
        raise ValueError("TASK_TYPE variable not set")

    if task_type == "EVENTS":
        url = os.getenv("EVENTS_RSS_URL")
        data = run_events_RSS(url)
    else:
        raise ValueError(f"Unsupported TASK_TYPE: {task_type}")
    items_to_csv(data, "data_collections/runningCSV.csv")
