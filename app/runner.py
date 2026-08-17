import json
import sys
from pathlib import Path
from app.history import HistoryManager
from app.config import OLLAMA_MODEL
from app.regression import RegressionDetector
from app.evaluator import Evaluator
from app.report import HTMLReport
from app.slack import SlackNotifier
from app.metrics import (
    calculate_accuracy,
    category_breakdown
)


evaluator = Evaluator()

results = evaluator.run()

print(f"Total results: {len(results)}")

for i, result in enumerate(results):
    if "expected_category" not in result:
        print(f"\nMissing expected_category at index {i}")
        print(result)
accuracy = calculate_accuracy(results)
breakdown = category_breakdown(results)

history = HistoryManager()

history_file = history.save_run(

    prompt_version=evaluator.prompt.version,

    model=OLLAMA_MODEL,

    accuracy=accuracy,

    category_breakdown=breakdown,

    results=results,
)
detector = RegressionDetector()

comparison = detector.compare(
    results,
    accuracy
)


print("\n===================")
print("Evaluation Results")
print("===================")

print(f"Accuracy: {accuracy}%")

print("\nCategory Breakdown:")
print(breakdown)

print("\nRegression Report")
print("=================")

if comparison["status"] == "FIRST_RUN":

        print("Status            : FIRST_RUN")
        print("No previous evaluation found.")

else:

        print(f"Previous Accuracy : {comparison['previous_accuracy']}")
        print(f"Current Accuracy  : {comparison['current_accuracy']}")
        print(f"Delta             : {comparison['delta']}%")
        print(f"Status            : {comparison['status']}")

        if comparison["status"] != "FIRST_RUN":

            print("\nRegressions:", len(comparison["regressions"]))
            for case in comparison["regressions"]:
                print(
                    f" - {case['id']} "
                    f"({case['expected_category']} -> "
                    f"{case['predicted_category']})"
                )

        if comparison["status"] != "FIRST_RUN":

            print("\nImprovements:", len(comparison["improvements"]))

        for case in comparison["improvements"]:
            print(
                f" + {case['id']} "
                f"({case['expected_category']})"
            )



Path("reports").mkdir(
    exist_ok=True
)


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
history = HistoryManager().get_history()
report = HTMLReport()

report_path = report.generate(
    comparison=comparison,
    breakdown=breakdown,
    prompt_version=evaluator.prompt.version,
    model=OLLAMA_MODEL,
    history=history,
)

print(f"\nHTML Report saved to:\n{report_path}")
notifier = SlackNotifier()

notifier.send(
    comparison=comparison,
    prompt_version=evaluator.prompt.version,
    model=OLLAMA_MODEL,
)
if comparison["status"] == "CRITICAL":

    print("\nCritical regression detected.")

    sys.exit(1)
    print("CI regression test run")