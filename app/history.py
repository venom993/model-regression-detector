import json
from pathlib import Path
from datetime import datetime


class HistoryManager:

    def __init__(self):
        self.history_dir = Path("history")
        self.history_dir.mkdir(exist_ok=True)

        self.baseline_dir = Path("baselines")
        self.baseline_dir.mkdir(exist_ok=True)

    def save_run(
        self,
        prompt_version,
        model,
        accuracy,
        category_breakdown,
        results,
        average_deepeval_relevancy=None,
    ):

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S_%f"
        )

        filename = self.history_dir / f"run_{timestamp}.json"

        data = {
            "timestamp": timestamp,
            "prompt_version": prompt_version,
            "model": model,
            "accuracy": accuracy,
            "category_breakdown": category_breakdown,
            "results": results,
            "average_deepeval_relevancy": average_deepeval_relevancy,
        }

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(
                data,
                f,
                indent=2,
                ensure_ascii=False,
            )

        return filename

    def get_history(self):

        history = []

        files = sorted(
            self.history_dir.glob("run_*.json")
        )

        for file in files:

            with open(file, encoding="utf-8") as f:
                history.append(json.load(f))

        return history

    # ==========================================
    # BASELINE MANAGEMENT
    # ==========================================

    def save_baseline(
        self,
        name,
        prompt_version,
        model,
        accuracy,
        category_breakdown,
        results,
        average_deepeval_relevancy=None
    ):

        filename = self.baseline_dir / f"{name}.json"

        data = {
            "baseline_name": name,
            "created_at": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "prompt_version": prompt_version,
            "model": model,
            "accuracy": accuracy,
            "category_breakdown": category_breakdown,
            "results": results,
            "average_deepeval_relevancy": average_deepeval_relevancy,
        }

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(
                data,
                f,
                indent=2,
                ensure_ascii=False,
            )

        return filename

    def load_baseline(self, name):

        filename = self.baseline_dir / f"{name}.json"

        if not filename.exists():
            return None

        with open(filename, encoding="utf-8") as f:
            return json.load(f)

    def list_baselines(self):

        return sorted(
            file.stem
            for file in self.baseline_dir.glob("*.json")
        )