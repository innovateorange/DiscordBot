"""
mainRSSRunner.py

This module provides functionality to run RSS event collection tasks and
save the results to a CSV file.

This Module does the following:
    - loads environment variables (RSS Feed URLS)
    - determines the task type (from ENV variables)
    - fetches event data from an RSS feed
    - writes the collected items to a CSV file.

Functions:
    run_get_events(url, subType):
        Fetches event data from the provided RSS URL using the getEvents function.

Usage:
    Run this module as a script. It expects the following environment variables:
        - TASK_TYPE: Specifies the type of task to run
            (e.g., "INFO_SESSION", "WORKSHOP", "SPEAKER_PANEL", "OTHER", "CAREER_FAIR").
        - Corresponding RSS URL environment variable for the selected TASK_TYPE.

Raises:
    ValueError:
        - If required environment variables are not set
        - If an unsupported TASK_TYPE is provided.

"""

import os

from dotenv import load_dotenv

from .csv_updater import items_to_csv
from .events import getEvents
from .internships import getInternships
from .jobs import getJobs


def run_events_RSS(url, subType):
    if not url:
        raise ValueError(f"{subType}_RSS variable not set")
    data = getEvents(url, subType)
    return data


def run_jobs_RSS(url):
    if not url:
        raise ValueError("JOBS_RSS variable not set")
    data = getJobs(url)
    return data


def run_internships_RSS(url):
    if not url:
        raise ValueError("INTERNSHIPS_RSS variable not set")
    data = getInternships(url)
    return data


if __name__ == "__main__":
    load_dotenv()

    task_type = os.getenv("TASK_TYPE")
    if not task_type:
        raise ValueError("TASK_TYPE variable not set")

    url = None
    if task_type == "INFO_SESSION":
        url = os.getenv("INFO_SESSION_RSS")
        data = run_events_RSS(url, task_type)
    elif task_type == "WORKSHOP":
        url = os.getenv("WORKSHOP_RSS")
        data = run_events_RSS(url, task_type)
    elif task_type == "SPEAKER_PANEL":
        url = os.getenv("SPEAKER_PANEL_RSS")
        data = run_events_RSS(url, task_type)
    elif task_type == "OTHER":
        url = os.getenv("OTHER_RSS")
        data = run_events_RSS(url, task_type)
    elif task_type == "CAREER_FAIR":
        url = os.getenv("CAREER_FAIR")
        data = run_events_RSS(url, task_type)
    elif task_type == "JOBS":
        url = os.getenv("JOBS_RSS")
        data = run_jobs_RSS(url)
    elif task_type == "INTERNSHIPS":
        url = os.getenv("INTERNSHIPS_RSS")
        data = run_internships_RSS(url)
    else:
        raise ValueError(f"Unsupported TASK_TYPE: {task_type}")

    items_to_csv(data, "data_collections/runningCSV.csv")
