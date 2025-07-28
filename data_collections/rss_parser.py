import datetime
import re

import feedparser

from .constants import VALID_STATES


def getInternships(url):
    return parse_rss_feed(url, "Internship")


def getJobs(url):
    return parse_rss_feed(url, "Job")


def parse_rss_feed(url, item_type):
    """Generic RSS feed parser for jobs and internships"""
    try:
        data = feedparser.parse(url)
    except (ConnectionError, TimeoutError) as e:
        raise RuntimeError(
            f"Network error while fetching RSS feed from {url}: {e}"
        ) from e
    except Exception as e:
        raise RuntimeError(f"Failed to parse the RSS feed from {url}: {e}") from e

    if getattr(data, "bozo", False) and getattr(data, "bozo_exception", None):
        raise RuntimeError(
            f"Malformed RSS feed {url!r}: {getattr(data, 'bozo_exception', '')}"
        )

    items = []
    for entry in data.get("entries", []):
        title = re.sub(
            r"\s+at\s+.+$", "", entry.get("title", "").strip(), flags=re.IGNORECASE
        )
        descrip = entry.get("description", "")

        company = "Unknown"
        whenDate = "Unknown"
        locations = "Unknown"

        # Retrieves Employer Information
        match = re.search(
            r"Employer:\s*([^\n<]+?)(?=\n|<|Expires:|$)", descrip, re.DOTALL
        )
        if match:
            company = match.group(1).strip()

        # Retrieves whenDate Information
        match = re.search(r"Expires:\s*(\d{2}/\d{2}/\d{4})", descrip)
        if match:
            whenDate = match.group(1)

        # Retrieves Locations Information
        locations = extract_locations(descrip)

        pubDate = entry.get("published", "")
        link = entry.get("link", "")

        item = {
            "Type": item_type,
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

        items.append(item)
    return items


def extract_locations(description):
    if not description:
        return ["Unknown"]
    result = set()
    # Compile regex patterns once for better performance
    remote_pattern = re.compile(r"\b(remote|telecommute)\b", re.IGNORECASE)
    hybrid_pattern = re.compile(r"\bhybrid\b", re.IGNORECASE)
    location_pattern = re.compile(r"Location\s*:\s*(.+?)(?:\n|$)", re.IGNORECASE)
    city_state_pattern = re.compile(r"([A-Za-z .\-\'&]+?, [A-Z]{2})")
    # Handle Remote / Hybrid
    if remote_pattern.search(description):
        result.add("Remote")
    if hybrid_pattern.search(description):
        result.add("Hybrid")
    # Extract from lines starting with Location:
    location_line_match = location_pattern.search(description)
    if location_line_match:
        location_line = location_line_match.group(1).strip()
        # find all "City, ST" or similar
        matches = city_state_pattern.findall(location_line)
        for loc in matches:
            loc = loc.strip()
            # Validate state part
            if ", " in loc:
                *_, state = loc.rsplit(", ", 1)
                if state in VALID_STATES and 1 <= len(loc.split()) <= 4:
                    # Word count filter: e.g., skip "Main Office Downtown Boston, MA"
                    result.add(loc)
    return list(result) if result else ["Unknown"]
