import feedparser
from dotenv import load_dotenv
import re
import datetime

# Load environment variables from a .env file, most likely going to be used outside of this file
#load_dotenv()

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
    """

    data = feedparser.parse(url)
    events = []

    for entry in data["entries"]:
        # Splits the title to remove the date in parentheses
        title = re.split(r"\s*\([^()]*\s*\d{4}", entry.get("title", ""))[0].strip()
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
            "Title": title,
            "Description": descrip,
            "whenDate": when,
            "pubDate": entry.get("published", ""),
            "Location": location,
            "link": entry.get("link", ""),
            "entryDate": datetime.datetime.now(),
        }

        events.append(event)  # list of each event which is stored in a dictionary
    return events


# Temporary code to test the function
# Remove and place in correct function call area when integrating into production
# Most likely going to be ran by a cron job or similar scheduler
# if __name__ == "__main__":
#     # Load the URL from environment variables and call the function
#     try:
#         url = os.getenv("url")
#         if not url:
#             raise ValueError("URL not found in environment variables.")
#     except ValueError as e:
#         print(f"Error: {e}")
#     getEvents(url)
