import datetime
import re

import feedparser

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


def getJobs(url):
    try:
        data = feedparser.parse(url)
    except Exception as e:
        raise RuntimeError(f"Failed to parse the RSS feed from {url}: {e}") from e

    if getattr(data, "bozo", False):
        raise RuntimeError(
            f"Malformed RSS feed {url!r}: {getattr(data, 'bozo_exception', '')}"
        )

    jobs = []

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

        job = {
            "Type": "Job",
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

        jobs.append(job)

    return jobs


def extract_locations(description):
    if not description:
        return ["Unknown"]

    result = set()

    # Handle Remote / Hybrid
    if re.search(r"\b(remote|telecommute)\b", description, re.IGNORECASE):
        result.add("Remote")
    if re.search(r"\bhybrid\b", description, re.IGNORECASE):
        result.add("Hybrid")

    # Extract from lines starting with Location:
    location_line_match = re.search(
        r"Location\s*:\s*(.+?)(?:\n|$)", description, re.IGNORECASE
    )
    if location_line_match:
        location_line = location_line_match.group(1).strip()

        # find all "City, ST" or similar
        matches = re.findall(r"([A-Za-z .\-\'&]+?, [A-Z]{2})", location_line)
        for loc in matches:
            loc = loc.strip()

            # Validate state part
            if ", " in loc:
                *_, state = loc.rsplit(", ", 1)
                if state in VALID_STATES and len(loc.split()) <= 3:
                    # Word count filter: e.g., skip "Main Office Downtown Boston, MA"
                    result.add(loc)

    return list(result) if result else ["Unknown"]
