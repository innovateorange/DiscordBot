# bot.py

import discord
from discord.ext import commands
import os
import sys
import logging
from dotenv import load_dotenv
from typing import List, Optional

# Import our custom modules
from config import config
from utils import (
    load_events_from_csv,
    get_upcoming_events,
    create_embed,
    add_field_to_embed,
    format_list_for_embed
)
from models import Event

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up Discord Intents to enable bot to receive message events
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True  # Required to read message content (needed for commands)

# Initialize bot with command prefix from config and specified intents
bot = commands.Bot(command_prefix=config.command_prefix, intents=intents, help_command=None)

# Global variables for data
events_data: List[Event] = []


# prints a message when the bot is ready in the terminal.
@bot.event
async def on_ready():
    """Event: Called when the bot logs in successfully."""
    global events_data

    print(f"✅ Logged in as {bot.user}")
    print(f"🤖 {config.bot_name} is ready to help with career development!")

    # Load events data on startup
    try:
        events_data = load_events_from_csv(str(config.events_csv))
        print(f"📅 Loaded {len(events_data)} events from CSV")
    except Exception as e:
        logger.error(f"Failed to load events data: {e}")
        print("⚠️  Warning: Could not load events data")

    # Validate configuration
    issues = config.validate_config()
    if issues:
        print("⚠️  Configuration issues found:")
        for issue in issues:
            print(f"  - {issue}")


# !help command
@bot.command()
async def help(ctx):
    """Command: Lists all available bot commands."""
    embed = create_embed(
        title=f"🤖 {config.bot_name} - Career Development Assistant",
        description=config.get_help_text(),
        color=0x00ff00
    )

    await ctx.send(embed=embed)


# !resume command
@bot.command()
async def resume(ctx):
    """Command: Sends links to resume resources."""
    embed = create_embed(
        title="📄 Resume Resources",
        description="Build an impressive engineering resume with these resources:",
        color=0x3498db
    )

    add_field_to_embed(embed, "Engineering Resumes Wiki",
                      "[Reddit Engineering Resumes](https://www.reddit.com/r/EngineeringResumes/wiki/index/)\nComprehensive guide to crafting technical resumes", inline=False)

    add_field_to_embed(embed, "Resume Templates",
                      "[Resume.io Templates](https://resume.io/templates)\nProfessional resume templates for engineers", inline=False)

    add_field_to_embed(embed, "Resume Tips",
                      "[ResumeLab](https://resumelab.com)\nATS-friendly resume tips and examples", inline=False)

    await ctx.send(embed=embed)


# !events command
@bot.command()
async def events(ctx, count: Optional[int] = None):
    """Command: Shows upcoming career events."""
    try:
        if not events_data:
            await ctx.send("⚠️ No events data available. Please check the CSV file.")
            return

        limit = count or config.max_events_display
        upcoming_events = get_upcoming_events(events_data, limit)

        if not upcoming_events:
            embed = create_embed(
                title="📅 Upcoming Events",
                description="No upcoming events found. Check back later!",
                color=0xffa500
            )
            await ctx.send(embed=embed)
            return

        embed = create_embed(
            title="📅 Upcoming Career Events",
            description=f"Here are the next {len(upcoming_events)} upcoming events:",
            color=0x9b59b6
        )

        for event in upcoming_events:
            event_text = event.format_for_discord()
            # Truncate if too long for embed field
            if len(event_text) > 1024:
                event_text = event_text[:1021] + "..."

            add_field_to_embed(embed, event.title, event_text, inline=False)

        await ctx.send(embed=embed)

    except Exception as e:
        logger.error(f"Error in events command: {e}")
        await ctx.send("⚠️ Sorry, there was an error retrieving events. Please try again later.")


# !resources command
@bot.command()
async def resources(ctx, category: Optional[str] = None):
    """Command: Shows recommended CS learning resources."""
    try:
        if category:
            resources_list = config.get_resources_by_category(category)
            title = f"📚 {category.title()} Learning Resources"
        else:
            resources_list = config.resources
            title = "📚 CS Learning Resources"

        if not resources_list:
            embed = create_embed(
                title=title,
                description="No resources found for the specified category." if category else "No resources available.",
                color=0xffa500
            )
            await ctx.send(embed=embed)
            return

        embed = create_embed(
            title=title,
            description=f"Here are {len(resources_list)} recommended learning resources:",
            color=0xe74c3c
        )

        for resource in resources_list[:config.max_resources_display]:
            resource_text = resource.format_for_discord()
            if len(resource_text) > 1024:
                resource_text = resource_text[:1021] + "..."
            add_field_to_embed(embed, resource.title, resource_text, inline=False)

        if len(resources_list) > config.max_resources_display:
            embed.set_footer(text=f"Showing {config.max_resources_display} of {len(resources_list)} resources. Use !resources <category> to filter.")

        await ctx.send(embed=embed)

    except Exception as e:
        logger.error(f"Error in resources command: {e}")
        await ctx.send("⚠️ Sorry, there was an error retrieving resources. Please try again later.")


# !interview command
@bot.command()
async def interview(ctx, difficulty: Optional[str] = None):
    """Command: Provides coding interview questions for practice."""
    try:
        import random

        if difficulty:
            difficulty_lower = difficulty.lower()
            filtered_questions = [q for q in config.interview_questions
                                if q.difficulty.lower() == difficulty_lower]
            if not filtered_questions:
                available_difficulties = set(q.difficulty for q in config.interview_questions)
                await ctx.send(f"⚠️ No questions found for difficulty '{difficulty}'. Available difficulties: {', '.join(available_difficulties)}")
                return
            question = random.choice(filtered_questions)
        else:
            question = config.get_random_interview_question()

        embed = create_embed(
            title="💡 Coding Interview Practice",
            description=f"**{question.question}**\n\n📂 Category: {question.category}\n🎯 Difficulty: {question.difficulty}",
            color=0xf39c12
        )

        if question.hints:
            hints_text = "\n".join(f"• {hint}" for hint in question.hints[:3])  # Limit to 3 hints
            add_field_to_embed(embed, "💡 Hints", hints_text, inline=False)

        embed.set_footer(text="Use !interview <difficulty> to get questions of a specific difficulty (Easy/Medium/Hard)")

        await ctx.send(embed=embed)

    except Exception as e:
        logger.error(f"Error in interview command: {e}")
        await ctx.send("⚠️ Sorry, there was an error retrieving interview questions. Please try again later.")


# !jobs command
@bot.command()
async def jobs(ctx, job_type: Optional[str] = None):
    """Command: Shows current job postings and career opportunities."""
    try:
        if job_type:
            jobs_list = config.get_jobs_by_type(job_type)
            title = f"💼 {job_type.title()} Opportunities"
        else:
            jobs_list = config.job_postings
            title = "💼 Job Postings & Opportunities"

        if not jobs_list:
            embed = create_embed(
                title=title,
                description="No job postings found for the specified type." if job_type else "No job postings available.",
                color=0xffa500
            )
            await ctx.send(embed=embed)
            return

        embed = create_embed(
            title=title,
            description=f"Here are {len(jobs_list)} current opportunities:",
            color=0x2ecc71
        )

        for job in jobs_list[:config.max_jobs_display]:
            job_text = job.format_for_discord()
            if len(job_text) > 1024:
                job_text = job_text[:1021] + "..."
            add_field_to_embed(embed, job.title, job_text, inline=False)

        if len(jobs_list) > config.max_jobs_display:
            embed.set_footer(text=f"Showing {config.max_jobs_display} of {len(jobs_list)} jobs. Use !jobs <type> to filter by job type.")

        await ctx.send(embed=embed)

    except Exception as e:
        logger.error(f"Error in jobs command: {e}")
        await ctx.send("⚠️ Sorry, there was an error retrieving job postings. Please try again later.")


# !networking command
@bot.command()
async def networking(ctx, category: Optional[str] = None):
    """Command: Provides networking tips and advice."""
    try:
        import random

        if category:
            category_lower = category.lower()
            filtered_tips = [tip for tip in config.networking_tips
                           if category_lower in tip.category.lower()]
            if not filtered_tips:
                available_categories = set(tip.category for tip in config.networking_tips)
                await ctx.send(f"⚠️ No networking tips found for category '{category}'. Available categories: {', '.join(available_categories)}")
                return
            tip = random.choice(filtered_tips)
        else:
            tip = random.choice(config.networking_tips)

        embed = create_embed(
            title="🤝 Networking Tips",
            description=tip.format_for_discord(),
            color=0x3498db
        )

        embed.set_footer(text="Use !networking <category> to get tips for a specific area (Events/Online Presence/Communication/Organizations)")

        await ctx.send(embed=embed)

    except Exception as e:
        logger.error(f"Error in networking command: {e}")
        await ctx.send("⚠️ Sorry, there was an error retrieving networking tips. Please try again later.")


# !skills command
@bot.command()
async def skills(ctx, skill_name: Optional[str] = None):
    """Command: Shows technical skills and learning paths."""
    try:
        if skill_name:
            skill = config.get_skill_by_name(skill_name)
            if not skill:
                # Show available skills
                available_skills = [s.name for s in config.skills]
                embed = create_embed(
                    title="🔍 Skill Not Found",
                    description=f"Couldn't find a skill named '{skill_name}'. Available skills:",
                    color=0xffa500
                )
                skills_text = format_list_for_embed(available_skills)
                add_field_to_embed(embed, "Available Skills", skills_text, inline=False)
                await ctx.send(embed=embed)
                return

            # Show detailed skill information
            embed = create_embed(
                title=f"🎯 {skill.name}",
                description=skill.format_for_discord(),
                color=0x9b59b6
            )

            if skill.resources:
                resources_text = "\n".join([f"• {r.title} ({r.difficulty})" for r in skill.resources[:5]])
                add_field_to_embed(embed, "📚 Learning Resources", resources_text, inline=False)

            if skill.prerequisites:
                prereqs_text = format_list_for_embed(skill.prerequisites)
                add_field_to_embed(embed, "📋 Prerequisites", prereqs_text, inline=False)

        else:
            # Show all available skills
            embed = create_embed(
                title="🎯 Technical Skills & Learning Paths",
                description=f"Here are {len(config.skills)} technical skills you can learn:",
                color=0x9b59b6
            )

            for skill in config.skills:
                skill_preview = skill.format_for_discord()
                if len(skill_preview) > 500:  # Shorter preview for overview
                    skill_preview = skill_preview[:497] + "..."
                add_field_to_embed(embed, skill.name, skill_preview, inline=False)

            embed.set_footer(text="Use !skills <skill_name> to get detailed information about a specific skill")

        await ctx.send(embed=embed)

    except Exception as e:
        logger.error(f"Error in skills command: {e}")
        await ctx.send("⚠️ Sorry, there was an error retrieving skills information. Please try again later.")


# !mentor command
@bot.command()
async def mentor(ctx):
    """Command: Provides mentoring resources and programs."""
    try:
        embed = create_embed(
            title="👨‍🏫 Mentoring Resources",
            description="Find mentors and get guidance for your career development:",
            color=0x34495e
        )

        add_field_to_embed(embed, "Mentorship Programs",
                          "**Advent Of Code Mentorship**\n[Apply here](https://adventofcode.com/)\nPair programming and career guidance", inline=False)

        add_field_to_embed(embed, "Professional Networks",
                          "**LinkedIn Alumni Network**\nConnect with graduates from your university\nSearch for alumni in your target companies", inline=False)

        add_field_to_embed(embed, "Online Communities",
                          "**Reddit Communities**\n[r/cscareerquestions](https://reddit.com/r/cscareerquestions)\n[r/learnprogramming](https://reddit.com/r/learnprogramming)", inline=False)

        add_field_to_embed(embed, "University Resources",
                          "**Career Center**\nSchedule appointments with career counselors\nAttend office hours for resume and interview prep", inline=False)

        add_field_to_embed(embed, "Tips for Finding a Mentor",
                          "• Attend career fairs and networking events\n• Join professional organizations\n• Reach out to professionals on LinkedIn\n• Be specific about what you want to learn", inline=False)

        await ctx.send(embed=embed)

    except Exception as e:
        logger.error(f"Error in mentor command: {e}")
        await ctx.send("⚠️ Sorry, there was an error retrieving mentoring resources. Please try again later.")


def run_bot():
    """Initialize and run the Discord bot with proper error handling."""
    try:
        # Validate configuration before starting
        issues = config.validate_config()
        if issues:
            print("❌ Configuration validation failed:")
            for issue in issues:
                print(f"  - {issue}")
            print("\nPlease fix these issues before running the bot.")
            sys.exit(1)

        # Load environment variables
        if not load_dotenv():
            print("❌ Failed to load .env file")
            sys.exit(1)

        token = os.getenv("DISCORD_BOT_TOKEN")
        if not token or token.strip() == "":
            print("❌ DISCORD_BOT_TOKEN is not set or empty in .env file")
            sys.exit(1)

        print("🚀 Starting CuseBot...")
        bot.run(token)

    except discord.LoginFailure:
        print("❌ Invalid Discord bot token. Please check your DISCORD_BOT_TOKEN in the .env file.")
        logger.error("Discord login failure - invalid token")
        sys.exit(1)
    except discord.PrivilegedIntentsRequired:
        print("❌ Bot requires privileged intents. Please enable them in the Discord Developer Portal.")
        logger.error("Privileged intents required but not enabled")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️  Bot shutdown requested by user")
        logger.info("Bot shutdown via keyboard interrupt")
    except Exception as e:
        print(f"❌ Unexpected error starting bot: {e}")
        logger.error(f"Unexpected error in run_bot: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_bot()
# to run the bot, run the command: python bot.py in the folder containing the file.
# make sure you have the discord.py library installed.
