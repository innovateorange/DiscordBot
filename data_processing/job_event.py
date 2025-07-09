import re
from typing import List, Dict, Optional, Any
# from internships import getInternships
from data_collections.csv_updater import extract_entries_from_csv, remove_duplicates


def print_jobs_command(command_args: str) -> Dict[str, Optional[str]]:
        """
        Prints the jobs command arguments and extracts filter parameters.
        
        Args:
            command_args (str): The arguments string with format: [role] [type] [season] [company] [location]
        
        Returns:
            dict: Dictionary containing printed parameters
        """
        # Prints parameters in brackets
        params = re.findall(r'\[([^\]]*)\]', command_args)

        # Map to expected parameters
        param_names = ['role', 'type', 'season', 'company', 'location']
        printed_params = {}
        
        for i, name in enumerate(param_names):
            if i < len(params) and params[i].strip():
                printed_params[name] = params[i].strip()
            else:
                printed_params[name] = None
        
        return printed_params

def filter_jobs(jobs: List[Dict[str, Any]], filters: Dict[str, Optional[str]]) -> List[Dict[str, Any]]:
        """
        Filters jobs based on provided criteria.
        
        Args:
            jobs (list): List of job dictionaries
            filters (dict): Dictionary of filter criteria
        
        Returns:
            list: Filtered list of jobs
        """
        filtered_jobs = []
        
        for job in jobs:
            # Check each filter criterion
            include_job = True
            
            # Role filter (check in title or description)
            if filters.get('role'):
                role_match = (
                    filters['role'].lower() in job.get('Title', '').lower() or
                    filters['role'].lower() in job.get('Description', '').lower()
                )
                if not role_match:
                    include_job = False
            
            # Type filter (internship, full-time, part-time, etc.)
            if filters.get('type') and include_job:
                type_match = (
                    filters['type'].lower() in job.get('Title', '').lower() or
                    filters['type'].lower() in job.get('Description', '').lower() or
                    filters['type'].lower() in job.get('Type', '').lower()
                )
                if not type_match:
                    include_job = False
            
            # Season filter (Summer, Fall, Winter, Spring, etc.)
            if filters.get('season') and include_job:
                season_match = (
                    filters['season'].lower() in job.get('Title', '').lower() or
                    filters['season'].lower() in job.get('Description', '').lower() or
                    filters['season'].lower() in job.get('whenDate', '').lower() or
                    filters['season'].lower() in job.get('pubDate', '').lower()
                )
                if not season_match:
                    include_job = False
            
            # Company filter
            if filters.get('company') and include_job:
                company_match = (
                    filters['company'].lower() in job.get('Company', '').lower() or
                    filters['company'].lower() in job.get('Title', '').lower() or
                    filters['company'].lower() in job.get('Description', '').lower()
                )
                if not company_match:
                    include_job = False
            
            # Location filter
            if filters.get('location') and include_job:
                location_match = filters['location'].lower() in job.get('Location', '').lower()
                if not location_match:
                    include_job = False
            
            if include_job:
                filtered_jobs.append(job)
        
        return filtered_jobs

def format_jobs_message(jobs: List[Dict[str, Any]], filters: Dict[str, Optional[str]] = None) -> str:
        """
        Formats job results into a Discord message.
        
        Args:
            jobs (list): List of job dictionaries
            filters (dict, optional): Applied filters for context
        
        Returns:
            str: Formatted message string
        """
        if not jobs:
            return "💼 No jobs found matching your criteria."
        
        # Build filter description
        filter_desc = []
        if filters:
            for key, value in filters.items():
                if value:
                    filter_desc.append(f"{key}: {value}")
        
        filter_text = f" (Filters: {', '.join(filter_desc)})" if filter_desc else ""
        
        message = f"💼 **Found {len(jobs)} job(s){filter_text}:**\n\n"
        
        # Limit to first 10 jobs to avoid Discord message length limits
        display_jobs = jobs[:10]
        
        for job in display_jobs:
            company = job.get('Title', 'Unknown Company')
            location = job.get('Location', 'Location not specified')
            when_date = job.get('whenDate', '')
            pub_date = job.get('pubDate', '')
            link = job.get('link', '')
            
            # Use the most descriptive title available
            title = job.get('Description', job.get('Title', 'Untitled Position'))
            
            job_text = f"**{title}**\n"
            job_text += f"🏢 {company}\n"
            
            if location:
                job_text += f"📍 {location}"
            
            job_text += "\n"
            
            # Add date information if available
            if when_date:
                job_text += f"📅 {when_date}\n"
            if pub_date:
                job_text += f"📅 Posted: {pub_date}\n"
            
            if link:
                job_text += f"🔗 [Apply Here]({link})\n"
            
            message += job_text + "\n"
        
        if len(jobs) > 10:
            message += f"... and {len(jobs) - 10} more jobs. Use more specific filters to narrow results."
        
        return message


""" This is for right now, until internships.py is properly set up. """
def getJobs(csv_file_path: str) -> List[Dict[str, Any]]:
    """
    Reads job data from CSV file and optionally filters based on command parameters.

    Args:
        csv_file_path (str): Path to the CSV file containing job data

    Returns:
        list: List of job dictionaries matching the criteria
    """
    try:
        # Load and deduplicate CSV data using csv_updater functions
        jobs = extract_entries_from_csv(csv_file_path)
        jobs = remove_duplicates(jobs)
        
        # Filter to keep only jobs and internships (case-insensitive with variations)
        allowed_types = {"job", "internship", "full-time", "part-time", "co-op", "coop"}
        jobs = [job for job in jobs if job.get("Type", "").lower() in allowed_types]
        
        return jobs

    except Exception as e:
        print(f"❌ Error loading or filtering jobs from CSV: {e}")
        return []
