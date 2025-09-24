"""Referenced from bot.py and filters and returns
jobs that match the inputted criteria.
"""
import discord

from datetime import datetime
from typing import Any
from discord.ext import commands
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
            filtered_jobs.append({**job, "confidence": confidence})
    filtered_jobs = sorted(filtered_jobs, key=lambda x: x["confidence"], reverse=True)
    return filtered_jobs


def format_jobs_message(jobs: list[dict[str, Any]], _filters: str = "") -> tuple[list[discord.Embed], str | None]:
    """
    Formats job results into Discord embeds and an optional summary string.

    Args:
        jobs (list): List of job dictionaries
        _filters (str, optional): Applied filters for context

    Returns:
        tuple: (List of discord.Embed objects, Optional additional jobs string)
    """
    if not jobs:
        return [], "💼 No jobs found matching your criteria."
    embeds = []
    limited_jobs = jobs[:5]
    for job in limited_jobs:
        title = job.get("Title", "Untitled Position")
        job_type = job.get("Type", "")
        company_name = job.get("Company", "")
        location = job.get("Location", "")

        if (
            isinstance(location, str)
            and location.startswith("[")
            and location.endswith("]")
        ):
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

        embed = discord.Embed(title=title, description=description, color=0x00ff00)
        embed.add_field(name="Type", value=job_type, inline=False)
        embed.add_field(name="Company", value=company_name, inline=False)
        if location_str.strip():
            embed.add_field(name="Location", value=location_str, inline=False)
        if when_date:
            embed.add_field(name="Start Date", value=when_date, inline=False)
        if pub_date:
            embed.add_field(name="Posted", value=formatted_pub_date, inline=False)
        if description:
            embed.add_field(name="Description", value=description, inline=False)
        if link:
            embed.add_field(name="Apply Here", value=f"[Link]({link})", inline=False)
        embeds.append(embed)
    additional_jobs = None
    if len(jobs) > 5:
        additional_jobs = f"... and {len(jobs) - 5} more jobs. Use more specific filters to narrow results."
    return embeds, additional_jobs


def get_jobs(csv_file_path: str) -> list[dict[str, Any]]:
    """
    Reads job and internship data from CSV file and filters based on command parameters.

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
