import os
import json
import requests
import re


def load_event_context():
    """
    Load the GitHub event name, action, and event payload from environment variables and file.

    Returns:
        tuple: A tuple containing the event name (str), event action (str or None), and the event payload (dict).

    Raises:
        ValueError: If required environment variables are missing.
    """
    event_name = os.getenv("GITHUB_EVENT_NAME")
    if not event_name:
        raise ValueError("GITHUB_EVENT_NAME environment variable is not set")

    event_path = os.getenv("GITHUB_EVENT_PATH")
    if not event_path:
        raise ValueError("GITHUB_EVENT_PATH environment variable is not set")

    with open(event_path, "r") as f:
        event = json.load(f)

    return event_name, event.get("action"), event


def load_user_map():
    """
    Load the mapping of GitHub usernames to Discord user IDs from the 'user_map.json' file.

    Returns:
        dict: A dictionary mapping GitHub usernames to Discord user IDs.
    """
    with open("user_map.json", "r") as f:
        user_map = json.load(f)

        return user_map


def load_webhook_url():
    """
    Retrieve the Discord webhook URL from the environment variable.

    Returns:
        str: The Discord webhook URL.

    Raises:
        ValueError: If the DISCORD_WEBHOOK_URL environment variable is missing or empty.
    """
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        raise ValueError(
            "DISCORD_WEBHOOK_URL environment variable is missing or empty."
        )

    return webhook_url


def post_to_discord(message: str, webhook_url: str):
    """
    Send a message to a Discord channel using the specified webhook URL.

    Raises:
        ValueError: If the webhook URL is not provided.
        HTTPError: If the POST request to Discord fails.
    """
    if not webhook_url:
        raise ValueError("DISCORD_WEBHOOK_URL environment variable is not set")
    payload = {"content": message}
    response = requests.post(webhook_url, json=payload)
    response.raise_for_status()


def generate_developer_list(assignees, user_map):
    """
    Convert a list of GitHub user objects to Discord mention strings using a user mapping.

    Parameters:
        assignees (list): List of GitHub user objects, each containing a 'login' key.
        user_map (dict): Mapping of GitHub usernames to Discord user IDs.

    Returns:
        list: List of Discord mention strings for users found in the user map.
    """
    return [
        f"<@{user_map[user['login']]}>"
        for user in assignees
        if user["login"] in user_map
    ]


def notify_assignment(obj, user_map, webhook_url):
    """
    Sends a Discord notification when an issue or pull request is assigned to one or more users.

    The notification includes the title, URL, and Discord mentions of the assigned users if they are present in the user map.
    """
    title = obj.get("title", "Untitled")
    url = obj.get("html_url", "")
    assignees = obj.get("assignees", [])

    mentions = generate_developer_list(assignees, user_map)

    if mentions:
        message = (
            f"📌 **Assignment Notice**\n"
            f"🔗 [{title}]({url})\n"
            f"👤 Assigned to: {', '.join(mentions)}"
        )
        post_to_discord(message, webhook_url)


def notify_review_request(pr_obj, user_map, webhook_url):
    """
    Sends a Discord notification when a pull request review is requested.

    The notification includes the pull request title, URL, and mentions the requested reviewers if they are mapped to Discord users.
    """
    title = pr_obj.get("title", "Untitled")
    url = pr_obj.get("html_url", "")
    reviewers = pr_obj.get("requested_reviewers", [])

    mentions = generate_developer_list(reviewers, user_map)
    if mentions:
        message = (
            f"🔍 **Review Requested**\n"
            f"🔗 [{title}]({url})\n"
            f"👤 Reviewers: {', '.join(mentions)}"
        )
        post_to_discord(message, webhook_url)


def notify_review_state_change(pr_obj, state: str, user_map, webhook_url):
    """
    Sends a Discord notification about a pull request review state change, mentioning the assigned user.

    Parameters:
        pr_obj (dict): The pull request object containing details such as title, URL, and assignee.
        state (str): The new review state (e.g., "approved", "changes_requested").
        user_map (dict): Mapping of GitHub usernames to Discord user IDs.
        webhook_url (str): The Discord webhook URL for posting the notification.
    """
    title = pr_obj.get("title", "Untitled")
    url = pr_obj.get("html_url", "")
    assignee = pr_obj.get("assignee", {})

    # Skip notification if there’s no valid assignee or the login isn’t in our map
    if not assignee or assignee.get("login") not in user_map:
        return

    mentioned_assignee = f"<@{user_map[assignee['login']]}>"

    message = (
        f"🔔 **PR Review State Change**\n"
        f"🔗 [{title}]({url})\n"
        f"🔄 State: {state}\n"
        f"👤 Assigned to: {mentioned_assignee}"
    )
    post_to_discord(message, webhook_url)


def notify_comment_mention(comment_body: str, context_obj, user_map, webhook_url):
    """
    Detects GitHub username mentions in a comment and sends a Discord notification for users found in the user map.

    Parameters:
        comment_body (str): The text of the comment to scan for @mentions.
        context_obj: The issue or pull request object providing context for the comment.

    Sends a formatted message to Discord mentioning the corresponding users if any GitHub usernames in the comment match entries in the user map.
    """
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
        post_to_discord(message, webhook_url)


def main():
    """
    Handles GitHub webhook events and sends corresponding notifications to Discord.
    Determines the event type and action, loads configuration and user mapping, and dispatches notifications for issue assignments, pull request review requests, pull request review state changes, and user mentions in comments.

    """
    event_name, event_action, event = load_event_context()
    user_map = load_user_map()
    webhook_url = load_webhook_url()

    # === Event dispatch ===

    print(f"Event Name: {event_name}, Action: {event_action}")
    # 1. Valid assignment events
    if event_name == "issues" and event_action in ["opened", "assigned"]:
        notify_assignment(event["issue"], user_map, webhook_url)

    # 2. Valid review request events
    elif event_name == "pull_request" and event_action in ["review_requested"]:
        notify_review_request(event["pull_request"], user_map, webhook_url)

    # 3. Valid request review events
    elif event_name == "pull_request_review" and event_action in ["submitted"]:
        state = event["review"].get("state")
        print(f"Review state: {state}")
        if state == "approved":
            notify_review_state_change(
                event["pull_request"], "approved", user_map, webhook_url
            )
        elif state == "changes_requested":
            notify_review_state_change(
                event["pull_request"], "changes requested", user_map, webhook_url
            )

    # 4. Valid comment events with possible @mentions
    elif (
        event_name in ["issue_comment", "pull_request_review_comment"]
        and "comment" in event
    ):
        comment_body = event["comment"]["body"]
        context_obj = event.get("issue") or event.get("pull_request", {})
        notify_comment_mention(comment_body, context_obj, user_map, webhook_url)


if __name__ == "__main__":
    main()
