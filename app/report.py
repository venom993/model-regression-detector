from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt


class HTMLReport:

    def __init__(self):
        self.report_dir = Path("reports")
        self.report_dir.mkdir(exist_ok=True)

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

    def generate(
        self,
        comparison,
        breakdown,
        prompt_version,
        model,
        history,
    ):

        accuracy_chart = self.create_accuracy_chart(
            history
        )

        latency_chart = self.create_latency_chart(
            history
        )

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

        latency_section = ""

        if "previous_latency" in comparison:

            latency_section = f"""

            <h2>Performance Regression</h2>

            <ul>

                <li>
                    Previous Average Latency:
                    {comparison["previous_latency"]} seconds
                </li>

                <li>
                    Current Average Latency:
                    {comparison["current_latency"]} seconds
                </li>

                <li>
                    Latency Delta:
                    {comparison["latency_delta"]}%
                </li>

                <li>
                    Status:
                    <span class="{comparison["latency_status"].lower()}">
                        {comparison["latency_status"]}
                    </span>
                </li>

            </ul>
            """

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

<p><b>Date:</b> {datetime.now()}</p>

<p><b>Prompt Version:</b> {prompt_version}</p>

<p><b>Model:</b> {model}</p>


<h2>Accuracy Regression</h2>

<ul>

<li>
Previous Accuracy:
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


{latency_section}
<h2>Performance Regression</h2>

<ul>

<li>
Previous Avg Latency:
{comparison.get("previous_average_latency", "N/A")} seconds
</li>

<li>
Current Avg Latency:
{comparison.get("current_average_latency", "N/A")} seconds
</li>

<li>
Latency Delta:
{comparison.get("latency_delta", "N/A")}%
</li>

<li>
Status:
<span class="{comparison.get("latency_status", "PASS").lower()}">
{comparison.get("latency_status", "PASS")}
</span>
</li>

</ul>

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