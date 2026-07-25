import json
from pathlib import Path


class RegressionDetector:

    def __init__(self):
        self.history_dir = Path("history")

    def _history_files(self):
        return sorted(
            self.history_dir.glob("run_*.json")
        )

    def previous_run(self):
        files = self._history_files()

        if len(files) < 2:
            return None

        with open(files[-2], encoding="utf-8") as f:
            return json.load(f)

    def compare(self, current_results, current_accuracy):

        previous = self.previous_run()

        if previous is None:
            return {
                "status": "FIRST_RUN"
            }

        previous_accuracy = previous["accuracy"]

        delta = round(
            current_accuracy - previous_accuracy,
            2
        )

        previous_results = {
            item["id"]: item
            for item in previous["results"]
            if item.get("status") != "error"
        }

        regressions = []
        improvements = []

        for item in current_results:

            if item.get("status") == "error":
                continue

            previous_item = previous_results.get(item["id"])

            if previous_item is None:
                continue

            old_pass = previous_item["status"] == "passed"
            new_pass = item["status"] == "passed"

            if old_pass and not new_pass:
                regressions.append(item)

            elif not old_pass and new_pass:
                improvements.append(item)

        if delta <= -8:
            level = "CRITICAL"
        elif delta <= -3:
            level = "WARNING"
        else:
            level = "PASS"

        return {
            "previous_accuracy": previous_accuracy,
            "current_accuracy": current_accuracy,
            "delta": delta,
            "status": level,
            "regressions": regressions,
            "improvements": improvements,
        }