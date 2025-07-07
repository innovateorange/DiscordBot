import requests
import re
import datetime
from typing import List, Dict


def getInternships(url: str) -> List[Dict]:
    """
    Parses a markdown file from the given URL and extracts internship details.
    
    Args:
        url (str): The URL of the markdown file containing internship data.
        
    Returns:
        list: A list of dictionaries, each containing details of an internship.
        
    Each Internship Contains:
        - Type: The type of the entry (always "Internship").
        - Title: The company name.
        - Description: The role/position description.
        - whenDate: The date and time of the internship (left blank).
        - pubDate: The date posted.
        - Location: The location of the internship.
        - link: The link to the application.
        - entryDate: Date that the entry entered our `runningCSV.csv`
        
    Raises:
        RuntimeError: If there's an error fetching or parsing the markdown file.
    """
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        markdown_content = response.text
    except Exception as e:
        raise RuntimeError(f"Failed to fetch the markdown file from {url}: {e}")

    if not markdown_content.strip():
        raise RuntimeError(f"Empty markdown file at {url}")

    internships = []
    
    # Split content into sections (assuming internships are separated by headers or sections)
    # Look for patterns that indicate internship entries
    internship_sections = _parse_internship_sections(markdown_content)
    
    for section in internship_sections:
        internship_data = _extract_internship_data(section)
        if internship_data:
            internship_data["entryDate"] = datetime.datetime.now(tz=datetime.timezone.utc)
            internships.append(internship_data)
    
    return internships


def _parse_internship_sections(content: str) -> List[str]:
    """
    Parse the markdown content into sections that might contain internship data.
    
    Args:
        content (str): The markdown content to parse.
        
    Returns:
        List[str]: List of sections that might contain internship data.
    """
    # Look for markdown tables first
    table_pattern = r'\|.*\|.*\|.*\|.*\|.*\|'
    table_matches = re.findall(table_pattern, content, re.MULTILINE)
    
    if table_matches:
        # Extract table rows that contain internship data
        table_rows = []
        for match in table_matches:
            # Skip header and separator rows
            if not re.match(r'^\|.*-.*\|', match) and '|' in match:
                table_rows.append(match)
        return table_rows
    
    # Fallback to section-based parsing, split by headers (with or without space), --- or ***
    sections = re.split(r'(?:\n\s*)?(?:#{1,6}\s*|---+|\*\*\*+)(?:\s*\n)?', content)
    valid_sections = [section.strip() for section in sections if len(section.strip()) > 50]
    return valid_sections


def _extract_internship_data(section: str) -> Dict:
    """
    Extract internship data from a section of markdown content.
    
    Args:
        section (str): A section of markdown content that might contain internship data.
        
    Returns:
        Dict: A dictionary containing internship data, or None if no valid data found.
    """
    # Initialize with default values
    internship = {
        "Type": "Internship",
        "Title": "",
        "Description": "",
        "whenDate": "",  # Left blank as per requirements
        "pubDate": "",
        "Location": "",
        "link": ""
    }
    
    # Check if this is a table row
    if section.startswith('|') and section.endswith('|'):
        return _extract_from_table_row(section)
    
    # Extract company name (Title)
    company_patterns = [
        r'(?:Company|Organization|Firm):\s*([^\n]+)',
        r'(?:at|with)\s+([A-Z][A-Za-z\s&.,]+?)(?:\s|$|\n)',
        r'([A-Z][A-Za-z\s&.,]+?)\s+(?:Internship|Position|Role)',
        r'#+\s*([A-Z][A-Za-z\s&.,]+?)(?:\s|$|\n)',
        r'^([A-Z][A-Za-z\s&.,]+)$'  # Header line with just company name
    ]
    
    for pattern in company_patterns:
        match = re.search(pattern, section, re.IGNORECASE | re.MULTILINE)
        if match:
            internship["Title"] = match.group(1).strip()
            break
    
    # Extract role/position (Description)
    role_patterns = [
        r'(?:Role|Position|Title):\s*([^\n]+)',
        r'(?:Internship|Position|Role)\s+(?:for|as)\s+([^\n]+)',
        r'([A-Za-z\s]+(?:Intern|Internship|Developer|Engineer|Analyst|Designer|Manager))',
    ]
    
    for pattern in role_patterns:
        match = re.search(pattern, section, re.IGNORECASE)
        if match:
            internship["Description"] = match.group(1).strip()
            break
    
    # Extract date posted (pubDate)
    date_patterns = [
        r'(?:Posted|Date|Published):\s*([^\n]+)',
        r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'(\w+\s+\d{1,2},?\s+\d{4})',
        r'(\d{4}-\d{2}-\d{2})'
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, section, re.IGNORECASE)
        if match:
            internship["pubDate"] = match.group(1).strip()
            break
    
    # Extract location
    location_patterns = [
        r'(?:Location|Place|Where):\s*([^\n]+)',
        r'(?:in|at)\s+([A-Z][A-Za-z\s,]+?)(?:\s|$|\n)',
        r'(Remote|On-site|Hybrid)',
        r'([A-Z][A-Za-z\s,]+?,\s*[A-Z]{2})'  # City, State format
    ]
    
    for pattern in location_patterns:
        match = re.search(pattern, section, re.IGNORECASE)
        if match:
            internship["Location"] = match.group(1).strip()
            break
    
    # Extract application link
    link_patterns = [
        r'(?:Apply|Application|Link):\s*(https?://[^\s\n)]+)',
        r'(https?://[^\s\n)]+)',
        r'\[([^\]]+)\]\((https?://[^\s\n)]+)\)'  # Markdown link format
    ]
    
    for pattern in link_patterns:
        match = re.search(pattern, section, re.IGNORECASE)
        if match:
            if len(match.groups()) == 2:  # Markdown link format
                internship["link"] = match.group(2)
            else:
                internship["link"] = match.group(1)
            break
    
    # Only return if at least one main field is present and not just random text
    main_fields = [internship["Title"], internship["Description"], internship["pubDate"], internship["Location"], internship["link"]]
    if any(f and not f.lower().startswith("this is just some random text") for f in main_fields):
        return internship
    
    return None


def _extract_from_table_row(row: str) -> Dict:
    """
    Extract internship data from a markdown table row.
    
    Args:
        row (str): A markdown table row containing internship data.
        
    Returns:
        Dict: A dictionary containing internship data, or None if no valid data found.
    """
    # Split the row by | and clean up
    cells = [cell.strip() for cell in row.split('|')[1:-1]]  # Remove first and last empty cells
    
    if len(cells) < 5:  # Need at least Company, Role, Location, Link, Date
        return None
    
    # Skip header and separator rows
    if any(cell.lower() in ['company', 'role', 'location', 'link', 'date', '-------', '----'] for cell in cells):
        return None
    
    # Skip rows that start with arrows (↳) as they are duplicate entries for the same company
    if cells[0].strip() == '↳':
        return None
    
    internship = {
        "Type": "Internship",
        "Title": cells[0].strip(),
        "Description": cells[1].strip(),
        "whenDate": "",  # Left blank as per requirements
        "Location": cells[2].strip(),
        "link": _extract_link_from_html(cells[3].strip()),
        "pubDate": cells[4].strip() if len(cells) > 4 else ""
    }
    
    # Clean up the data
    for key in internship:
        if key != "Type" and key != "whenDate":
            # Remove markdown formatting and HTML tags
            internship[key] = re.sub(r'\*\*([^*]+)\*\*', r'\1', internship[key])
            internship[key] = re.sub(r'\*([^*]+)\*', r'\1', internship[key])
            internship[key] = re.sub(r'<[^>]+>', '', internship[key])  # Remove HTML tags
            internship[key] = internship[key].strip()
    
    # Only return if we have meaningful data
    if (internship["Title"] and internship["Title"] != "Company" and 
        internship["Description"] and internship["Description"] != "Role"):
        return internship
    
    return None


def _extract_link_from_html(html_cell: str) -> str:
    """
    Extract the actual URL from an HTML link cell.
    
    Args:
        html_cell (str): HTML content like '<a href="url">text</a>'
        
    Returns:
        str: The extracted URL or empty string if not found
    """
    # Extract href from HTML anchor tag
    href_match = re.search(r'href=["\']([^"\']+)["\']', html_cell)
    if href_match:
        return href_match.group(1)
    
    # If no HTML link found, return the original content
    return html_cell 