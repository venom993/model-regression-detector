import requests

from app.config import SLACK_WEBHOOK_URL


class SlackNotifier:

    def __init__(self):
        self.webhook_url = SLACK_WEBHOOK_URL


    def send(self, comparison, prompt_version, model):

        message = (
            "🤖 LLM Regression Detector\n\n"

            f"*Model:* {model}\n"
            f"*Prompt Version:* {prompt_version}\n\n"

            "📊 *Accuracy Regression*\n"
            f"Previous Accuracy: "
            f"{comparison.get('previous_accuracy', 'N/A')}%\n"

            f"Current Accuracy: "
            f"{comparison.get('current_accuracy', 'N/A')}%\n"

            f"Delta: "
            f"{comparison.get('delta', 'N/A')}%\n"

            f"Status: "
            f"*{comparison.get('status', 'N/A')}*\n\n"

            "⚡ *Performance Regression*\n"
            f"Previous Avg Latency: "
            f"{comparison.get('previous_average_latency', 'N/A')} seconds\n"

            f"Current Avg Latency: "
            f"{comparison.get('current_average_latency', 'N/A')} seconds\n"

            f"Latency Delta: "
            f"{comparison.get('latency_delta', 'N/A')}%\n"

            f"Status: "
            f"*{comparison.get('latency_status', 'N/A')}*\n\n"

            "🧠 *Semantic Similarity Regression*\n"
            f"Previous Avg Similarity: "
            f"{comparison.get('previous_average_similarity', 'N/A')}\n"

            f"Current Avg Similarity: "
            f"{comparison.get('current_average_similarity', 'N/A')}\n"

            f"Similarity Delta: "
            f"{comparison.get('similarity_delta', 'N/A')}%\n"

            f"Status: "
            f"*{comparison.get('similarity_status', 'N/A')}*\n\n"
            "🧪 *DeepEval Relevancy*\n"

            f"Previous Avg Relevancy: "
            f"{comparison.get('previous_average_deepeval_relevancy', 'N/A')}\n"

            f"Current Avg Relevancy: "
            f"{comparison.get('current_average_deepeval_relevancy', 'N/A')}\n"

            f"DeepEval Delta: "
            f"{comparison.get('deepeval_delta', 'N/A')}%\n"

            f"Status: "
            f"*{comparison.get('deepeval_status', 'N/A')}*\n\n"
            "🔄 *Case Changes*\n"
            f"🔴 Regressions: "
            f"{len(comparison.get('regressions', []))}\n"

            f"🟢 Improvements: "
            f"{len(comparison.get('improvements', []))}"
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

            print(
                "Slack HTTP status:",
                response.status_code
            )

            print(
                "Slack response:",
                response.text
            )

        except requests.exceptions.RequestException as e:

            print(
                f"Slack notification failed: {e}"
            )