# config.py
# Configuration management for the Discord bot

import os
from pathlib import Path
from typing import Dict, Any, List
from models import Resource, JobPosting, InterviewQuestion, NetworkingTip, Skill
from utils import (
    get_default_resources,
    get_default_job_postings,
    get_default_interview_questions,
    get_default_networking_tips,
    get_default_skills
)


class BotConfig:
    """Configuration class for the Discord bot."""

    def __init__(self):
        # Bot settings
        self.bot_token = os.getenv("DISCORD_BOT_TOKEN", "")
        self.command_prefix = "!"

        # File paths
        self.data_dir = Path("data-collections")
        self.events_csv = self.data_dir / "dummy_events.csv"

        # Bot appearance
        self.bot_name = "CuseBot"
        self.bot_description = "Career Development Assistant for Students"

        # Command settings
        self.max_events_display = 5
        self.max_resources_display = 10
        self.max_jobs_display = 5
        self.max_questions_display = 3

        # Initialize data
        self._resources = None
        self._job_postings = None
        self._interview_questions = None
        self._networking_tips = None
        self._skills = None

    @property
    def resources(self) -> List[Resource]:
        """Get learning resources."""
        if self._resources is None:
            self._resources = get_default_resources()
        return self._resources

    @property
    def job_postings(self) -> List[JobPosting]:
        """Get job postings."""
        if self._job_postings is None:
            self._job_postings = get_default_job_postings()
        return self._job_postings

    @property
    def interview_questions(self) -> List[InterviewQuestion]:
        """Get interview questions."""
        if self._interview_questions is None:
            self._interview_questions = get_default_interview_questions()
        return self._interview_questions

    @property
    def networking_tips(self) -> List[NetworkingTip]:
        """Get networking tips."""
        if self._networking_tips is None:
            self._networking_tips = get_default_networking_tips()
        return self._networking_tips

    @property
    def skills(self) -> List[Skill]:
        """Get skills."""
        if self._skills is None:
            self._skills = get_default_skills()
        return self._skills

    def get_help_text(self) -> str:
        """Generate help text for all commands."""
        return f"""**🤖 {self.bot_name} Commands:**

`{self.command_prefix}help` – Show this help message
`{self.command_prefix}resume` – Link to engineering resume resources
`{self.command_prefix}events` – See upcoming career events
`{self.command_prefix}resources` – Get recommended CS learning materials
`{self.command_prefix}interview` – Practice coding interview questions
`{self.command_prefix}jobs` – View current job postings and opportunities
`{self.command_prefix}networking` – Get networking tips and advice
`{self.command_prefix}skills` – Explore technical skills and learning paths
`{self.command_prefix}mentor` – Find mentoring resources and programs

**Tip:** Use `{self.command_prefix}skills <skill_name>` to get details about a specific skill!"""

    def validate_config(self) -> List[str]:
        """Validate configuration and return list of issues."""
        issues = []

        if not self.bot_token:
            issues.append("DISCORD_BOT_TOKEN environment variable not set")

        if not self.events_csv.exists():
            issues.append(f"Events CSV file not found: {self.events_csv}")

        if not self.data_dir.exists():
            issues.append(f"Data directory not found: {self.data_dir}")

        return issues

    def get_random_interview_question(self) -> InterviewQuestion:
        """Get a random interview question."""
        import random
        return random.choice(self.interview_questions)

    def get_skill_by_name(self, skill_name: str) -> Skill:
        """Get a skill by name (case-insensitive)."""
        skill_name_lower = skill_name.lower()
        for skill in self.skills:
            if skill.name.lower() == skill_name_lower:
                return skill
        return None

    def search_resources(self, query: str, category: str = None) -> List[Resource]:
        """Search resources by query and optional category."""
        query_lower = query.lower()
        results = []

        for resource in self.resources:
            if query_lower in resource.title.lower() or query_lower in resource.description.lower():
                if category and category.lower() not in resource.category.lower():
                    continue
                results.append(resource)

        return results

    def get_resources_by_category(self, category: str) -> List[Resource]:
        """Get resources filtered by category."""
        category_lower = category.lower()
        return [r for r in self.resources if category_lower in r.category.lower()]

    def get_jobs_by_type(self, job_type: str) -> List[JobPosting]:
        """Get job postings filtered by type."""
        job_type_lower = job_type.lower()
        return [j for j in self.job_postings if job_type_lower in j.job_type.lower()]


# Global configuration instance
config = BotConfig()
