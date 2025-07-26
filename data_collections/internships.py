import datetime
import re

import feedparser

from .jobs import extract_locations

VALID_STATES = {
    "AL",
    "AK",
    "AZ",
    "AR",
    "CA",
    "CO",
    "CT",
    "DE",
    "FL",
    "GA",
    "HI",
    "ID",
    "IL",
    "IN",
    "IA",
    "KS",
    "KY",
    "LA",
    "ME",
    "MD",
    "MA",
    "MI",
    "MN",
    "MS",
    "MO",
    "MT",
    "NE",
    "NV",
    "NH",
    "NJ",
    "NM",
    "NY",
    "NC",
    "ND",
    "OH",
    "OK",
    "OR",
    "PA",
    "RI",
    "SC",
    "SD",
    "TN",
    "TX",
    "UT",
    "VT",
    "VA",
    "WA",
    "WV",
    "WI",
    "WY",
}


def getInternships(url):
    try:
        data = feedparser.parse(url)
    except Exception as e:
        raise RuntimeError(f"Failed to parse the RSS feed from {url}: {e}") from e

    if getattr(data, "bozo", False):
        raise RuntimeError(
            f"Malformed RSS feed {url!r}: {getattr(data, 'bozo_exception', '')}"
        )

    internships = []

    for entry in data.get("entries", []):
        title = re.sub(r"\s+at.*", "", entry.get("title", ""), flags=re.IGNORECASE)
        descrip = entry.get("description", "")

        company = "Unknown"
        whenDate = "Unknown"
        locations = "Unknown"

        # Retrieves Employer Information
        match = re.search(r"Employer:.*?(?=\n|<|Expires:)", descrip, re.DOTALL)
        if match:
            company = match.group().removeprefix("Employer: ").strip()

        # Retrieves whenDate Information
        match = re.search(r"Expires:\s*(\d{2}/\d{2}/\d{4})", descrip)
        if match:
            whenDate = match.group(1)

        # Retrieves Locations Information
        locations = extract_locations(descrip)

        pubDate = entry.get("published", "")
        link = entry.get("link", "")

        internship = {
            "Type": "Internship",
            "subType": "",
            "Company": company,
            "Title": title,
            "Description": "",
            "whenDate": whenDate,
            "pubDate": pubDate,
            "Location": locations,
            "link": link,
            "entryDate": datetime.datetime.now(tz=datetime.timezone.utc),
        }

        internships.append(internship)

    return internships
