import json
from pathlib import Path

import matplotlib.pyplot as plt


class TrendAnalyzer:

    def __init__(self):
        self.history_dir = Path("history")
        self.reports_dir = Path("reports")

        self.reports_dir.mkdir(exist_ok=True)

    def load_history(self):
        runs = []

        files = sorted(
            self.history_dir.glob("run_*.json")
        )

        for file in files:
            try:
                with open(
                    file,
                    "r",
                    encoding="utf-8"
                ) as f:
                    data = json.load(f)

                runs.append(data)

            except Exception as e:
                print(
                    f"Could not load {file}: {e}"
                )

        return runs

    def average_latency(self, results):
        latencies = [
            item["latency"]
            for item in results
            if item.get("latency") is not None
            and item.get("status") != "error"
        ]

        if not latencies:
            return 0

        return round(
            sum(latencies) / len(latencies),
            3
        )

    def create_accuracy_chart(self):
        runs = self.load_history()

        if not runs:
            print("No history found.")
            return None

        labels = []
        accuracies = []

        for index, run in enumerate(runs, start=1):
            labels.append(f"Run {index}")
            accuracies.append(run["accuracy"])

        plt.figure(figsize=(10, 5))

        plt.plot(
            labels,
            accuracies,
            marker="o"
        )

        plt.title("LLM Accuracy Trend")

        plt.xlabel("Evaluation Run")

        plt.ylabel("Accuracy (%)")

        plt.xticks(rotation=45)

        plt.grid(True)

        plt.tight_layout()

        output_path = (
            self.reports_dir /
            "accuracy_trend.png"
        )

        plt.savefig(output_path)

        plt.close()

        print(
            f"Accuracy chart saved: "
            f"{output_path}"
        )

        return output_path

    def create_latency_chart(self):
        runs = self.load_history()

        if not runs:
            print("No history found.")
            return None

        labels = []
        latencies = []

        for index, run in enumerate(runs, start=1):

            average = self.average_latency(
                run.get("results", [])
            )

            labels.append(f"Run {index}")
            latencies.append(average)

        plt.figure(figsize=(10, 5))

        plt.plot(
            labels,
            latencies,
            marker="o"
        )

        plt.title("LLM Average Latency Trend")

        plt.xlabel("Evaluation Run")

        plt.ylabel("Average Latency (seconds)")

        plt.xticks(rotation=45)

        plt.grid(True)

        plt.tight_layout()

        output_path = (
            self.reports_dir /
            "latency_trend.png"
        )

        plt.savefig(output_path)

        plt.close()

        print(
            f"Latency chart saved: "
            f"{output_path}"
        )

        return output_path

    def generate(self):
        accuracy_chart = (
            self.create_accuracy_chart()
        )

        latency_chart = (
            self.create_latency_chart()
        )

        return {
            "accuracy_chart": accuracy_chart,
            "latency_chart": latency_chart,
        }