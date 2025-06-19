import os
import json
import requests

# Load GitHub event payload
with open(os.getenv("GITHUB_EVENT_PATH"), "r") as f:
    event = json.load(f)

# Load GitHub-to-Discord user map
with open("user_map.json", "r") as f:
    user_map = json.load(f)

def post_to_discord(message):
    discord_webhook = os.getenv("DISCORD_WEBHOOK_URL")
    payload = {
        "content": message
    }
    response = requests.post(discord_webhook, json=payload)
    response.raise_for_status()
    
# Handle Assignment to Issues & PRs
if event.get("action") == "assigned":
    assignee = event.get("assignee", {}).get("login")
    issue_title = event.get("issue", {}).get("title")
    issue_url = event.get("issue", {}).get("html_url")
    
    if assignee and issue_title and issue_url:
        message = f"🔔 Assigned to Issue:\n**{issue_title}**\nAssigned to: {assignee}\n{issue_url}"
        post_to_discord(message)

# Handle Comments on Issues & PRs
elif event.get("action") == "created":
    # Check if it's a comment on an issue or PR
    if "comment" in event:
        comment = event.get("comment", {}).get("body")
        issue_title = event.get("issue", {}).get("title")
        issue_url = event.get("issue", {}).get("html_url")
        
        if comment and issue_title and issue_url:
            message = f"🔔 Comment on Issue:\n**{issue_title}**\nComment: {comment}\n{issue_url}"
            post_to_discord(message)
    elif "review" in event:
        # Handle PR review comments
        comment = event.get("review", {}).get("body")
        pr_title = event.get("pull_request", {}).get("title")
        pr_url = event.get("pull_request", {}).get("html_url")
        
        if comment and pr_title and pr_url:
            message = f"🔔 Review Comment on PR:\n**{pr_title}**\nComment: {comment}\n{pr_url}"
            post_to_discord(message)

# Replace GitHub mentions with Discord mentions
def convert_mentions(text):
    for github_user, discord_id in user_map.items():
        text = text.replace(f"@{github_user}", f"<@{discord_id}>")
    return text

message = convert_mentions(comment)
post_to_discord(message)
