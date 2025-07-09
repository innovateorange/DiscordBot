import re
from typing import List, Dict, Optional, Any
# from internships import getInternships
from data_collections.csv_updater import extract_entries_from_csv, remove_duplicates


def paste_jobs_command(command_args: str) -> Dict[str, Any]:
    """
    Parses the jobs command arguments to extract search filters from both flag notation and bracket notation.
    
    Args:
        command_args (str): The arguments string with format options:
                           Flag notation: "[search_term] [flags]"
                           Examples: "software -c google -l remote"
                                   "-c microsoft internship"
                                   "python -t internship -s summer"
                           
                           Bracket notation: "[role] [type] [season] [company] [location]"
                           Examples: "[software engineer] [internship] [summer] [google] [remote]"
                                   "[python developer] [] [] [microsoft] []"
    
    Returns:
        dict: Dictionary containing parsed parameters
    """
    pasted_params = {
        'role': None,
        'type': None,
        'season': None,
        'company': None,
        'location': None,
        'general_search': None
    }
    
    if not command_args.strip():
        return pasted_params
    
    # Check if using bracket notation
    if '[' in command_args and ']' in command_args:
        # Extract content from brackets using regex
        bracket_pattern = r'\[([^\]]*)\]'
        matches = re.findall(bracket_pattern, command_args)
        
        # Map matches to parameters in order: role, type, season, company, location
        param_keys = ['role', 'type', 'season', 'company', 'location']
        
        for i, match in enumerate(matches):
            if i < len(param_keys):
                # Only set non-empty values
                if match.strip():
                    pasted_params[param_keys[i]] = match.strip()
        
        return pasted_params
    
    # Otherwise, use flag notation parsing
    # Split command args into tokens
    tokens = command_args.split()
    
    # Parse flags and their values
    i = 0
    general_search_terms = []
    
    while i < len(tokens):
        token = tokens[i]
        
        # Check if it's a flag
        if token.startswith('-'):
            # Handle flag
            if token in ['-r', '--role'] and i + 1 < len(tokens):
                pasted_params['role'] = tokens[i + 1]
                i += 2
            elif token in ['-t', '--type'] and i + 1 < len(tokens):
                pasted_params['type'] = tokens[i + 1]
                i += 2
            elif token in ['-s', '--season'] and i + 1 < len(tokens):
                pasted_params['season'] = tokens[i + 1]
                i += 2
            elif token in ['-c', '--company'] and i + 1 < len(tokens):
                pasted_params['company'] = tokens[i + 1]
                i += 2
            elif token in ['-l', '--location'] and i + 1 < len(tokens):
                pasted_params['location'] = tokens[i + 1]
                i += 2
            else:
                # Unknown flag, skip it
                i += 1
        else:
            # It's a general search term
            general_search_terms.append(token)
            i += 1
    
    # Combine general search terms
    if general_search_terms:
        pasted_params['general_search'] = ' '.join(general_search_terms)
    
    return pasted_params


def filter_jobs(jobs: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Filters jobs based on provided criteria including general search and specific flags.
    
    Args:
        jobs (list): List of job dictionaries
        filters (dict): Dictionary of filter criteria
    
    Returns:
        list: Filtered list of jobs
    """
    filtered_jobs = []
    
    for job in jobs:
        include_job = True
        
        # General search filter - searches across all fields
        if filters.get('general_search') and include_job:
            general_search = filters['general_search'].lower()
            searchable_fields = [
                job.get('Title', ''),
                job.get('Description', ''),
                job.get('Type', ''),
                job.get('Company', ''),
                job.get('Location', ''),
                job.get('whenDate', ''),
                job.get('pubDate', '')
            ]
            
            # Check if general search term appears in any field
            general_match = any(general_search in field.lower() for field in searchable_fields)
            if not general_match:
                include_job = False
        
        # Role filter (check in title or description)
        if filters.get('role') and include_job:
            role_match = (
                filters['role'].lower() in job.get('Title', '').lower() or
                filters['role'].lower() in job.get('Description', '').lower() or
                filters['role'].lower() in job.get('Type', '').lower() or
                filters['role'].lower() in job.get('Company', '').lower() or
                filters['role'].lower() in job.get('Location', '').lower() 
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


def format_jobs_message(jobs: List[Dict[str, Any]], filters: Dict[str, Any] = None) -> str:
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
                if key == 'general_search':
                    filter_desc.append(f"search: {value}")
                else:
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


def getJobs(csv_file_path: str, command_args: str = "") -> List[Dict[str, Any]]:
    """
    Reads job data from CSV file and filters based on command parameters.

    Args:
        csv_file_path (str): Path to the CSV file containing job data
        command_args (str): Command arguments for filtering (e.g., "software -c google -l remote")

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
        
        # Apply filters if command_args provided
        if command_args.strip():
            filters = paste_jobs_command(command_args)
            jobs = filter_jobs(jobs, filters)
        
        return jobs

    except Exception as e:
        print(f"❌ Error loading or filtering jobs from CSV: {e}")
        return []