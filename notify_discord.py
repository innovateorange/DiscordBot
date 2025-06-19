import os
import json
import requests
import re

# Load GitHub context and event payload
event_name = os.getenv("GITHUB_EVENT_NAME")
with open(os.getenv("GITHUB_EVENT_PATH"), "r") as f:
    event = json.load(f)
event_action = event.get("action")

with open(os.getenv("GITHUB_EVENT_PATH"), "r") as f:
    event = json.load(f)

with open("user_map.json", "r") as f:
    user_map = json.load(f)

webhook_url = os.getenv("DISCORD_WEBHOOK_URL")


def post_to_discord(message: str):
    payload = {"content": message}
    response = requests.post(webhook_url, json=payload)
    response.raise_for_status()


def notify_assignment(obj):
    title = obj.get("title", "Untitled")
    url = obj.get("html_url", "")
    assignees = obj.get("assignees", [])

    mentions = [
        f"<@{user_map[user['login']]}>"
        for user in assignees
        if user["login"] in user_map
    ]

    if mentions:
        message = (
            f"📌 **Assignment Notice**\n"
            f"🔗 [{title}]({url})\n"
            f"👤 Assigned to: {', '.join(mentions)}"
        )
        post_to_discord(message)


def notify_comment_mention(comment_body: str, context_obj):
    mentioned_users = re.findall(r"@(\w+)", comment_body)

    mentions = [
        f"<@{user_map[login]}>" for login in mentioned_users if login in user_map
    ]

    if mentions:
        message = (
            f"💬 **Mention in Comment**\n"
            f"🔗 [{context_obj.get('title', 'Untitled')}]({context_obj.get('html_url', '')})\n"
            f"👤 Mentioned: {', '.join(mentions)}\n"
            f'📝 "{comment_body.strip()}"'
        )
        post_to_discord(message)


# === Event dispatch ===

# 1. Valid assignment events
print(f"Event Name: {event_name}, Action: {event_action}")
if event_name == "issues" and event_action in ["opened", "assigned"]:
    notify_assignment(event["issue"])

elif event_name == "pull_request" and event_action in ["opened", "assigned"]:
    notify_assignment(event["pull_request"])

# 2. Valid comment events with possible @mentions
elif (
    event_name in ["issue_comment", "pull_request_review_comment"]
    and "comment" in event
):
    comment_body = event["comment"]["body"]
    context_obj = event.get("issue") or event.get("pull_request", {})
    notify_comment_mention(comment_body, context_obj)

# testing pull requests
