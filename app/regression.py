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

    def calculate_average_latency(self, results):

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

    def calculate_average_similarity(self, results):

        similarities = [
            item["summary_similarity"]
            for item in results
            if item.get("summary_similarity") is not None
            and item.get("status") != "error"
        ]

        if not similarities:
            return 0

        return round(
            sum(similarities) / len(similarities),
            3
        )

    def compare(
        self,
        current_results,
        current_accuracy,
        reference=None,
        baseline_name=None,
    ):

        # Use the provided baseline/reference.
        if reference is not None:
            previous = reference

        # Otherwise use the previous evaluation.
        else:
            previous = self.previous_run()

        current_average_latency = (
            self.calculate_average_latency(
                current_results
            )
        )

        current_average_similarity = (
            self.calculate_average_similarity(
                current_results
            )
        )

        # ============================
        # FIRST RUN
        # ============================

        if previous is None:

            return {
                "status": "FIRST_RUN",
                "baseline_name": baseline_name,

                "previous_accuracy": None,
                "current_accuracy": current_accuracy,
                "delta": 0,

                "previous_average_latency": None,
                "current_average_latency":
                    current_average_latency,
                "latency_delta": 0,
                "latency_status": "FIRST_RUN",

                "previous_average_similarity": None,
                "current_average_similarity":
                    current_average_similarity,
                "similarity_delta": 0,
                "similarity_status": "FIRST_RUN",

                "regressions": [],
                "improvements": [],
            }

        # ============================
        # ACCURACY COMPARISON
        # ============================

        previous_accuracy = previous["accuracy"]

        delta = round(
            current_accuracy - previous_accuracy,
            2
        )

        # ============================
        # LATENCY COMPARISON
        # ============================

        previous_average_latency = (
            self.calculate_average_latency(
                previous["results"]
            )
        )

        if previous_average_latency > 0:

            latency_delta = round(
                (
                    current_average_latency
                    - previous_average_latency
                )
                / previous_average_latency
                * 100,
                2
            )

        else:
            latency_delta = 0

        # ============================
        # SEMANTIC SIMILARITY
        # ============================

        previous_average_similarity = (
            self.calculate_average_similarity(
                previous["results"]
            )
        )

        if previous_average_similarity > 0:

            similarity_delta = round(
                (
                    current_average_similarity
                    - previous_average_similarity
                )
                / previous_average_similarity
                * 100,
                2
            )

        else:
            similarity_delta = 0

        # ============================
        # ACCURACY STATUS
        # ============================

        if delta <= -8:
            level = "CRITICAL"

        elif delta <= -3:
            level = "WARNING"

        else:
            level = "PASS"

        # ============================
        # LATENCY STATUS
        # ============================

        if latency_delta >= 50:
            latency_status = "CRITICAL"

        elif latency_delta >= 20:
            latency_status = "WARNING"

        else:
            latency_status = "PASS"

        # ============================
        # SIMILARITY STATUS
        # ============================

        if similarity_delta <= -15:
            similarity_status = "CRITICAL"

        elif similarity_delta <= -7:
            similarity_status = "WARNING"

        else:
            similarity_status = "PASS"

        # ============================
        # CASE REGRESSIONS
        # ============================

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

            previous_item = previous_results.get(
                item["id"]
            )

            if previous_item is None:
                continue

            old_pass = (
                previous_item["status"] == "passed"
            )

            new_pass = (
                item["status"] == "passed"
            )

            if old_pass and not new_pass:
                regressions.append(item)

            elif not old_pass and new_pass:
                improvements.append(item)

        # ============================
        # FINAL COMPARISON RESULT
        # ============================

        return {
            "baseline_name": baseline_name,

            "previous_accuracy": previous_accuracy,
            "current_accuracy": current_accuracy,
            "delta": delta,
            "status": level,

            "previous_average_latency":
                previous_average_latency,

            "current_average_latency":
                current_average_latency,

            "latency_delta":
                latency_delta,

            "latency_status":
                latency_status,

            "previous_average_similarity":
                previous_average_similarity,

            "current_average_similarity":
                current_average_similarity,

            "similarity_delta":
                similarity_delta,

            "similarity_status":
                similarity_status,

            "regressions": regressions,
            "improvements": improvements,
        }