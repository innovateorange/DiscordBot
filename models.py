# models.py
# Data models for the Discord bot

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from enum import Enum


class EventType(Enum):
    """Types of events the bot can handle."""
    EVENT = "Event"
    WORKSHOP = "Workshop"
    MEETUP = "Meetup"
    WEBINAR = "Webinar"


@dataclass
class Event:
    """Represents an event with all its details."""
    title: str
    description: str
    start_date: datetime
    end_date: Optional[datetime] = None
    location: str = ""
    link: str = ""
    event_type: EventType = EventType.EVENT
    pub_date: Optional[datetime] = None

    def __post_init__(self):
        """Validate event data after initialization."""
        if self.end_date and self.start_date > self.end_date:
            raise ValueError("Start date cannot be after end date")

    @property
    def is_upcoming(self) -> bool:
        """Check if the event is upcoming (starts in the future)."""
        return self.start_date > datetime.now()

    @property
    def duration_hours(self) -> Optional[float]:
        """Calculate event duration in hours if end_date is provided."""
        if self.end_date:
            duration = self.end_date - self.start_date
            return duration.total_seconds() / 3600
        return None

    def format_for_discord(self) -> str:
        """Format event for Discord message display."""
        date_format = "%A, %B %d, %Y at %I:%M %p %Z"
        start_str = self.start_date.strftime(date_format)

        if self.end_date:
            end_str = self.end_date.strftime(date_format)
            time_info = f"{start_str} - {end_str}"
        else:
            time_info = start_str

        location_info = f" 📍 {self.location}" if self.location else ""
        link_info = f"\n🔗 {self.link}" if self.link else ""

        return f"**{self.title}**\n{self.description}\n🕒 {time_info}{location_info}{link_info}"


@dataclass
class Resource:
    """Represents a learning resource."""
    title: str
    description: str
    url: str
    category: str
    difficulty: str = "Beginner"  # Beginner, Intermediate, Advanced
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []

    def format_for_discord(self) -> str:
        """Format resource for Discord message display."""
        tags_str = f" 🏷️ {', '.join(self.tags)}" if self.tags else ""
        difficulty_emoji = {
            "Beginner": "🟢",
            "Intermediate": "🟡",
            "Advanced": "🔴"
        }.get(self.difficulty, "⚪")

        return f"**{self.title}** {difficulty_emoji}\n{self.description}\n🔗 {self.url}{tags_str}"


@dataclass
class JobPosting:
    """Represents a job posting or career opportunity."""
    title: str
    company: str
    description: str
    location: str
    url: str
    salary_range: Optional[str] = None
    job_type: str = "Full-time"  # Full-time, Part-time, Internship, etc.
    posted_date: Optional[datetime] = None

    def format_for_discord(self) -> str:
        """Format job posting for Discord message display."""
        salary_info = f"\n💰 {self.salary_range}" if self.salary_range else ""
        location_info = f" 📍 {self.location}" if self.location else ""

        return f"**{self.title}** at **{self.company}**\n{self.description}\n🕒 {self.job_type}{location_info}{salary_info}\n🔗 {self.url}"


@dataclass
class InterviewQuestion:
    """Represents an interview question with solution hints."""
    question: str
    category: str
    difficulty: str = "Medium"
    hints: List[str] = None
    solution: Optional[str] = None

    def __post_init__(self):
        if self.hints is None:
            self.hints = []

    def format_for_discord(self) -> str:
        """Format interview question for Discord message display."""
        difficulty_emoji = {
            "Easy": "🟢",
            "Medium": "🟡",
            "Hard": "🔴"
        }.get(self.difficulty, "⚪")

        hints_str = ""
        if self.hints:
            hints_str = "\n💡 **Hints:**\n" + "\n".join(f"• {hint}" for hint in self.hints)

        return f"**{self.question}** {difficulty_emoji}\n📂 {self.category}{hints_str}"


@dataclass
class NetworkingTip:
    """Represents a networking tip or advice."""
    title: str
    content: str
    category: str

    def format_for_discord(self) -> str:
        """Format networking tip for Discord message display."""
        return f"**{self.title}**\n{self.content}\n📂 {self.category}"


@dataclass
class Skill:
    """Represents a technical skill with learning resources."""
    name: str
    description: str
    category: str
    resources: List[Resource] = None
    prerequisites: List[str] = None

    def __post_init__(self):
        if self.resources is None:
            self.resources = []
        if self.prerequisites is None:
            self.prerequisites = []

    def format_for_discord(self) -> str:
        """Format skill for Discord message display."""
        prereqs_str = f"\n📚 **Prerequisites:** {', '.join(self.prerequisites)}" if self.prerequisites else ""
        resources_count = len(self.resources)

        return f"**{self.name}**\n{self.description}\n📂 {self.category}{prereqs_str}\n🔗 {resources_count} learning resources available"
