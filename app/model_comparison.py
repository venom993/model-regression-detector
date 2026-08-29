import json
from pathlib import Path
from datetime import datetime

from app.evaluator import Evaluator


class ModelComparison:

    def __init__(
        self,
        model_a,
        model_b,
        prompt_version="2",
    ):

        self.model_a = model_a
        self.model_b = model_b
        self.prompt_version = prompt_version

        self.report_dir = Path("reports")
        self.report_dir.mkdir(
            exist_ok=True
        )

    def _calculate_metrics(
        self,
        results
    ):

        valid_results = [
            result
            for result in results
            if result.get("status")
            in ["passed", "failed"]
        ]

        total = len(valid_results)

        correct = sum(
            1
            for result in valid_results
            if result["status"] == "passed"
        )

        accuracy = (
            correct / total * 100
            if total
            else 0
        )

        latencies = [
            result["latency"]
            for result in valid_results
            if "latency" in result
        ]

        similarities = [
            result["summary_similarity"]
            for result in valid_results
            if "summary_similarity"
            in result
        ]

        deepeval_scores = [
            result["deepeval_relevancy"]
            for result in valid_results
            if "deepeval_relevancy"
            in result
        ]

        average_latency = (
            sum(latencies)
            / len(latencies)
            if latencies
            else 0
        )

        average_similarity = (
            sum(similarities)
            / len(similarities)
            if similarities
            else 0
        )

        average_deepeval = (
            sum(deepeval_scores)
            / len(deepeval_scores)
            if deepeval_scores
            else 0
        )

        return {
            "accuracy": round(
                accuracy,
                2
            ),

            "average_latency": round(
                average_latency,
                3
            ),

            "average_similarity": round(
                average_similarity,
                3
            ),

            "average_deepeval_relevancy": round(
                average_deepeval,
                3
            ),

            "total": total,

            "correct": correct,
        }

    def compare(self):

        print()
        print("==============================")
        print("MODEL-TO-MODEL COMPARISON")
        print("==============================")

        print()

        print(
            f"Model A: {self.model_a}"
        )

        print(
            f"Model B: {self.model_b}"
        )

        print()

        # ------------------------------------------
        # MODEL A
        # ------------------------------------------

        print(
            f"Evaluating {self.model_a}..."
        )

        evaluator_a = Evaluator(
            model=self.model_a,
            prompt_version=self.prompt_version,
        )

        results_a = evaluator_a.run()

        # ------------------------------------------
        # MODEL B
        # ------------------------------------------

        print(
            f"Evaluating {self.model_b}..."
        )

        evaluator_b = Evaluator(
            model=self.model_b,
            prompt_version=self.prompt_version,
        )

        results_b = evaluator_b.run()

        # ------------------------------------------
        # CALCULATE METRICS
        # ------------------------------------------

        metrics_a = self._calculate_metrics(
            results_a
        )

        metrics_b = self._calculate_metrics(
            results_b
        )

        # ------------------------------------------
        # DELTAS
        # ------------------------------------------

        accuracy_delta = round(
            metrics_b["accuracy"]
            - metrics_a["accuracy"],
            2,
        )

        latency_delta = round(
            (
                (
                    metrics_b["average_latency"]
                    - metrics_a["average_latency"]
                )
                / metrics_a["average_latency"]
                * 100
            )
            if metrics_a["average_latency"]
            else 0,
            2,
        )

        similarity_delta = round(
            (
                (
                    metrics_b["average_similarity"]
                    - metrics_a["average_similarity"]
                )
                / metrics_a["average_similarity"]
                * 100
            )
            if metrics_a["average_similarity"]
            else 0,
            2,
        )

        deepeval_delta = round(
            (
                (
                    metrics_b[
                        "average_deepeval_relevancy"
                    ]
                    -
                    metrics_a[
                        "average_deepeval_relevancy"
                    ]
                )
                /
                metrics_a[
                    "average_deepeval_relevancy"
                ]
                * 100
            )
            if metrics_a[
                "average_deepeval_relevancy"
            ]
            else 0,
            2,
        )

        # ------------------------------------------
        # OVERALL WINNER
        # ------------------------------------------

        
        # ------------------------------------------
        # WEIGHTED MODEL SCORE
        # ------------------------------------------
        #
        # Accuracy is the most important metric for
        # this email classification application.
        #
        # Accuracy      = 50%
        # Similarity    = 20%
        # DeepEval      = 20%
        # Latency       = 10%
        #

        weights = {
            "accuracy": 0.50,
            "similarity": 0.20,
            "deepeval": 0.20,
            "latency": 0.10,
        }

        # Normalize accuracy
        accuracy_a = metrics_a["accuracy"] / 100
        accuracy_b = metrics_b["accuracy"] / 100

        # Similarity and DeepEval are already 0-1
        similarity_a = metrics_a[
            "average_similarity"
        ]

        similarity_b = metrics_b[
            "average_similarity"
        ]

        deepeval_a = metrics_a[
            "average_deepeval_relevancy"
        ]

        deepeval_b = metrics_b[
            "average_deepeval_relevancy"
        ]

        # Latency is better when LOWER.
        # Normalize relative to both models.
        latency_a = metrics_a[
            "average_latency"
        ]

        latency_b = metrics_b[
            "average_latency"
        ]

        total_latency = (
            latency_a + latency_b
        )

        if total_latency:

            latency_score_a = (
                latency_b / total_latency
            )

            latency_score_b = (
                latency_a / total_latency
            )

        else:

            latency_score_a = 0.5
            latency_score_b = 0.5

        weighted_score_a = round(
            (
                accuracy_a
                * weights["accuracy"]
            )
            +
            (
                similarity_a
                * weights["similarity"]
            )
            +
            (
                deepeval_a
                * weights["deepeval"]
            )
            +
            (
                latency_score_a
                * weights["latency"]
            ),
            4,
        )

        weighted_score_b = round(
            (
                accuracy_b
                * weights["accuracy"]
            )
            +
            (
                similarity_b
                * weights["similarity"]
            )
            +
            (
                deepeval_b
                * weights["deepeval"]
            )
            +
            (
                latency_score_b
                * weights["latency"]
            ),
            4,
        )

        weighted_scores = {
            self.model_a:
            weighted_score_a,

            self.model_b:
            weighted_score_b,
        }
        if (
            weighted_score_a
            > weighted_score_b
        ):

            winner = self.model_a

        elif (
            weighted_score_b
            > weighted_score_a
        ):

            winner = self.model_b

        else:

            winner = "TIE"

        # ------------------------------------------
        # FINAL COMPARISON
        # ------------------------------------------

        comparison = {

            "timestamp":
            datetime.now().isoformat(),

            "prompt_version":
            self.prompt_version,

            "model_a":
            {
                "model": self.model_a,
                **metrics_a,
            },

            "model_b":
            {
                "model": self.model_b,
                **metrics_b,
            },

            "deltas":
            {
                "accuracy":
                accuracy_delta,

                "latency":
                latency_delta,

                "similarity":
                similarity_delta,

                "deepeval":
                deepeval_delta,
            },

            "scores": weighted_scores,
            "weights": weights,

            "winner":
            winner,
        }

        # ------------------------------------------
        # SAVE
        # ------------------------------------------

        output = (
            self.report_dir
            / "model_comparison.json"
        )

        with open(
            output,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                comparison,
                file,
                indent=2,
            )

        # ------------------------------------------
        # DISPLAY
        # ------------------------------------------

        print()
        print("==============================")
        print("MODEL COMPARISON RESULTS")
        print("==============================")

        print()

        print(
            f"{'Metric':<25}"
            f"{self.model_a:<18}"
            f"{self.model_b:<18}"
        )

        print("-" * 61)

        print(
            f"{'Accuracy':<25}"
            f"{metrics_a['accuracy']:<18}"
            f"{metrics_b['accuracy']:<18}"
        )

        print(
            f"{'Avg Latency (seconds)':<25}"
            f"{metrics_a['average_latency']:<18}"
            f"{metrics_b['average_latency']:<18}"
        )

        print(
            f"{'Avg Similarity':<25}"
            f"{metrics_a['average_similarity']:<18}"
            f"{metrics_b['average_similarity']:<18}"
        )

        print(
            f"{'DeepEval Relevancy':<25}"
            f"{metrics_a['average_deepeval_relevancy']:<18}"
            f"{metrics_b['average_deepeval_relevancy']:<18}"
        )

        print()

        print(
            f"Accuracy Delta: "
            f"{accuracy_delta}%"
        )

        print(
            f"Latency Delta: "
            f"{latency_delta}%"
        )

        print(
            f"Similarity Delta: "
            f"{similarity_delta}%"
        )

        print(
            f"DeepEval Delta: "
            f"{deepeval_delta}%"
        )
        print()

        print(
            "Weighted Score:"
        )

        print(
            f"{self.model_a}: "
            f"{weighted_score_a}"
        )

        print(
            f"{self.model_b}: "
            f"{weighted_score_b}"
        )
        print()

        print(
            f"Winner: {winner}"
        )

        print()

        print(
            "Comparison saved to:"
        )

        print(output)

        return comparison
