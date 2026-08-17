import requests

from app.config import SLACK_WEBHOOK_URL


class SlackNotifier:
    def __init__(self):
        self.webhook_url = SLACK_WEBHOOK_URL

    def send(self, comparison, prompt_version, model):
        message = (
            "🤖 LLM Regression Detector\n\n"
            f"Model: {model}\n"
            f"Prompt Version: {prompt_version}\n"
            f"Previous Accuracy: {comparison.get('previous_accuracy')}\n"
            f"Current Accuracy: {comparison.get('current_accuracy')}\n"
            f"Delta: {comparison.get('delta')}%\n"
            f"Status: {comparison.get('status')}"
        )

        if not self.webhook_url:
            print("Slack webhook is not configured.")
            return

        try:
            response = requests.post(
                self.webhook_url,
                json={"text": message},
                timeout=30
            )

            print("Slack HTTP status:", response.status_code)
            print("Slack response:", response.text)

        except requests.exceptions.RequestException as e:
            print(f"Slack notification failed: {e}")