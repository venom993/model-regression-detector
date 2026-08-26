# Testing GitHub Pull Request regression comments
import argparse
import json
import sys
from pathlib import Path

from app.history import HistoryManager
from app.config import OLLAMA_MODEL
from app.regression import RegressionDetector
from app.evaluator import Evaluator
from app.report import HTMLReport
from app.slack import SlackNotifier
from app.metrics import calculate_accuracy, category_breakdown
from app.trends import TrendAnalyzer
# --------------------------------------------------
# COMMAND LINE ARGUMENTS
# --------------------------------------------------

parser = argparse.ArgumentParser(
    description="LLM Regression Detection Pipeline"
)

parser.add_argument(
    "--save-baseline",
    type=str,
    help="Save the current evaluation as a named baseline",
)

parser.add_argument(
    "--baseline",
    type=str,
    help="Compare the current evaluation against a named baseline",
)

parser.add_argument(
    "--list-baselines",
    action="store_true",
    help="List all available baselines",
)

args = parser.parse_args()
# --------------------------------------------------
# LIST BASELINES
# --------------------------------------------------

if args.list_baselines:

    history_manager = HistoryManager()

    baselines = history_manager.list_baselines()

    if not baselines:
        print("\nNo baselines found.")

    else:
        print("\nAvailable baselines:")

        for baseline in baselines:
            print(f" - {baseline}")

    sys.exit(0)
evaluator = Evaluator()

results = evaluator.run()

print(f"Total results: {len(results)}")

for i, result in enumerate(results):
    if "expected_category" not in result:
        print(f"\nMissing expected_category at index {i}")
        print(result)


accuracy = calculate_accuracy(results)
breakdown = category_breakdown(results)

# --------------------------------------------------
# REGRESSION CHECK
# --------------------------------------------------

detector = RegressionDetector()

# IMPORTANT:
# Compare BEFORE saving the current run.
comparison = detector.compare(
    results,
    accuracy
)
Path("reports").mkdir(exist_ok=True)

with open(
    "reports/regression_comparison.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        comparison,
        f,
        indent=2,
        ensure_ascii=False
    )
print(
    "Regression comparison saved:"
    " reports/regression_comparison.json"
)

print("\n===================")
print("Evaluation Results")
print("===================")

print(f"Accuracy: {accuracy}%")

print("\nCategory Breakdown:")
print(breakdown)

print("\nRegression Report")
print("=================")

# --------------------------------------------------
# COMPARISON LABEL
# --------------------------------------------------

if args.baseline:
    comparison_label = "Baseline"
else:
    comparison_label = "Previous"


if comparison["status"] == "FIRST_RUN":

    print("Status            : FIRST_RUN")
    print("No previous evaluation found.")

else:

    print("\nAccuracy Regression")
    print("===================")

    print(
        f"{comparison_label} Accuracy : "
        f"{comparison['previous_accuracy']}"
    )

    print(
        f"Current Accuracy  : "
        f"{comparison['current_accuracy']}"
    )

    print(
        f"Delta             : "
        f"{comparison['delta']}%"
    )

    print(
        f"Status            : "
        f"{comparison['status']}"
    )



print("\nPerformance Regression")
print("======================")

print(
    f"{comparison_label} Avg Latency : "
    f"{comparison['previous_average_latency']} seconds"
)

print(
    f"Current Avg Latency  : "
    f"{comparison['current_average_latency']} seconds"
)

print(
    f"Latency Delta        : "
    f"{comparison['latency_delta']}%"
)

print(
    f"Status               : "
    f"{comparison['latency_status']}"
)
print("\nSemantic Similarity")
print("===================")

previous_similarity = comparison.get(
    "previous_average_similarity"
)

current_similarity = comparison.get(
    "current_average_similarity"
)

if previous_similarity is None:

    print(
        f"{comparison_label} Avg Similarity : N/A"
    )

else:

    print(
        f"{comparison_label} Avg Similarity : "
        f"{previous_similarity}"
    )

print(
    f"Current Avg Similarity  : "
    f"{current_similarity}"
)

print(
    f"Similarity Delta        : "
    f"{comparison['similarity_delta']}%"
)

print(
    f"Status                  : "
    f"{comparison['similarity_status']}"
)

print(
        "\nRegressions:",
        len(comparison["regressions"])
    )

for case in comparison["regressions"]:
        print(
            f" - {case['id']} "
            f"({case['expected_category']} -> "
            f"{case['predicted_category']})"
        )

print(
        "\nImprovements:",
        len(comparison["improvements"])
    )

for case in comparison["improvements"]:
        print(
            f" + {case['id']} "
            f"({case['expected_category']})"
        )


# --------------------------------------------------
# SAVE CURRENT RUN AFTER COMPARISON
# --------------------------------------------------

history = HistoryManager()

history_file = history.save_run(
    prompt_version=evaluator.prompt.version,
    model=OLLAMA_MODEL,
    accuracy=accuracy,
    category_breakdown=breakdown,
    results=results,
)

print(f"\nHistory saved: {history_file}")


# --------------------------------------------------
# JSON REPORT
# --------------------------------------------------

Path("reports").mkdir(exist_ok=True)

with open(
    "reports/evaluation_result.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        results,
        f,
        indent=2,
        ensure_ascii=False
    )

print(
    "\nReport saved:"
    " reports/evaluation_result.json"
)


# --------------------------------------------------
# HTML REPORT
# --------------------------------------------------

history_data = HistoryManager().get_history()

report = HTMLReport()

report_path = report.generate(
    comparison=comparison,
    breakdown=breakdown,
    prompt_version=evaluator.prompt.version,
    model=OLLAMA_MODEL,
    history=history_data,
)

print(
    f"\nHTML Report saved to:\n{report_path}"
)
trend_analyzer = TrendAnalyzer()

trend_paths = trend_analyzer.generate()

print(
    "\nHistorical trend charts generated:"
)

print(
    f"Accuracy: "
    f"{trend_paths['accuracy_chart']}"
)

print(
    f"Latency: "
    f"{trend_paths['latency_chart']}"
)


# --------------------------------------------------
# SLACK
# --------------------------------------------------

notifier = SlackNotifier()

notifier.send(
    comparison=comparison,
    prompt_version=evaluator.prompt.version,
    model=OLLAMA_MODEL,
)


# --------------------------------------------------
# CI FAILURE
# --------------------------------------------------

if (
    comparison["status"] == "CRITICAL"
    or comparison["latency_status"] == "CRITICAL"
    or comparison["similarity_status"] == "CRITICAL"
):
    print("\nCritical regression detected.")
    sys.exit(1)

print("\nCI regression test run")