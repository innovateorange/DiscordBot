"""Referenced from bot.py and filters and returns
jobs that match the inputted criteria.
"""

from typing import Any
from datetime import datetime

from data_processing.get_type_data import (
    get_type_data,
)


def filter_jobs(jobs: list[dict[str, Any]], _filters: str) -> list[dict[str, Any]]:
    """
    Filters jobs based on provided criteria

    Args:
        jobs (list): List of job dictionaries
        _filters (str): String of filter criteria

    Returns:
        list: Filtered list of jobs
    """
    if not _filters:
        return jobs
    filtered_jobs = []
    for job in jobs:
        include_job = False
        confidence = 0
        search_terms = _filters.split()
        searchable_fields = [
            job.get("Title", ""),
            job.get("subType", ""),
            job.get("Company", ""),
            job.get("Description", ""),
            job.get("Location", ""),
            job.get("whenDate", ""),
            job.get("pubDate", ""),
        ]
        for term in search_terms:
            for field in searchable_fields:
                if term.lower() in field.lower():
                    include_job = True
                    confidence += 1
                    break
        if include_job:
            job.update({"confidence": confidence})
            filtered_jobs.append(job)
    filtered_jobs = sorted(filtered_jobs, key=lambda x: x["confidence"], reverse=True)
    return filtered_jobs


def format_jobs_message(jobs: list[dict[str, Any]], _filters: str) -> str:
    """
    Formats job results into a Discord message.

    Args:
        jobs (list): List of job dictionaries
        _filters (str, optional): Applied filters for context

    Returns:
        str: Formatted message string
    """
    if not jobs:
        return "💼 No jobs found matching your criteria."
    filter_text = f" (Filters: {_filters.strip()})" if _filters else ""
    message = f"💼 **Found {len(jobs)} job(s):{filter_text}**\n\n"
    limited_jobs = jobs[:5]
    for job in limited_jobs:
        title = job.get("Title", "Untitled Position")
        job_type = job.get("Type", "")
        company_name = job.get("Company", "")
        location = job.get("Location", "")

        if isinstance(location, str) and location.startswith("[") and location.endswith("]"):
            location_str = location.replace("[", "").replace("]", "").replace("'", "")
        else:
            location_str = str(location)

        description = job.get("Description", "")
        when_date = job.get("whenDate", "")
        pub_date = job.get("pubDate", "")
        link = job.get("link", "")
        formatted_pub_date = pub_date

        if pub_date:
            try:
                dt = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z")
                formatted_pub_date = dt.strftime("%b %d %Y")
            except Exception:
                formatted_pub_date = pub_date

        job_text = f"**{title}**\n"
        job_text += f"📝 {job_type}\n"
        job_text += f"🏢 {company_name}\n"
        if location_str.strip():
            job_text += f"📍 {location_str}\n"
        if when_date:
            job_text += f"📅 Start Date: {when_date}\n"
        if pub_date:
            job_text += f"📅 Posted: {formatted_pub_date}\n"
        if description:
            job_text += f"📝 {description}\n"
        if link:
            job_text += f"🔗 [Apply Here](<{link}>)\n"
        message += job_text + "\n"
    if len(jobs) > 5:
        message += f"... and {len(jobs) - 5} more jobs. Use more specific filters to narrow results."  # noqa: E501
    return message


def get_jobs(csv_file_path: str) -> list[dict[str, Any]]:
    """
    Reads job data from CSV file and filters based on command parameters.

    Args:
        csv_file_path (str): Path to the CSV file containing job data

    Returns:
        list: List of job dictionaries matching the criteria
    """
    try:
        jobs = get_type_data(csv_file_path, "Job")
        _jobs = get_type_data(csv_file_path, "Internship")
        jobs.extend(_jobs)
    except RuntimeError:
        print("Error loading or filtering jobs from CSV")
        raise
    return jobs
