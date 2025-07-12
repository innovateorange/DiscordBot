# bot.py

import os
import sys

import discord
from discord.ext import commands
from dotenv import load_dotenv
from data_processing.job_event import (
    get_jobs,
    paste_jobs_command,
    format_jobs_message,
    filter_jobs,
)

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
    Handles the event when the bot has successfully connected to Discord
    and is ready to operate.
    """
    print(f"✅ Logged in as {bot.user}")


# Welcome message when a new member joins the server (requires privileged intent)
@bot.event
async def on_member_join(member: discord.Member) -> None:
    """
    Sends a welcome message when a new member joins the server.

    Attempts to post the welcome message in a suitable channel
    (e.g., "welcome", "general", "introductions", or "lobby"),
    falling back to the system channel or the first available
    text channel if necessary. If no appropriate channel is found,
    sends a direct message to the new member. The welcome message
    includes a mention of the "networking" channel if it exists.
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
    welcome_message = f"Welcome to **{member.guild.name}**, {member.mention}! Feel free to introduce yourself in {networking_mention}"  # noqa: E501

    try:
        if welcome_channel:
            await welcome_channel.send(welcome_message)
            print(
                f"📨 Welcome message sent for {member.display_name} in #{welcome_channel.name}"  # noqa: E501
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
            f"❌ Could not send welcome message for {member.display_name} - missing permissions"  # noqa: E501
        )
    except Exception as e:
        print(f"❌ Error sending welcome message for {member.display_name}: {e}")


# !help command placeholder
@bot.command()
async def help(ctx) -> None:
    """
    Sends a message listing all available bot commands and their
    descriptions in the current channel.
    """
    help_message = (
        "**🤖 BugBot Commands:**\n"
        "`!resume` – Link to engineering resume resources\n"
        "`!events` – See upcoming club events\n"
        "`!resources` – Get recommended CS learning materials\n"
        "`!jobs search-terms` – Search for jobs and internships\n\n"
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
    Sends a message listing upcoming club events and their dates in
    response to the `!events` command.
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
    Sends a list of recommended computer science learning resources
    to the channel in response to the `!resources` command.
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

    Usage: !jobs [search_critera]

    Examples:
    - !jobs software engineer
    - !jobs google remote
    - !jobs python internship summer
    - !jobs microsoft internship
    """
    csv_file_path = "data_collections/runningCSV.csv"
    try:
        jobs = get_jobs(csv_file_path)
    except OSError:
        await ctx.send(
            "Sorry, there was an error searching for jobs. Please try again later."
        )
    else:
        filters = paste_jobs_command(args)
        jobs = filter_jobs(jobs, filters)
        message = format_jobs_message(jobs, filters)
        await ctx.send(message)


def run_bot() -> None:
    """
    Loads environment variables, retrieves the Discord bot token,
    and starts the bot.

    Exits the program with an error message if the environment file
    is missing or the token is invalid.
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
        print("environment file was not found")
        sys.exit(1)


if __name__ == "__main__":
    run_bot()
# to run the bot, run the command: python bot.py in the folder containing the file.
# make sure you have the discord.py library installed.
