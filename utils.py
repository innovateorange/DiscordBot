# utils.py
# Utility functions for data processing and Discord interactions

import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
import discord
from models import Event, EventType, Resource, JobPosting, InterviewQuestion, NetworkingTip, Skill

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_datetime(date_str: str) -> Optional[datetime]:
    """
    Parse datetime from various string formats.

    Args:
        date_str: Date string to parse

    Returns:
        Parsed datetime object or None if parsing fails
    """
    formats = [
        "%A, %B %d, %Y at %I:%M %p %Z",  # "Friday, April 25th 2025, 6:00 pm EDT"
        "%a, %d %b %Y %H:%M:%S %z",      # "Tue, 15 Apr 2025 10:00:00 -0400"
        "%Y-%m-%d %H:%M:%S",             # ISO format
        "%Y-%m-%d",                      # Date only
    ]

    for fmt in formats:
        try:
            # Clean up the date string
            cleaned = date_str.replace("th", "").replace("st", "").replace("nd", "").replace("rd", "")
            return datetime.strptime(cleaned, fmt)
        except ValueError:
            continue

    logger.warning(f"Could not parse datetime: {date_str}")
    return None


def load_events_from_csv(csv_path: str) -> List[Event]:
    """
    Load events from CSV file.

    Args:
        csv_path: Path to the CSV file

    Returns:
        List of Event objects
    """
    events = []

    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    # Parse dates
                    when_date = row.get('whenDate', '')
                    pub_date = row.get('pubDate', '')

                    # Handle date ranges (e.g., "Friday, April 25th 2025, 6:00 pm EDT - Sunday, April 27th 2025, 12:00 pm EDT")
                    if ' - ' in when_date:
                        start_str, end_str = when_date.split(' - ', 1)
                        start_date = parse_datetime(start_str.strip())
                        end_date = parse_datetime(end_str.strip())
                    else:
                        start_date = parse_datetime(when_date)
                        end_date = None

                    pub_datetime = parse_datetime(pub_date) if pub_date else None

                    # Determine event type
                    event_type_str = row.get('Type', 'Event')
                    try:
                        event_type = EventType(event_type_str)
                    except ValueError:
                        event_type = EventType.EVENT

                    event = Event(
                        title=row.get('Title', ''),
                        description=row.get('Description', ''),
                        start_date=start_date,
                        end_date=end_date,
                        location=row.get('Location', ''),
                        link=row.get('link', ''),
                        event_type=event_type,
                        pub_date=pub_datetime
                    )

                    events.append(event)

                except Exception as e:
                    logger.error(f"Error parsing event row: {row}. Error: {e}")
                    continue

    except FileNotFoundError:
        logger.error(f"Events CSV file not found: {csv_path}")
    except Exception as e:
        logger.error(f"Error loading events from CSV: {e}")

    return events


def get_upcoming_events(events: List[Event], limit: int = 5) -> List[Event]:
    """
    Get upcoming events sorted by date.

    Args:
        events: List of all events
        limit: Maximum number of events to return

    Returns:
        List of upcoming events
    """
    upcoming = [event for event in events if event.is_upcoming]
    upcoming.sort(key=lambda x: x.start_date)
    return upcoming[:limit]


def create_embed(title: str, description: str = "", color: int = 0x00ff00) -> discord.Embed:
    """
    Create a Discord embed with consistent styling.

    Args:
        title: Embed title
        description: Embed description
        color: Embed color (hex)

    Returns:
        Discord Embed object
    """
    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=datetime.now()
    )
    embed.set_footer(text="CuseBot - Career Development Assistant")
    return embed


def add_field_to_embed(embed: discord.Embed, name: str, value: str, inline: bool = False) -> discord.Embed:
    """
    Add a field to an embed with length validation.

    Args:
        embed: The embed to add field to
        name: Field name
        value: Field value
        inline: Whether field should be inline

    Returns:
        Modified embed
    """
    # Discord has limits: field name <= 256 chars, field value <= 1024 chars
    name = name[:256] if len(name) > 256 else name
    value = value[:1024] if len(value) > 1024 else value

    embed.add_field(name=name, value=value, inline=inline)
    return embed


def format_list_for_embed(items: List[str], max_items: int = 10) -> str:
    """
    Format a list of items for embed display.

    Args:
        items: List of strings to format
        max_items: Maximum number of items to display

    Returns:
        Formatted string
    """
    if not items:
        return "No items available."

    display_items = items[:max_items]
    formatted = "\n".join(f"• {item}" for item in display_items)

    if len(items) > max_items:
        formatted += f"\n... and {len(items) - max_items} more"

    return formatted


def get_default_resources() -> List[Resource]:
    """
    Get default learning resources.

    Returns:
        List of default Resource objects
    """
    return [
        Resource(
            title="CS50: Introduction to Computer Science",
            description="Harvard's introductory computer science course",
            url="https://cs50.harvard.edu",
            category="Computer Science",
            difficulty="Beginner",
            tags=["programming", "algorithms", "data structures"]
        ),
        Resource(
            title="The Odin Project",
            description="Free full-stack web development curriculum",
            url="https://www.theodinproject.com",
            category="Web Development",
            difficulty="Beginner",
            tags=["HTML", "CSS", "JavaScript", "Ruby"]
        ),
        Resource(
            title="FreeCodeCamp",
            description="Interactive coding lessons and certifications",
            url="https://www.freecodecamp.org",
            category="Programming",
            difficulty="Beginner",
            tags=["JavaScript", "React", "Node.js", "Python"]
        ),
        Resource(
            title="LeetCode",
            description="Coding interview preparation platform",
            url="https://leetcode.com",
            category="Interview Prep",
            difficulty="Intermediate",
            tags=["algorithms", "data structures", "system design"]
        ),
        Resource(
            title="Cracking the Coding Interview",
            description="Comprehensive guide to technical interviews",
            url="https://www.amazon.com/Cracking-Coding-Interview-Programming-Questions/dp/0984782850",
            category="Interview Prep",
            difficulty="Advanced",
            tags=["algorithms", "system design", "behavioral"]
        )
    ]


def get_default_job_postings() -> List[JobPosting]:
    """
    Get default job postings.

    Returns:
        List of default JobPosting objects
    """
    return [
        JobPosting(
            title="Software Engineering Intern",
            company="Tech Corp",
            description="Summer internship opportunity for computer science students",
            location="Remote",
            url="https://example.com/job1",
            job_type="Internship",
            posted_date=datetime.now()
        ),
        JobPosting(
            title="Full Stack Developer",
            company="StartupXYZ",
            description="Join our fast-growing startup as a full-stack developer",
            location="New York, NY",
            url="https://example.com/job2",
            salary_range="$80,000 - $100,000",
            job_type="Full-time"
        ),
        JobPosting(
            title="Data Science Analyst",
            company="DataTech Inc",
            description="Analyze large datasets and build predictive models",
            location="San Francisco, CA",
            url="https://example.com/job3",
            salary_range="$90,000 - $120,000",
            job_type="Full-time"
        )
    ]


def get_default_interview_questions() -> List[InterviewQuestion]:
    """
    Get default interview questions.

    Returns:
        List of default InterviewQuestion objects
    """
    return [
        InterviewQuestion(
            question="Explain the difference between a stack and a queue.",
            category="Data Structures",
            difficulty="Easy",
            hints=[
                "Think about the order of operations",
                "Consider LIFO vs FIFO"
            ]
        ),
        InterviewQuestion(
            question="What is the time complexity of binary search?",
            category="Algorithms",
            difficulty="Easy",
            hints=[
                "Binary search divides the search space in half each time",
                "Consider the worst case scenario"
            ]
        ),
        InterviewQuestion(
            question="Design a URL shortening service like bit.ly",
            category="System Design",
            difficulty="Hard",
            hints=[
                "Think about scalability and uniqueness",
                "Consider database design and caching"
            ]
        ),
        InterviewQuestion(
            question="Explain the concept of polymorphism in object-oriented programming.",
            category="Object-Oriented Programming",
            difficulty="Medium",
            hints=[
                "Think about different forms of the same method",
                "Consider inheritance and interfaces"
            ]
        )
    ]


def get_default_networking_tips() -> List[NetworkingTip]:
    """
    Get default networking tips.

    Returns:
        List of default NetworkingTip objects
    """
    return [
        NetworkingTip(
            title="Attend Industry Events",
            content="Participate in tech conferences, meetups, and career fairs to connect with professionals in your field.",
            category="Events"
        ),
        NetworkingTip(
            title="Leverage LinkedIn Effectively",
            content="Keep your profile updated, connect with alumni, and engage with industry content regularly.",
            category="Online Presence"
        ),
        NetworkingTip(
            title="Informational Interviews",
            content="Reach out to professionals for 15-30 minute conversations about their career paths and advice.",
            category="Communication"
        ),
        NetworkingTip(
            title="Join Professional Organizations",
            content="Become a member of organizations like ACM, IEEE, or industry-specific groups for networking opportunities.",
            category="Organizations"
        ),
        NetworkingTip(
            title="Follow Up",
            content="Always send a thank-you note after networking interactions to maintain the connection.",
            category="Communication"
        )
    ]


def get_default_skills() -> List[Skill]:
    """
    Get default skills with learning resources.

    Returns:
        List of default Skill objects
    """
    return [
        Skill(
            name="Python Programming",
            description="A versatile programming language used in web development, data science, and automation",
            category="Programming Languages",
            prerequisites=[],
            resources=[
                Resource("Python.org Tutorial", "Official Python tutorial", "https://docs.python.org/3/tutorial/", "Programming", "Beginner"),
                Resource("Automate the Boring Stuff", "Practical Python programming book", "https://automatetheboringstuff.com", "Programming", "Beginner")
            ]
        ),
        Skill(
            name="Data Structures & Algorithms",
            description="Fundamental computer science concepts for efficient problem-solving",
            category="Computer Science",
            prerequisites=["Basic Programming"],
            resources=[
                Resource("GeeksforGeeks DSA", "Comprehensive DSA tutorials", "https://www.geeksforgeeks.org/data-structures/", "CS Fundamentals", "Intermediate"),
                Resource("LeetCode", "Practice coding problems", "https://leetcode.com", "Practice", "Intermediate")
            ]
        ),
        Skill(
            name="Web Development",
            description="Building websites and web applications",
            category="Software Development",
            prerequisites=["HTML", "CSS", "JavaScript"],
            resources=[
                Resource("MDN Web Docs", "Complete web development reference", "https://developer.mozilla.org", "Web Development", "All Levels"),
                Resource("The Odin Project", "Full-stack curriculum", "https://www.theodinproject.com", "Web Development", "Beginner")
            ]
        ),
        Skill(
            name="Machine Learning",
            description="Building AI models and predictive systems",
            category="Artificial Intelligence",
            prerequisites=["Python", "Statistics", "Linear Algebra"],
            resources=[
                Resource("Coursera ML Course", "Andrew Ng's machine learning course", "https://www.coursera.org/learn/machine-learning", "AI/ML", "Intermediate"),
                Resource("Scikit-learn Documentation", "Python ML library", "https://scikit-learn.org", "AI/ML", "Intermediate")
            ]
        )
    ]
