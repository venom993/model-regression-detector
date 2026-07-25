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

        runs = [
            i + 1
            for i in range(len(history))
        ]

        accuracies = [
            item["accuracy"]
            for item in history
        ]

        plt.figure(figsize=(8,4))

        plt.plot(
            runs,
            accuracies,
            marker="o"
        )

        plt.title("Accuracy Over Time")

        plt.xlabel("Evaluation Run")

        plt.ylabel("Accuracy (%)")

        plt.grid(True)

        chart = self.report_dir / "accuracy.png"

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
        chart = self.create_accuracy_chart(
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

        improvements = ""

        for item in comparison["improvements"]:

            improvements += f"""
            <tr>
                <td>{item["id"]}</td>
                <td>{item["expected_category"]}</td>
                <td>{item["predicted_category"]}</td>
            </tr>
            """

        category_rows = ""

        for category, values in breakdown.items():

            category_rows += f"""
            <tr>
                <td>{category}</td>
                <td>{values["accuracy"]}%</td>
            </tr>
            """

        html = f"""
<!DOCTYPE html>

<html>

<head>

<title>Regression Report</title>

<style>

body {{
font-family: Arial;
margin:40px;
background:#f5f5f5;
}}

table {{
border-collapse: collapse;
width:100%;
margin-bottom:30px;
}}

th,td {{
border:1px solid #ddd;
padding:8px;
}}

th {{
background:#222;
color:white;
}}

.pass {{
color:green;
font-weight:bold;
}}

.warning {{
color:orange;
font-weight:bold;
}}

.critical {{
color:red;
font-weight:bold;
}}

</style>

</head>

<body>

<h1>Model Regression Report</h1>

<p><b>Date:</b> {datetime.now()}</p>

<p><b>Prompt Version:</b> {prompt_version}</p>

<p><b>Model:</b> {model}</p>

<h2>Overall</h2>

<ul>

<li>Previous Accuracy: {comparison["previous_accuracy"]}%</li>

<li>Current Accuracy: {comparison["current_accuracy"]}%</li>

<li>Delta: {comparison["delta"]}%</li>

<li>Status:
<span class="{comparison["status"].lower()}">
{comparison["status"]}
</span>
</li>

</ul>

<h2>Category Accuracy</h2>

<table>

<tr>

<th>Category</th>

<th>Accuracy</th>

</tr>

{category_rows}

</table>

<h2>Accuracy Trend</h2>

<img src="accuracy.png" width="700">

<h2>Regressions ({len(comparison["regressions"])})</h2>

<table>

<tr>

<th>Email</th>

<th>Expected</th>

<th>Predicted</th>

</tr>

{regressions}

</table>

<h2>Improvements ({len(comparison["improvements"])})</h2>

<table>

<tr>

<th>Email</th>

<th>Expected</th>

<th>Predicted</th>

</tr>

{improvements}

</table>

</body>

</html>
"""

        output = self.report_dir / "evaluation_report.html"

        with open(
            output,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(html)

        return output