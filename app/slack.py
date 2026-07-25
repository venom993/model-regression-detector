import requests

from app.config import SLACK_WEBHOOK_URL


class SlackNotifier:

    def send(
        self,
        comparison,
        prompt_version,
        model,
    ):

        if not SLACK_WEBHOOK_URL:
            print("Slack webhook not configured.")
            return

        message = f"""
*Model Regression Report*

Model: {model}

Prompt Version: {prompt_version}

Previous Accuracy:
{comparison["previous_accuracy"]}%

Current Accuracy:
{comparison["current_accuracy"]}%

Delta:
{comparison["delta"]}%

Status:
{comparison["status"]}

Regressions:
{len(comparison["regressions"])}

Improvements:
{len(comparison["improvements"])}
"""

        requests.post(

            SLACK_WEBHOOK_URL,

            json={
                "text": message
            }

        )

        print("Slack notification sent.")