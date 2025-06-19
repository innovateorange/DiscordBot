import os
import json
import requests
import re

# Load GitHub event payload
with open(os.getenv("GITHUB_EVENT_PATH"), "r") as f:
    event = json.load(f)

# Load user map
with open("user_map.json", "r") as f:
    user_map = json.load(f)

webhook = os.getenv("DISCORD_WEBHOOK_URL")

def post_to_discord(message):
    payload = { "content": message }
    response = requests.post(webhook, json=payload)
    response.raise_for_status()

# Handle assignment or issue/PR opened with assignees
if "assignees" in event.get("issue", {}) or "assignees" in event.get("pull_request", {}):
    obj = event.get("issue") or event.get("pull_request")
    title = obj.get("title", "Untitled")
    url = obj.get("html_url", "")
    assignees = obj.get("assignees", [])

    mentions = []
    for user in assignees:
        login = user["login"]
        if login in user_map:
            mentions.append(f"<@{user_map[login]}>")

    if mentions:
        message = (
            f"📌 **Assignment Notice**\n"
            f"🔗 [{title}]({url})\n"
            f"👤 Assigned to: {', '.join(mentions)}"
        )
        post_to_discord(message)

# Handle comment mentions
elif "comment" in event:
    comment = event["comment"]["body"]
    url = event.get("issue", event.get("pull_request", {})).get("html_url", "")
    title = event.get("issue", event.get("pull_request", {})).get("title", "Untitled")

    mentioned_users = re.findall(r"@(\w+)", comment)

    mentions = []
    for login in mentioned_users:
        if login in user_map:
            mentions.append(f"<@{user_map[login]}>")

    if mentions:
        message = (
            f"💬 **Mention in Comment**\n"
            f"🔗 [{title}]({url})\n"
            f"👤 Mentioned: {', '.join(mentions)}\n"
            f"📝 \"{comment}\""
        )
        post_to_discord(message)
