import sys
import unittest
from unittest.mock import MagicMock, mock_open, patch

import notify_discord


class TestNotifyDiscord(unittest.TestCase):

    def setUp(self):
        # Remove the module if it was already imported to ensure clean import
        if "notify_discord" in sys.modules:
            del sys.modules["notify_discord"]

    @patch("requests.post")
    def test_successful_post_to_discord(self, mock_post):
        # Mock successful HTTP response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # Mock environment variables and file operations
        with patch("os.getenv") as mock_getenv, patch(
            "builtins.open", mock_open()
        ) as mock_file:

            def getenv_side_effect(key):
                env_vars = {
                    "GITHUB_EVENT_NAME": "issues",
                    "GITHUB_EVENT_PATH": "event.json",
                    "DISCORD_WEBHOOK_URL": "https://fake.webhook.url",
                }
                return env_vars.get(key)

            mock_getenv.side_effect = getenv_side_effect

            # Mock event.json and user_map.json files
            event_data = '{"action": "opened", "issue": {"title": "Test Issue", "html_url": "https://github.com/test", "assignees": []}}'  # noqa: E501
            user_map_data = '{"user1": "123456789"}'

            mock_file.side_effect = [
                mock_open(read_data=event_data).return_value,
                mock_open(read_data=user_map_data).return_value,
            ]

            # Import the module after mocking
            import notify_discord

            # Test the function
            notify_discord.post_to_discord("Test Message", "https://fake.webhook.url")

            # Verify the request was made
            mock_post.assert_called_once_with(
                "https://fake.webhook.url", json={"content": "Test Message"}
            )

    def test_missing_github_event_name(self):
        # Mock environment variables without event name
        with patch("os.getenv") as mock_getenv:
            mock_getenv.side_effect = lambda k: {
                "GITHUB_EVENT_NAME": None,
                "GITHUB_EVENT_PATH": "dummy_path",
            }.get(k)

            with self.assertRaises(ValueError) as context:
                notify_discord.load_event_context()

            self.assertIn(
                "GITHUB_EVENT_NAME environment variable is not set",
                str(context.exception),
            )

    def test_missing_github_event_path(self):
        # Mock environment variables without event path
        with patch("os.getenv") as mock_getenv:
            mock_getenv.side_effect = lambda k: {
                "GITHUB_EVENT_NAME": "dummy_name",
                "GITHUB_EVENT_PATH": None,
            }.get(k)

            with self.assertRaises(ValueError) as context:
                notify_discord.load_event_context()

            self.assertIn(
                "GITHUB_EVENT_PATH environment variable is not set",
                str(context.exception),
            )

    def test_missing_discord_webhook_url(self):
        # Mock environment variables without webhook URL
        with patch("os.getenv", return_value=None):
            with self.assertRaises(ValueError) as context:
                notify_discord.load_webhook_url()
            self.assertIn(
                "DISCORD_WEBHOOK_URL environment variable is missing or empty.",
                str(context.exception),
            )

    def test_valid_context_load(self):
        mock_event_json = '{"action": "opened", "issue": {"title": "Test Issue"}}'

        with patch("os.getenv") as mock_getenv, patch(
            "builtins.open", mock_open(read_data=mock_event_json)
        ):

            mock_getenv.side_effect = lambda k: {
                "GITHUB_EVENT_NAME": "issues",
                "GITHUB_EVENT_PATH": "event.json",
            }.get(k)

            event_name, action, event = notify_discord.load_event_context()
            self.assertEqual(event_name, "issues")
            self.assertEqual(action, "opened")
            self.assertIn("issue", event)

    def test_generate_developer_list(self):
        assignees = [{"login": "andewmark"}, {"login": "lementknight"}]
        user_map = {"andewmark": 123, "lementknight": 456}
        expected = ["<@123>", "<@456>"]

        result = notify_discord.generate_developer_list(assignees, user_map)
        self.assertEqual(result, expected)

    def test_notify_assignment(self):
        obj = {
            "title": "some_title",
            "html_url": "https://fake.html",
            "assignees": [{"login": "andewmark"}],
        }
        user_map = {"andewmark": 123}
        webhook_url = "https://fake.webhook"

        expected = (
            "📌 **Assignment Notice**\n"
            "🔗 [some_title](https://fake.html)\n"
            "👤 Assigned to: <@123>"
        )
        expected_payload = {"content": expected}

        with patch("notify_discord.requests.post") as mock_post:
            notify_discord.notify_assignment(obj, user_map, webhook_url)

            mock_post.assert_called_once_with(webhook_url, json=expected_payload)

    def test_notify_review_request(self):
        obj = {
            "title": "some_title",
            "html_url": "https://fake.html",
            "requested_reviewers": [{"login": "andewmark"}],
        }
        user_map = {"andewmark": 123}
        webhook_url = "https://fake.webhook"

        expected = (
            "🔍 **Review Requested**\n"
            "🔗 [some_title](https://fake.html)\n"
            "👤 Reviewers: <@123>"
        )
        expected_payload = {"content": expected}

        with patch("notify_discord.requests.post") as mock_post:
            notify_discord.notify_review_request(obj, user_map, webhook_url)

            mock_post.assert_called_once_with(webhook_url, json=expected_payload)

    def test_review_state_change(self):
        obj = {
            "title": "some_title",
            "html_url": "https://fake.html",
            "assignee": {"login": "andewmark"},
        }
        user_map = {"andewmark": 123}
        webhook_url = "https://fake.webhook"
        state = "approved"

        expected = (
            "🔔 **PR Review State Change**\n"
            "🔗 [some_title](https://fake.html)\n"
            "🔄 State: approved\n"
            "👤 Assigned to: <@123>"
        )
        expected_payload = {"content": expected}

        with patch("notify_discord.requests.post") as mock_post:
            notify_discord.notify_review_state_change(obj, state, user_map, webhook_url)

            mock_post.assert_called_once_with(webhook_url, json=expected_payload)

    def test_notify_comment_mention(self):
        comment_body = "Hi @andewmark hello!"
        obj = {"title": "some_title", "html_url": "https://fake.html"}
        user_map = {"andewmark": 123}
        webhook_url = "https://fake.html"

        expected = (
            "💬 **Mention in Comment**\n"
            "🔗 [some_title](https://fake.html)\n"
            "👤 Mentioned: <@123>\n"
            '📝 "Hi @andewmark hello!"'
        )
        expected_payload = {"content": expected}

        with patch("notify_discord.requests.post") as mock_post:
            notify_discord.notify_comment_mention(
                comment_body, obj, user_map, webhook_url
            )

            mock_post.assert_called_once_with(webhook_url, json=expected_payload)

    def test_load_user_map(self):
        user_map_data = '{"user1": "123456789"}'
        with patch("builtins.open", mock_open(read_data=user_map_data)) as mock_file:
            result = notify_discord.load_user_map()
            assert result == {"user1": "123456789"}
            mock_file.assert_called_once_with("user_map.json")

    def test_load_webhook_url(self):
        with patch("os.getenv", return_value="https://fake.webhook"):
            webhook_url = notify_discord.load_webhook_url()
            self.assertEqual("https://fake.webhook", webhook_url)

    def test_missing_webhook_post_to_discord(self):
        with self.assertRaises(ValueError) as context:
            notify_discord.post_to_discord("hello word", webhook_url=None)
        self.assertIn(
            "DISCORD_WEBHOOK_URL environment variable is not set",
            str(context.exception),
        )


if __name__ == "__main__":
    unittest.main()
