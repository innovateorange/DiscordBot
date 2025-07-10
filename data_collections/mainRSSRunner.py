""""""

from dotenv import load_dotenv
from .events import getEvents
from .internships import getInternships
from .csv_updater import items_to_csv
import os


def run_events_RSS(url):
    if not url:
        raise ValueError("EVENTS_RSS_URL variable not set")
    data = getEvents(url)
    return data


def run_internships_markdown(url):
    if not url:
        raise ValueError("INTERNSHIPS_MARKDOWN_URL variable not set")
    data = getInternships(url)
    return data


if __name__ == "__main__":
    load_dotenv()

    task_type = os.getenv("TASK_TYPE")
    if not task_type:
        raise ValueError("TASK_TYPE variable not set")

    if task_type == "EVENTS":
        url = os.getenv("EVENTS_RSS_URL")
        data = run_events_RSS(url)
    elif task_type == "INTERNSHIPS":
        url = os.getenv("INTERNSHIPS_MARKDOWN_URL")
        data = run_internships_markdown(url)
    else:
        raise ValueError(f"Unsupported TASK_TYPE: {task_type}")
    items_to_csv(data, "data_collections/runningCSV.csv")
