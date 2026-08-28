from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt


class HTMLReport:

    def __init__(self):
        self.report_dir = Path("reports")
        self.report_dir.mkdir(exist_ok=True)

    # ==========================================
    # ACCURACY CHART
    # ==========================================

    def create_accuracy_chart(self, history):

        if len(history) < 2:
            return None

        runs = list(range(1, len(history) + 1))

        accuracies = [
            item["accuracy"]
            for item in history
        ]

        plt.figure(figsize=(10, 5))

        plt.plot(
            runs,
            accuracies,
            marker="o"
        )

        plt.title("Accuracy Over Time")
        plt.xlabel("Evaluation Run")
        plt.ylabel("Accuracy (%)")
        plt.grid(True)
        plt.tight_layout()

        chart = self.report_dir / "accuracy.png"

        plt.savefig(chart)
        plt.close()

        return chart.name

    # ==========================================
    # LATENCY CHART
    # ==========================================

    def create_latency_chart(self, history):

        if len(history) < 2:
            return None

        runs = []
        latencies = []

        for index, run in enumerate(history, start=1):

            results = run.get("results", [])

            valid_latencies = [
                item["latency"]
                for item in results
                if item.get("latency") is not None
                and item.get("status") != "error"
            ]

            if valid_latencies:

                average_latency = (
                    sum(valid_latencies)
                    / len(valid_latencies)
                )

                runs.append(index)

                latencies.append(
                    round(average_latency, 3)
                )

        if not latencies:
            return None

        plt.figure(figsize=(10, 5))

        plt.plot(
            runs,
            latencies,
            marker="o"
        )

        plt.title("Average Latency Over Time")
        plt.xlabel("Evaluation Run")
        plt.ylabel("Average Latency (seconds)")
        plt.grid(True)
        plt.tight_layout()

        chart = self.report_dir / "latency.png"

        plt.savefig(chart)
        plt.close()

        return chart.name

    # ==========================================
    # DEEPEVAL RELEVANCY CHART
    # ==========================================

    def create_deepeval_chart(self, history):

        if len(history) < 2:
            return None

        runs = []
        relevancy_scores = []

        for index, run in enumerate(history, start=1):

            score = run.get(
                "average_deepeval_relevancy"
            )

            if score is not None:

                runs.append(index)

                relevancy_scores.append(score)

        if not relevancy_scores:
            return None

        plt.figure(figsize=(10, 5))

        plt.plot(
            runs,
            relevancy_scores,
            marker="o"
        )

        plt.title(
            "Average DeepEval Relevancy Over Time"
        )

        plt.xlabel("Evaluation Run")

        plt.ylabel(
            "Average DeepEval Relevancy"
        )

        plt.grid(True)

        plt.tight_layout()

        chart = (
            self.report_dir
            / "deepeval_relevancy.png"
        )

        plt.savefig(chart)

        plt.close()

        return chart.name

    # ==========================================
    # GENERATE HTML REPORT
    # ==========================================

    def generate(
        self,
        comparison,
        breakdown,
        prompt_version,
        model,
        history,
    ):

        # ==========================================
        # CREATE CHARTS
        # ==========================================

        accuracy_chart = self.create_accuracy_chart(
            history
        )

        latency_chart = self.create_latency_chart(
            history
        )

        deepeval_chart = self.create_deepeval_chart(
            history
        )

        # ==========================================
        # BASELINE / PREVIOUS RUN LABEL
        # ==========================================

        baseline_name = comparison.get(
            "baseline_name"
        )

        if baseline_name:

            comparison_label = (
                f"Baseline ({baseline_name})"
            )

        else:

            comparison_label = "Previous Run"

        # ==========================================
        # REGRESSIONS
        # ==========================================

        regressions = ""

        for item in comparison["regressions"]:

            regressions += f"""
            <tr>
                <td>{item["id"]}</td>
                <td>{item["expected_category"]}</td>
                <td>{item["predicted_category"]}</td>
            </tr>
            """

        if not regressions:

            regressions = """
            <tr>
                <td colspan="3">
                    No regressions detected.
                </td>
            </tr>
            """

        # ==========================================
        # IMPROVEMENTS
        # ==========================================

        improvements = ""

        for item in comparison["improvements"]:

            improvements += f"""
            <tr>
                <td>{item["id"]}</td>
                <td>{item["expected_category"]}</td>
                <td>{item["predicted_category"]}</td>
            </tr>
            """

        if not improvements:

            improvements = """
            <tr>
                <td colspan="3">
                    No improvements detected.
                </td>
            </tr>
            """

        # ==========================================
        # CATEGORY BREAKDOWN
        # ==========================================

        category_rows = ""

        for category, values in breakdown.items():

            category_rows += f"""
            <tr>
                <td>{category}</td>
                <td>{values["total"]}</td>
                <td>{values["correct"]}</td>
                <td>{values["accuracy"]}%</td>
            </tr>
            """

        # ==========================================
        # ACCURACY CHART SECTION
        # ==========================================

        accuracy_chart_section = ""

        if accuracy_chart:

            accuracy_chart_section = f"""
            <h2>📈 Accuracy Trend</h2>

            <img
                src="{accuracy_chart}"
                class="chart"
                alt="Accuracy trend chart"
            >
            """

        # ==========================================
        # LATENCY CHART SECTION
        # ==========================================

        latency_chart_section = ""

        if latency_chart:

            latency_chart_section = f"""
            <h2>⚡ Latency Trend</h2>

            <img
                src="{latency_chart}"
                class="chart"
                alt="Latency trend chart"
            >
            """

        # ==========================================
        # DEEPEVAL CHART SECTION
        # ==========================================

        deepeval_chart_section = ""

        if deepeval_chart:

            deepeval_chart_section = f"""
            <h2>🧪 DeepEval Relevancy Trend</h2>

            <img
                src="{deepeval_chart}"
                class="chart"
                alt="DeepEval relevancy trend chart"
            >
            """

        # ==========================================
        # SEMANTIC SIMILARITY
        # ==========================================

        similarity_section = f"""

        <h2>Semantic Similarity Regression</h2>

        <ul>

            <li>
                {comparison_label} Avg Similarity:
                {comparison.get(
                    "previous_average_similarity",
                    "N/A"
                )}
            </li>

            <li>
                Current Avg Similarity:
                {comparison.get(
                    "current_average_similarity",
                    "N/A"
                )}
            </li>

            <li>
                Similarity Delta:
                {comparison.get(
                    "similarity_delta",
                    "N/A"
                )}%
            </li>

            <li>
                Status:
                <span class="{comparison.get(
                    "similarity_status",
                    "PASS"
                ).lower()}">

                    {comparison.get(
                        "similarity_status",
                        "PASS"
                    )}

                </span>
            </li>

        </ul>
        """

        # ==========================================
        # DEEPEVAL RELEVANCY
        # ==========================================

        deepeval_section = f"""

        <h2>🧪 DeepEval Relevancy</h2>

        <ul>

            <li>
                {comparison_label}
                Avg DeepEval Relevancy:

                {comparison.get(
                    "previous_average_deepeval_relevancy",
                    "N/A"
                )}
            </li>

            <li>
                Current Avg DeepEval Relevancy:

                {comparison.get(
                    "current_average_deepeval_relevancy",
                    "N/A"
                )}
            </li>

            <li>
                DeepEval Delta:

                {comparison.get(
                    "deepeval_delta",
                    "N/A"
                )}%
            </li>

            <li>
                Status:

                <span class="{comparison.get(
                    "deepeval_status",
                    "PASS"
                ).lower()}">

                    {comparison.get(
                        "deepeval_status",
                        "PASS"
                    )}

                </span>
            </li>

        </ul>
        """

        # ==========================================
        # GENERATE HTML
        # ==========================================

        html = f"""
<!DOCTYPE html>

<html>

<head>

<title>LLM Regression Report</title>

<style>

body {{
    font-family: Arial, sans-serif;
    margin: 40px;
    background: #f5f5f5;
}}

.container {{
    max-width: 1100px;
    margin: auto;
    background: white;
    padding: 30px;
    border-radius: 10px;
}}

table {{
    border-collapse: collapse;
    width: 100%;
    margin-bottom: 30px;
}}

th,
td {{
    border: 1px solid #ddd;
    padding: 10px;
    text-align: left;
}}

th {{
    background: #222;
    color: white;
}}

.pass {{
    color: green;
    font-weight: bold;
}}

.warning {{
    color: orange;
    font-weight: bold;
}}

.critical {{
    color: red;
    font-weight: bold;
}}

.first_run {{
    color: blue;
    font-weight: bold;
}}

.chart {{
    width: 100%;
    max-width: 900px;
    margin-bottom: 40px;
    border: 1px solid #ddd;
}}

</style>

</head>

<body>

<div class="container">

<h1>🤖 LLM Regression Report</h1>

<p>
    <b>Date:</b> {datetime.now()}
</p>

<p>
    <b>Prompt Version:</b> {prompt_version}
</p>

<p>
    <b>Model:</b> {model}
</p>

<p>
    <b>Comparison Target:</b>
    {comparison_label}
</p>


<h2>Accuracy Regression</h2>

<ul>

    <li>
        {comparison_label} Accuracy:
        {comparison["previous_accuracy"]}%
    </li>

    <li>
        Current Accuracy:
        {comparison["current_accuracy"]}%
    </li>

    <li>
        Delta:
        {comparison["delta"]}%
    </li>

    <li>
        Status:

        <span class="{comparison["status"].lower()}">

            {comparison["status"]}

        </span>
    </li>

</ul>


<h2>Performance Regression</h2>

<ul>

    <li>
        {comparison_label} Avg Latency:

        {comparison.get(
            "previous_average_latency",
            "N/A"
        )}

        seconds
    </li>

    <li>
        Current Avg Latency:

        {comparison.get(
            "current_average_latency",
            "N/A"
        )}

        seconds
    </li>

    <li>
        Latency Delta:

        {comparison.get(
            "latency_delta",
            "N/A"
        )}%
    </li>

    <li>
        Status:

        <span class="{comparison.get(
            "latency_status",
            "PASS"
        ).lower()}">

            {comparison.get(
                "latency_status",
                "PASS"
            )}

        </span>
    </li>

</ul>


{similarity_section}


{deepeval_section}


<h2>Category Accuracy</h2>

<table>

<tr>

    <th>Category</th>
    <th>Total</th>
    <th>Correct</th>
    <th>Accuracy</th>

</tr>

{category_rows}

</table>


{accuracy_chart_section}


{latency_chart_section}


{deepeval_chart_section}


<h2>
    Regressions ({len(comparison["regressions"])})
</h2>

<table>

<tr>

    <th>Email</th>
    <th>Expected</th>
    <th>Predicted</th>

</tr>

{regressions}

</table>


<h2>
    Improvements ({len(comparison["improvements"])})
</h2>

<table>

<tr>

    <th>Email</th>
    <th>Expected</th>
    <th>Predicted</th>

</tr>

{improvements}

</table>

</div>

</body>

</html>
"""

        # ==========================================
        # SAVE REPORT
        # ==========================================

        output = (
            self.report_dir
            / "evaluation_report.html"
        )

        with open(
            output,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(html)

        return output