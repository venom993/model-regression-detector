import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="LLM Regression Dashboard",
    page_icon="📊",
    layout="wide",
)


# ==================================================
# LOAD EVALUATION HISTORY
# ==================================================

HISTORY_DIR = Path("history")


@st.cache_data
def load_history():
    files = sorted(HISTORY_DIR.glob("run_*.json"))

    history = []

    for file in files:
        try:
            with open(file, encoding="utf-8") as f:
                data = json.load(f)

            data["filename"] = file.name
            history.append(data)

        except Exception as e:
            st.warning(
                f"Could not read {file.name}: {e}"
            )

    return history


history = load_history()


# ==================================================
# HEADER
# ==================================================

st.title("🤖 LLM Regression Detection Dashboard")

st.markdown(
    """
    Monitor model accuracy, latency, regressions,
    improvements, and historical evaluation trends.
    """
)


# ==================================================
# CHECK FOR HISTORY
# ==================================================

if not history:
    st.error(
        "No evaluation history found in the history folder."
    )
    st.stop()


# ==================================================
# CURRENT AND PREVIOUS RUN
# ==================================================

current = history[-1]

previous = (
    history[-2]
    if len(history) > 1
    else None
)


current_accuracy = current.get(
    "accuracy",
    0
)

previous_accuracy = (
    previous.get("accuracy", 0)
    if previous
    else None
)


# ==================================================
# CALCULATE AVERAGE LATENCY
# ==================================================

def average_latency(run):

    if not run:
        return None

    results = run.get(
        "results",
        []
    )

    latencies = [
        item.get("latency")
        for item in results
        if item.get("latency") is not None
        and item.get("status") != "error"
    ]

    if not latencies:
        return None

    return round(
        sum(latencies) / len(latencies),
        3
    )


current_latency = average_latency(current)

previous_latency = (
    average_latency(previous)
    if previous
    else None
)


# ==================================================
# CALCULATE DELTAS
# ==================================================

accuracy_delta = (
    round(
        current_accuracy - previous_accuracy,
        2
    )
    if previous_accuracy is not None
    else None
)


latency_delta = None

if (
    previous_latency is not None
    and current_latency is not None
    and previous_latency > 0
):

    latency_delta = round(
        (
            (
                current_latency
                - previous_latency
            )
            / previous_latency
        )
        * 100,
        2
    )


# ==================================================
# TOP METRICS
# ==================================================

st.divider()

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "Current Accuracy",
        f"{current_accuracy}%",
        (
            f"{accuracy_delta}%"
            if accuracy_delta is not None
            else None
        ),
    )


with col2:

    st.metric(
        "Current Average Latency",
        (
            f"{current_latency}s"
            if current_latency is not None
            else "N/A"
        ),
        (
            f"{latency_delta}%"
            if latency_delta is not None
            else None
        ),
    )


with col3:

    st.metric(
        "Total Evaluation Runs",
        len(history)
    )


# ==================================================
# PREVIOUS RUN INFORMATION
# ==================================================

st.subheader("📌 Current vs Previous Evaluation")

comparison_data = {
    "Metric": [
        "Accuracy",
        "Average Latency",
    ],
    "Previous": [
        (
            f"{previous_accuracy}%"
            if previous_accuracy is not None
            else "N/A"
        ),
        (
            f"{previous_latency}s"
            if previous_latency is not None
            else "N/A"
        ),
    ],
    "Current": [
        f"{current_accuracy}%",
        (
            f"{current_latency}s"
            if current_latency is not None
            else "N/A"
        ),
    ],
    "Delta": [
        (
            f"{accuracy_delta}%"
            if accuracy_delta is not None
            else "N/A"
        ),
        (
            f"{latency_delta}%"
            if latency_delta is not None
            else "N/A"
        ),
    ],
}

comparison_df = pd.DataFrame(
    comparison_data
)

st.dataframe(
    comparison_df,
    use_container_width=True,
    hide_index=True,
)


# ==================================================
# BUILD HISTORY DATA
# ==================================================

history_rows = []

for index, run in enumerate(history):

    run_latency = average_latency(run)

    history_rows.append(
        {
            "Run": index + 1,
            "Filename": run.get(
                "filename"
            ),
            "Accuracy": run.get(
                "accuracy"
            ),
            "Average Latency": run_latency,
            "Prompt Version": run.get(
                "prompt_version",
                "Unknown"
            ),
            "Model": run.get(
                "model",
                "Unknown"
            ),
        }
    )


history_df = pd.DataFrame(
    history_rows
)


# ==================================================
# ACCURACY TREND
# ==================================================

st.divider()

st.subheader("📈 Accuracy Trend")

accuracy_chart = px.line(
    history_df,
    x="Run",
    y="Accuracy",
    markers=True,
    hover_data=[
        "Filename",
        "Prompt Version",
        "Model",
    ],
)

accuracy_chart.update_layout(
    yaxis_title="Accuracy (%)",
    xaxis_title="Evaluation Run",
)

st.plotly_chart(
    accuracy_chart,
    use_container_width=True,
)


# ==================================================
# LATENCY TREND
# ==================================================

st.subheader("⚡ Latency Trend")

latency_df = history_df.dropna(
    subset=["Average Latency"]
)

if not latency_df.empty:

    latency_chart = px.line(
        latency_df,
        x="Run",
        y="Average Latency",
        markers=True,
        hover_data=[
            "Filename",
            "Prompt Version",
            "Model",
        ],
    )

    latency_chart.update_layout(
        yaxis_title="Average Latency (seconds)",
        xaxis_title="Evaluation Run",
    )

    st.plotly_chart(
        latency_chart,
        use_container_width=True,
    )

else:

    st.info(
        "No latency data available."
    )


# ==================================================
# CATEGORY PERFORMANCE
# ==================================================

st.divider()

st.subheader("📊 Current Category Performance")

category_breakdown = current.get(
    "category_breakdown",
    {}
)

if category_breakdown:

    category_rows = []

    for category, values in category_breakdown.items():

        category_rows.append(
            {
                "Category": category,
                "Accuracy": values.get(
                    "accuracy",
                    0
                ),
                "Correct": values.get(
                    "correct",
                    0
                ),
                "Total": values.get(
                    "total",
                    0
                ),
            }
        )

    category_df = pd.DataFrame(
        category_rows
    )

    category_chart = px.bar(
        category_df,
        x="Category",
        y="Accuracy",
        text="Accuracy",
    )

    category_chart.update_layout(
        yaxis_title="Accuracy (%)"
    )

    st.plotly_chart(
        category_chart,
        use_container_width=True,
    )

    st.dataframe(
        category_df,
        use_container_width=True,
        hide_index=True,
    )

else:

    st.info(
        "No category breakdown available."
    )


# ==================================================
# REGRESSIONS AND IMPROVEMENTS
# ==================================================

st.divider()

st.subheader("🔍 Current Case Changes")

if previous:

    previous_results = {
        item["id"]: item
        for item in previous.get(
            "results",
            []
        )
        if item.get("status") != "error"
    }

    regressions = []
    improvements = []

    for item in current.get(
        "results",
        []
    ):

        if item.get("status") == "error":
            continue

        previous_item = previous_results.get(
            item.get("id")
        )

        if previous_item is None:
            continue

        old_pass = (
            previous_item.get("status")
            == "passed"
        )

        new_pass = (
            item.get("status")
            == "passed"
        )

        if old_pass and not new_pass:

            regressions.append(item)

        elif not old_pass and new_pass:

            improvements.append(item)


    reg_col, imp_col = st.columns(2)

    with reg_col:

        st.metric(
            "🔴 Regressions",
            len(regressions)
        )

    with imp_col:

        st.metric(
            "🟢 Improvements",
            len(improvements)
        )


    if regressions:

        st.subheader("🔴 Regressions")

        regression_df = pd.DataFrame(
            [
                {
                    "Email": item.get("id"),
                    "Expected": item.get(
                        "expected_category"
                    ),
                    "Predicted": item.get(
                        "predicted_category"
                    ),
                }
                for item in regressions
            ]
        )

        st.dataframe(
            regression_df,
            use_container_width=True,
            hide_index=True,
        )


    if improvements:

        st.subheader("🟢 Improvements")

        improvement_df = pd.DataFrame(
            [
                {
                    "Email": item.get("id"),
                    "Expected": item.get(
                        "expected_category"
                    ),
                    "Predicted": item.get(
                        "predicted_category"
                    ),
                }
                for item in improvements
            ]
        )

        st.dataframe(
            improvement_df,
            use_container_width=True,
            hide_index=True,
        )

else:

    st.info(
        "Run another evaluation to compare results."
    )


# ==================================================
# EVALUATION HISTORY TABLE
# ==================================================

st.divider()

st.subheader("📚 Evaluation History")

st.dataframe(
    history_df,
    use_container_width=True,
    hide_index=True,
)


# ==================================================
# RAW LATEST RUN
# ==================================================

with st.expander(
    "🔧 View Latest Evaluation Data"
):

    st.json(current)