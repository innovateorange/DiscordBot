import os
import json
import requests

# Load GitHub event payload
with open(os.getenv("GITHUB_EVENT_PATH"), "r") as f:
    event = json.load(f)

# Load GitHub-to-Discord user map
with open("user_map.json", "r") as f:
    user_map = json.load(f)

# Extract relevant content (issue comment, PR comment, etc.)
comment = (
    event.get("comment", {}).get("body", "") or
    event.get("review", {}).get("body", "")
)

# Replace GitHub mentions with Discord mentions
def convert_mentions(text):
    for github_user, discord_id in user_map.items():
        text = text.replace(f"@{github_user}", f"<@{discord_id}>")
    return text

message = convert_mentions(comment)

# Send to Discord
discord_webhook = os.getenv("DISCORD_WEBHOOK_URL")
payload = {
    "content": f"🔔 GitHub Mention:\n{message}"
}

response = requests.post(discord_webhook, json=payload)
response.raise_for_status()
