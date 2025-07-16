import datetime
import re

import feedparser


def getEvents(url):
    """
    Parses the RSS feed from the given URL and extracts event details.
    Args:
        url (str): The URL of the RSS feed.
    Returns:
        list: A list of dictionaries, each containing details of an event.
    Each Event Contains:
        - Type: The type of the event (always "Event").
        - Title: The title of the event.
        - Description: The description of the event.
        - whenDate: The date and time of the event.
        - pubDate: The publication date of the event.
        - Location: The location of the event.
        - link: The link to the event details.
        - entryDate: Date that the entry entered the our `runningCSV.csv`
    """
    try:
        data = feedparser.parse(url)
    except Exception as e:
        raise RuntimeError(f"Failed to parse the RSS feed from {url}: {e}") from e

    if getattr(data, "bozo", False):
        raise RuntimeError(
            f"Malformed RSS feed {url!r}: {getattr(data, 'bozo_exception', '')}"
        )

    events = []

    for entry in data.get("entries", []):
        # Splits the title to remove the date in parentheses
        title = re.sub(r"\s*\([^)]+\)\s*$", "", entry.get("title", "")).strip()
        descrip = entry.get("description", "")
        when = ""
        location = ""

        # gets the whenDate and the Location by string manipulation
        # if unable to find, then keeps it empty
        if "When:" in descrip:
            try:
                when = descrip.split("When:")[1].split("\n")[0].strip()
            except IndexError:
                when = ""

        if "Location:" in descrip:
            try:
                location = descrip.split("Location:")[1].split("\n")[0].strip()
            except IndexError:
                location = ""

        # Remove the "When:" and "Location:" from the description
        descrip = re.sub(
            r"^\s*(When|Location):.*?(\n|$)",
            "",
            entry.get("description", ""),
            flags=re.IGNORECASE | re.MULTILINE,
        ).strip()

        event = {
            "Type": "Event",
            "Company": "",
            "Title": title,
            "Description": descrip,
            "whenDate": when,
            "pubDate": entry.get("published", ""),
            "Location": location,
            "link": entry.get("link", ""),
            "entryDate": datetime.datetime.now(tz=datetime.timezone.utc),
        }

        events.append(event)  # list of each event which is stored in a dictionary
    return events
