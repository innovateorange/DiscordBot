# bot.py

import discord
from discord.ext import commands
import os
import sys
import re
from typing import List, Dict, Optional, Any
from dotenv import load_dotenv

# Set up Discord Intents to enable bot to receive message events
intents: discord.Intents = discord.Intents.default()
intents.messages = True
intents.message_content = True  # Required to read message content (needed for commands)
intents.members = True  # Privileged intent

# Initialize bot with command prefix '!' and specified intents
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)


# prints a message when the bot is ready in the terminal.
@bot.event
async def on_ready():
    """
    Handles the event when the bot has successfully connected to Discord and is ready to operate.
    """
    print(f"✅ Logged in as {bot.user}")


# Welcome message when a new member joins the server (requires privileged intent)
@bot.event
async def on_member_join(member: discord.Member) -> None:
    """
    Sends a welcome message when a new member joins the server.

    Attempts to post the welcome message in a suitable channel (e.g., "welcome", "general", "introductions", or "lobby"), falling back to the system channel or the first available text channel if necessary. If no appropriate channel is found, sends a direct message to the new member. The welcome message includes a mention of the "networking" channel if it exists.
    """
    # Try to find a welcome channel (common names: welcome, general, etc.)
    welcome_channel: discord.TextChannel | None = None

    # Look for common welcome channel names
    for channel in member.guild.text_channels:
        if channel.name.lower() in ["welcome", "general", "introductions", "lobby"]:
            welcome_channel = channel
            break

    # If no specific welcome channel found, use the first available text channel
    if not welcome_channel:
        if member.guild.system_channel:
            welcome_channel = member.guild.system_channel
        elif member.guild.text_channels:
            welcome_channel = member.guild.text_channels[0]

    # Find networking channel for clickable link
    networking_channel: discord.TextChannel | None = None
    for channel in member.guild.text_channels:
        if channel.name.lower() == "networking":
            networking_channel = channel
            break

    # Create networking channel mention or fallback text
    networking_mention = (
        f"<#{networking_channel.id}>" if networking_channel else "#networking"
    )

    # Create welcome message
    welcome_message = f"Welcome to **{member.guild.name}**, {member.mention}! Feel free to introduce yourself in {networking_mention}"

    try:
        if welcome_channel:
            await welcome_channel.send(welcome_message)
            print(
                f"📨 Welcome message sent for {member.display_name} in #{welcome_channel.name}"
            )
        else:
            # Fallback: send a DM if no suitable channel is found
            await member.send(
                f"🎉 Welcome to **{member.guild.name}**!\n\n"
                f"I'm BugBot! Type `!help` in any channel to see what I can do. 🤖"
            )
            print(f"📨 Welcome DM sent to {member.display_name}")
    except discord.Forbidden:
        # Bot doesn't have permissions to send messages in the channel or to the user
        print(
            f"❌ Could not send welcome message for {member.display_name} - missing permissions"
        )
    except Exception as e:
        print(f"❌ Error sending welcome message for {member.display_name}: {e}")


# !help command placeholder
@bot.command()
async def help(ctx) -> None:
    """
    Sends a message listing all available bot commands and their descriptions in the current channel.
    """
    help_message = (
        "**🤖 BugBot Commands:**\n"
        "`!resume` – Link to engineering resume resources\n"
        "`!events` – See upcoming club events\n"
        "`!resources` – Get recommended CS learning materials\n"
        "`!jobs` – Search for jobs and internships\n"
    )
    await ctx.send(help_message)


# !resume command placeholder
@bot.command()
async def resume(ctx) -> None:
    """
    Sends a link to engineering resume resources in response to the !resume command.
    """
    await ctx.send(
        "📄 Resume Resources: https://www.reddit.com/r/EngineeringResumes/wiki/index/"
    )


# !events command placeholder
@bot.command()
async def events(ctx) -> None:
    """
    Sends a message listing upcoming club events and their dates in response to the `!events` command.
    """
    await ctx.send(
        "📅 Upcoming Events:\n"
        "- April 12: Git Workshop\n"
        "- April 19: LeetCode Challenge Night\n"
        "- April 26: Final Meeting + Pizza 🍕"
    )


# !resources command placeholder
@bot.command()
async def resources(ctx) -> None:
    """
    Sends a list of recommended computer science learning resources to the channel in response to the `!resources` command.
    """
    await ctx.send(
        "📚 CS Learning Resources:\n"
        "- [CS50](https://cs50.harvard.edu)\n"
        "- [The Odin Project](https://www.theodinproject.com/)\n"
        "- [FreeCodeCamp](https://www.freecodecamp.org/)\n"
        "- [LeetCode](https://leetcode.com/)"
    )


@bot.command()
async def jobs(ctx, *, args: str = "") -> None:
    """
    Searches for jobs and internships based on specified criteria.
    Usage: !jobs [role] [type] [season] [company] [location]
    Leave brackets empty [] to ignore that filter.
    
    Examples:
    - !jobs [Software Developer] [internship] [Summer 2025] [] []
    - !jobs [] [internship] [] [Google] []
    - !jobs [] [] [] [] [New York]
    """

    def parse_jobs_command(command_args: str) -> Dict[str, Optional[str]]:
        """
        Parses the jobs command arguments and extracts filter parameters.
        
        Args:
            command_args (str): The arguments string with format: [role] [type] [season] [company] [location]
        
        Returns:
            dict: Dictionary containing parsed parameters
        """
        # Parse parameters in brackets
        params = re.findall(r'\[([^\]]*)\]', command_args)

        # Map to expected parameters
        param_names = ['role', 'type', 'season', 'company', 'location']
        parsed_params = {}
        
        for i, name in enumerate(param_names):
            if i < len(params) and params[i].strip():
                parsed_params[name] = params[i].strip()
            else:
                parsed_params[name] = None
        
        return parsed_params

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

    def getJobs(csv_file_path: str, command_args: str = None) -> List[Dict[str, Any]]:
        """
        Reads job data from CSV file and optionally filters based on command parameters.

        CSV columns: -- From internships.py
            - Type: The type of the entry (always "Internship").
            - Title: The company name.
            - Description: The role/position description.
            - whenDate: The date and time of the internship (left blank).
            - pubDate: The date posted.
            - Location: The location of the internship.
            - link: The link to the application.
            - entryDate: Date that the entry entered our `runningCSV.csv`

        Args:
            csv_file_path (str): Path to the CSV file containing job data
            command_args (str, optional): Command arguments for filtering

        Returns:
            list: List of job dictionaries matching the criteria
        """
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                jobs = []
                
                if not lines:
                    return []
                
                # Parse header row
                header = lines[0].strip().split(',')
                
                # Parse data rows
                for line in lines[1:]:
                    if not line.strip():
                        continue
                    
                    # Simple CSV parsing - split by comma and strip whitespace
                    values = [val.strip().strip('"') for val in line.split(',')]
                    
                    # Create row dictionary
                    row = {}
                    for i, col in enumerate(header):
                        row[col.strip().strip('"')] = values[i] if i < len(values) else ""
                    
                    # Create job dictionary - enhanced structure
                    job = {
                        "Type": row.get("Type", "Job"),
                        "Title": row.get("Title", ""),
                        "Description": row.get("Description", ""),
                        "Company": row.get("Company", row.get("Title", "")),  # Fallback to Title if Company not available
                        "Location": row.get("Location", ""),
                        "whenDate": row.get("whenDate", ""),
                        "pubDate": row.get("pubDate", ""),
                        "link": row.get("link", ""),
                        "entryDate": row.get("entryDate", "")
                    }
                    
                    # Only add jobs with meaningful data
                    if job["Title"] or job["Description"]:
                        jobs.append(job)
                
        except FileNotFoundError:
            print(f"CSV file not found: {csv_file_path}")
            return []
        except Exception as e:
            print(f"Error reading CSV file {csv_file_path}: {e}")
            return []
        
        # If command arguments are provided, filter the jobs
        if command_args and command_args.strip():
            try:
                filters = parse_jobs_command(command_args)
                jobs = filter_jobs(jobs, filters)
            except Exception as e:
                print(f"Error parsing command arguments '{command_args}': {e}")
        
        return jobs

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
            job_text += f"🏢 {company}"
            
            if location:
                job_text += f" • 📍 {location}"
            
            job_text += "\n"
            
            # Add date information if available
            if when_date:
                job_text += f"📅 {when_date}\n"
            elif pub_date:
                job_text += f"📅 Posted: {pub_date}\n"
            
            if link:
                job_text += f"🔗 [Apply Here]({link})\n"
            
            message += job_text + "\n"
        
        if len(jobs) > 10:
            message += f"... and {len(jobs) - 10} more jobs. Use more specific filters to narrow results."
        
        return message
    
    # Path to your CSV file
    csv_file_path = "runningCSV.csv"
    
    try:
        # Get jobs from CSV
        job_results = getJobs(csv_file_path, args)
        
        # Parse filters for message formatting
        filters = parse_jobs_command(args) if args.strip() else {}
        
        # Format and send the message
        message = format_jobs_message(job_results, filters)
        await ctx.send(message)
        
        # Log the command usage
        print(f"📋 Jobs command used by {ctx.author.display_name} with args: '{args}'")
        
    except Exception as e:
        await ctx.send("❌ Sorry, there was an error searching for jobs. Please try again later.")
        print(f"❌ Error in jobs command: {e}")


def run_bot() -> None:
    """
    Loads environment variables, retrieves the Discord bot token, and starts the bot.

    Exits the program with an error message if the environment file is missing or the token is invalid.
    """
    if load_dotenv():
        token = os.getenv("DISCORD_BOT_TOKEN")
        assert token, "DISCORD_BOT_TOKEN can not be empty or None"
        try:
            bot.run(token)
        except discord.LoginFailure:
            print("Invalid token provided. Please check your .env file.")
            sys.exit(1)
    else:
        print("environment file does not found")
        sys.exit(1)


if __name__ == "__main__":
    run_bot()
# to run the bot, run the command: python bot.py in the folder containing the file.
# make sure you have the discord.py library installed.
