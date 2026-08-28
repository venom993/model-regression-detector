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
REPORTS_DIR = Path("reports")

COMPARISON_FILE = (
    REPORTS_DIR / "regression_comparison.json"
)


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
def load_comparison():

    if not COMPARISON_FILE.exists():
        return None

    try:

        with open(
            COMPARISON_FILE,
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except Exception as e:

        st.warning(
            f"Could not read regression comparison: {e}"
        )

        return None


comparison = load_comparison()

if st.button("🔄 Refresh Dashboard"):
    st.cache_data.clear()
    st.rerun()

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
def average_similarity(run):

    if not run:
        return None

    results = run.get(
        "results",
        []
    )

    similarities = [
        item.get("summary_similarity")
        for item in results
        if item.get("summary_similarity") is not None
        and item.get("status") != "error"
    ]

    if not similarities:
        return None

    return round(
        sum(similarities) / len(similarities),
        3
    )
def average_deepeval_relevancy(run):

    if not run:
        return None

    # Newer runs may store the average directly
    direct_average = run.get(
        "average_deepeval_relevancy"
    )

    if direct_average is not None:
        return direct_average

    results = run.get(
        "results",
        []
    )

    scores = [
        item.get("deepeval_relevancy")
        for item in results
        if item.get("deepeval_relevancy") is not None
        and item.get("status") != "error"
    ]

    if not scores:
        return None

    return round(
        sum(scores) / len(scores),
        3
    )

current_latency = average_latency(current)

previous_latency = (
    average_latency(previous)
    if previous
    else None
)
current_similarity = average_similarity(current)

previous_similarity = (
    average_similarity(previous)
    if previous
    else None
)

current_deepeval = average_deepeval_relevancy(
    current
)

previous_deepeval = (
    average_deepeval_relevancy(previous)
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

similarity_delta = None

if (
    previous_similarity is not None
    and current_similarity is not None
    and previous_similarity > 0
):

    similarity_delta = round(
        (
            (
                current_similarity
                - previous_similarity
            )
            / previous_similarity
        )
        * 100,
        2
    )
deepeval_delta = None

if (
    previous_deepeval is not None
    and current_deepeval is not None
    and previous_deepeval > 0
):

    deepeval_delta = round(
        (
            (
                current_deepeval
                - previous_deepeval
            )
            / previous_deepeval
        )
        * 100,
        2
    )
# ==================================================
# TOP METRICS
# ==================================================

st.divider()

col1, col2, col3, col4, col5 = st.columns(5)

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

with col4:

    st.metric(
        "Current Avg Similarity",
        (
            f"{current_similarity:.3f}"
            if current_similarity is not None
            else "N/A"
        ),
        (
            f"{similarity_delta}%"
            if similarity_delta is not None
            else None
        ),
    )
with col5:

    st.metric(

        "🤖 DeepEval Relevancy",

        (
            f"{current_deepeval:.3f}"
            if current_deepeval is not None
            else "N/A"
        ),

        (
            f"{deepeval_delta}%"
            if deepeval_delta is not None
            else None
        ),

    )
# ==================================================
# PREVIOUS RUN INFORMATION
# ==================================================

st.subheader("📌 Current vs Previous Evaluation")

comparison_data = {
    "Metric": [
        "Accuracy",
        "Average Latency",
        "Average Semantic Similarity",
        "Average DeepEval Relevancy",
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
    (
        f"{previous_similarity}"
        if previous_similarity is not None
        else "N/A"
    ),
    (
        f"{previous_deepeval}"
        if previous_deepeval is not None
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
    (
        f"{current_similarity}"
        if current_similarity is not None
        else "N/A"
    ),
    (
        f"{current_deepeval}"
        if current_deepeval is not None
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
    (
        f"{similarity_delta}%"
        if similarity_delta is not None
        else "N/A"
    ),
    (
        f"{deepeval_delta}%"
        if deepeval_delta is not None
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

    run_similarity = average_similarity(run)
    run_deepeval = run.get(
        "average_deepeval_relevancy"
    )

    
    prompt_version = run.get(
        "prompt_version",
        "Unknown"
    )

    # Convert 1.0 -> 1 and 2.0 -> 2
    if isinstance(prompt_version, float):
        if prompt_version.is_integer():
            prompt_version = int(prompt_version)

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
            "Average Similarity": run_similarity,
            "Average DeepEval Relevancy": run_deepeval,
            "Prompt Version": str(
                prompt_version
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
# DEBUG: DETECTED MODELS
# ==================================================

st.subheader("🔧 Debug: Models Found in History")

st.write(
    history_df[
        ["Filename", "Model"]
    ]
)
st.write("Detected models:")

st.write(
    history_df["Model"].unique()
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
# SEMANTIC SIMILARITY TREND
# ==================================================

st.subheader("🧠 Semantic Similarity Trend")

similarity_df = history_df.dropna(
    subset=["Average Similarity"]
)

if not similarity_df.empty:

    similarity_chart = px.line(
        similarity_df,
        x="Run",
        y="Average Similarity",
        markers=True,
        hover_data=[
            "Filename",
            "Prompt Version",
            "Model",
        ],
    )

    similarity_chart.update_layout(
        yaxis_title="Average Semantic Similarity",
        xaxis_title="Evaluation Run",
    )

    st.plotly_chart(
        similarity_chart,
        use_container_width=True,
    )

else:

    st.info(
        "No semantic similarity data available."
    )
# ==================================================
# DEEPEVAL RELEVANCY TREND
# ==================================================

st.subheader("🤖 DeepEval Relevancy Trend")

deepeval_df = history_df.dropna(
    subset=[
        "Average DeepEval Relevancy"
    ]
)

if not deepeval_df.empty:

    deepeval_chart = px.line(

        deepeval_df,

        x="Run",

        y="Average DeepEval Relevancy",

        markers=True,

        hover_data=[

            "Filename",

            "Prompt Version",

            "Model",

        ],

    )

    deepeval_chart.update_layout(

        yaxis_title="Average DeepEval Relevancy",

        xaxis_title="Evaluation Run",

    )

    st.plotly_chart(

        deepeval_chart,

        use_container_width=True,

    )

else:

    st.info(
        "No DeepEval relevancy data available."
    )    
# ==================================================
# PROMPT VERSION COMPARISON
# ==================================================

st.divider()

st.subheader("📝 Prompt Version Comparison")


prompt_comparison_rows = []

for prompt_version in sorted(
    history_df["Prompt Version"]
    .dropna()
    .unique()
):

    prompt_runs = history_df[
        history_df["Prompt Version"]
        == prompt_version
    ]

    average_prompt_accuracy = round(
        prompt_runs["Accuracy"].mean(),
        2
    )

    average_prompt_latency = round(
        prompt_runs[
            "Average Latency"
        ].mean(),
        3
    )

    average_prompt_similarity = round(
        prompt_runs[
            "Average Similarity"
        ].mean(),
        3
    )
    average_prompt_deepeval = round(

    prompt_runs[

        "Average DeepEval Relevancy"

    ].mean(),

    3
)
    prompt_comparison_rows.append(
        {
            "Prompt Version": prompt_version,
            "Evaluation Runs": len(prompt_runs),
            "Avg Accuracy": average_prompt_accuracy,
            "Avg Latency (s)": average_prompt_latency,
            "Avg Similarity": average_prompt_similarity,
            "Avg DeepEval Relevancy": average_prompt_deepeval,
        }
    )


prompt_comparison_df = pd.DataFrame(
    prompt_comparison_rows
)


if not prompt_comparison_df.empty:

    st.dataframe(
        prompt_comparison_df,
        use_container_width=True,
        hide_index=True,
    )

    prompt_accuracy_chart = px.bar(
        prompt_comparison_df,
        x="Prompt Version",
        y="Avg Accuracy",
        text="Avg Accuracy",
    )

    prompt_accuracy_chart.update_layout(
        title="Average Accuracy by Prompt Version",
        yaxis_title="Average Accuracy (%)",
        xaxis_title="Prompt Version",
    )

    st.plotly_chart(
        prompt_accuracy_chart,
        use_container_width=True,
    )

    prompt_latency_chart = px.bar(
        prompt_comparison_df,
        x="Prompt Version",
        y="Avg Latency (s)",
        text="Avg Latency (s)",
    )

    prompt_latency_chart.update_layout(
        title="Average Latency by Prompt Version",
        yaxis_title="Average Latency (seconds)",
        xaxis_title="Prompt Version",
    )

    st.plotly_chart(
        prompt_latency_chart,
        use_container_width=True,
    )

    prompt_similarity_chart = px.bar(
        prompt_comparison_df,
        x="Prompt Version",
        y="Avg Similarity",
        text="Avg Similarity",
    )

    prompt_similarity_chart.update_layout(
        title="Average Semantic Similarity by Prompt Version",
        yaxis_title="Average Similarity",
        xaxis_title="Prompt Version",
    )

    st.plotly_chart(
        prompt_similarity_chart,
        use_container_width=True,
    )
    prompt_deepeval_chart = px.bar(
        
        prompt_comparison_df,
        x="Prompt Version",
        y="Avg DeepEval Relevancy",
        text="Avg DeepEval Relevancy",
    )
    prompt_deepeval_chart.update_layout(

    title="Average DeepEval Relevancy by Prompt Version",

    yaxis_title="Average DeepEval Relevancy",

    xaxis_title="Prompt Version",

    )
    st.plotly_chart(

    prompt_deepeval_chart,

    use_container_width=True,
    )

else:

    st.info(
        "No prompt version data available."
    )

# ==================================================
# MODEL-TO-MODEL COMPARISON
# ==================================================

st.divider()

st.subheader("🤖 Model-to-Model Comparison")


# Create the model comparison dataframe
model_comparison_df = (
    history_df
    .groupby("Model", dropna=False)
    .agg(
        **{
            "Evaluation Runs": (
                "Run",
                "count"
            ),
            "Avg Accuracy": (
                "Accuracy",
                "mean"
            ),
            "Avg Latency (s)": (
                "Average Latency",
                "mean"
            ),
            "Avg Similarity": (
                "Average Similarity",
                "mean"
            ),
             "Avg DeepEval Relevancy": (
                "Average DeepEval Relevancy",
                "mean"
            ),
        }
    )
    .reset_index()
)


# Round the values
model_comparison_df[
    "Avg Accuracy"
] = model_comparison_df[
    "Avg Accuracy"
].round(2)


model_comparison_df[
    "Avg Latency (s)"
] = model_comparison_df[
    "Avg Latency (s)"
].round(3)


model_comparison_df[
    "Avg Similarity"
] = model_comparison_df[
    "Avg Similarity"
].round(3)
model_comparison_df[
    "Avg DeepEval Relevancy"
] = model_comparison_df[
    "Avg DeepEval Relevancy"
].round(3)

if not model_comparison_df.empty:

    # ----------------------------------------------
    # MODEL COMPARISON TABLE
    # ----------------------------------------------

    st.dataframe(
        model_comparison_df,
        use_container_width=True,
        hide_index=True,
    )


    # ----------------------------------------------
    # MODEL ACCURACY
    # ----------------------------------------------

    st.subheader(
        "🎯 Accuracy by Model"
    )

    model_accuracy_chart = px.bar(
        model_comparison_df,
        x="Model",
        y="Avg Accuracy",
        text="Avg Accuracy",
    )

    model_accuracy_chart.update_layout(
        yaxis_title="Average Accuracy (%)",
        xaxis_title="Model",
    )

    st.plotly_chart(
        model_accuracy_chart,
        use_container_width=True,
    )


    # ----------------------------------------------
    # MODEL LATENCY
    # ----------------------------------------------

    st.subheader(
        "⚡ Latency by Model"
    )

    model_latency_chart = px.bar(
        model_comparison_df,
        x="Model",
        y="Avg Latency (s)",
        text="Avg Latency (s)",
    )

    model_latency_chart.update_layout(
        yaxis_title="Average Latency (seconds)",
        xaxis_title="Model",
    )

    st.plotly_chart(
        model_latency_chart,
        use_container_width=True,
    )


    # ----------------------------------------------
    # MODEL SEMANTIC SIMILARITY
    # ----------------------------------------------

    st.subheader(
        "🧠 Semantic Similarity by Model"
    )

    model_similarity_chart = px.bar(
        model_comparison_df,
        x="Model",
        y="Avg Similarity",
        text="Avg Similarity",
    )

    model_similarity_chart.update_layout(
        yaxis_title="Average Semantic Similarity",
        xaxis_title="Model",
    )

    st.plotly_chart(
        model_similarity_chart,
        use_container_width=True,
    )

    # ----------------------------------------------
# MODEL DEEPEVAL RELEVANCY
# ----------------------------------------------

    st.subheader(
    "🧪 DeepEval Relevancy by Model"
)

    model_deepeval_chart = px.bar(
       model_comparison_df,
       x="Model",
       y="Avg DeepEval Relevancy",
       text="Avg DeepEval Relevancy",
)

    model_deepeval_chart.update_layout(
       yaxis_title="Average DeepEval Relevancy",
       xaxis_title="Model",
)

    st.plotly_chart(
      model_deepeval_chart,
      use_container_width=True,
)
    # ==================================================
    # AUTOMATIC MODEL WINNERS
    # ==================================================

    st.divider()

    st.subheader(
        "🏆 Model Performance Winners"
    )


    if len(model_comparison_df) >= 2:

        # Best accuracy
        best_accuracy_model = (
            model_comparison_df.loc[
                model_comparison_df[
                    "Avg Accuracy"
                ].idxmax()
            ]
        )


        # Fastest model
        latency_models = model_comparison_df.dropna(
            subset=["Avg Latency (s)"]
        )

        fastest_model = None

        if not latency_models.empty:

            fastest_model = (
                latency_models.loc[
                    latency_models[
                        "Avg Latency (s)"
                    ].idxmin()
                ]
            )


        # Best semantic similarity
        similarity_models = (
            model_comparison_df.dropna(
                subset=["Avg Similarity"]
            )
        )

        best_similarity_model = None

        if not similarity_models.empty:

            best_similarity_model = (
                similarity_models.loc[
                    similarity_models[
                        "Avg Similarity"
                    ].idxmax()
                ]
            )

        deepeval_models = model_comparison_df.dropna(
          subset=["Avg DeepEval Relevancy"]
)

        best_deepeval_model = None

        if not deepeval_models.empty:

           best_deepeval_model = (
           deepeval_models.loc[
            deepeval_models[
                "Avg DeepEval Relevancy"
            ].idxmax()
        ]
    )
        winner_col1, winner_col2, winner_col3, winner_col4 = (
          st.columns(4)
)


        # Best Accuracy
        with winner_col1:

            st.metric(
                "🎯 Best Accuracy",
                best_accuracy_model[
                    "Model"
                ],
                (
                    f'{best_accuracy_model["Avg Accuracy"]}%'
                ),
            )


        # Fastest Model
        with winner_col2:

            if fastest_model is not None:

                st.metric(
                    "⚡ Fastest Model",
                    fastest_model[
                        "Model"
                    ],
                    (
                        f'{fastest_model["Avg Latency (s)"]}s'
                    ),
                )

            else:

                st.metric(
                    "⚡ Fastest Model",
                    "N/A",
                )


        # Best Similarity
        with winner_col3:

            if best_similarity_model is not None:

                st.metric(
                    "🧠 Best Similarity",
                    best_similarity_model[
                        "Model"
                    ],
                    (
                        f'{best_similarity_model["Avg Similarity"]:.3f}'
                    ),
                )

            else:

                st.metric(
                    "🧠 Best Similarity",
                    "N/A",
                )
        with winner_col4:

            if best_deepeval_model is not None:

                st.metric(
            "🧪 Best DeepEval",
            best_deepeval_model[
                "Model"
            ],
            (
                f'{best_deepeval_model["Avg DeepEval Relevancy"]:.3f}'
            ),
        )

            else:

               st.metric(
            "🧪 Best DeepEval",
            "N/A",
        )

    else:

        st.info(
            "Run evaluations with at least two "
            "different models to determine the winners."
        )


else:

    st.info(
        "No model data available."
    )
# ==================================================
# OVERALL RECOMMENDED MODEL
# ==================================================

st.divider()

st.subheader("⭐ Overall Recommended Model")


if len(model_comparison_df) >= 2:

    recommendation_df = model_comparison_df.copy()


    # ----------------------------------------------
    # NORMALIZE ACCURACY
    # Higher accuracy = better
    # ----------------------------------------------

    accuracy_min = recommendation_df[
        "Avg Accuracy"
    ].min()

    accuracy_max = recommendation_df[
        "Avg Accuracy"
    ].max()


    if accuracy_max != accuracy_min:

        recommendation_df[
            "Accuracy Score"
        ] = (
            recommendation_df[
                "Avg Accuracy"
            ]
            - accuracy_min
        ) / (
            accuracy_max
            - accuracy_min
        )

    else:

        recommendation_df[
            "Accuracy Score"
        ] = 1.0


    # ----------------------------------------------
    # NORMALIZE LATENCY
    # Lower latency = better
    # ----------------------------------------------

    latency_min = recommendation_df[
        "Avg Latency (s)"
    ].min()

    latency_max = recommendation_df[
        "Avg Latency (s)"
    ].max()


    if latency_max != latency_min:

        recommendation_df[
            "Latency Score"
        ] = (
            latency_max
            - recommendation_df[
                "Avg Latency (s)"
            ]
        ) / (
            latency_max
            - latency_min
        )

    else:

        recommendation_df[
            "Latency Score"
        ] = 1.0


    # ----------------------------------------------
    # NORMALIZE SEMANTIC SIMILARITY
    # Higher similarity = better
    # ----------------------------------------------

    similarity_min = recommendation_df[
        "Avg Similarity"
    ].min()

    similarity_max = recommendation_df[
        "Avg Similarity"
    ].max()


    if similarity_max != similarity_min:

        recommendation_df[
            "Similarity Score"
        ] = (
            recommendation_df[
                "Avg Similarity"
            ]
            - similarity_min
        ) / (
            similarity_max
            - similarity_min
        )

    else:

        recommendation_df[
            "Similarity Score"
        ] = 1.0

    # ----------------------------------------------
# NORMALIZE DEEPEVAL RELEVANCY
# Higher = better
# ----------------------------------------------

    deepeval_min = recommendation_df[
    "Avg DeepEval Relevancy"
].min()

    deepeval_max = recommendation_df[
    "Avg DeepEval Relevancy"
].max()

    if deepeval_max != deepeval_min:

        recommendation_df[
        "DeepEval Score"
    ] = (
        recommendation_df[
            "Avg DeepEval Relevancy"
        ]
        - deepeval_min
    ) / (
        deepeval_max
        - deepeval_min
    )

    else:

        recommendation_df[
        "DeepEval Score"
    ] = 1.0
    # ----------------------------------------------
    # CALCULATE OVERALL SCORE
    #
    # Accuracy: 40%
    # Latency: 30%
    # Similarity: 30%
    # ----------------------------------------------

    recommendation_df[
    "Overall Score"
] = (
    recommendation_df[
        "Accuracy Score"
    ] * 0.35

    +

    recommendation_df[
        "Latency Score"
    ] * 0.25

    +

    recommendation_df[
        "Similarity Score"
    ] * 0.20

    +

    recommendation_df[
        "DeepEval Score"
    ] * 0.20
)


    # Convert to percentage
    recommendation_df[
        "Overall Score"
    ] = (
        recommendation_df[
            "Overall Score"
        ] * 100
    ).round(2)


    # ----------------------------------------------
    # FIND BEST MODEL
    # ----------------------------------------------

    recommended_model = (
        recommendation_df.loc[
            recommendation_df[
                "Overall Score"
            ].idxmax()
        ]
    )


    # ----------------------------------------------
    # SHOW RECOMMENDATION
    # ----------------------------------------------

    col1, col2 = st.columns(2)


    with col1:

        st.metric(
            "🏆 Recommended Model",
            recommended_model[
                "Model"
            ],
        )


    with col2:

        st.metric(
            "⭐ Overall Score",
            (
                f'{recommended_model["Overall Score"]}%'
            ),
        )


    # ----------------------------------------------
    # EXPLANATION
    # ----------------------------------------------

    st.success(
        f"🏆 {recommended_model['Model']} is "
        "currently the best overall model based on "
        "accuracy, speed, and semantic similarity."
    )


    # ----------------------------------------------
    # SHOW MODEL SCORES
    # ----------------------------------------------

    score_display_df = recommendation_df[
        [
            "Model",
            "Avg Accuracy",
            "Avg Latency (s)",
            "Avg Similarity",
            "Avg DeepEval Relevancy",
            "Overall Score",
        ]
    ].sort_values(
        "Overall Score",
        ascending=False,
    )


    st.subheader(
        "📊 Overall Model Rankings"
    )


    st.dataframe(
        score_display_df,
        use_container_width=True,
        hide_index=True,
    )


    # ----------------------------------------------
    # OVERALL SCORE CHART
    # ----------------------------------------------

    overall_score_chart = px.bar(
        score_display_df,
        x="Model",
        y="Overall Score",
        text="Overall Score",
    )


    overall_score_chart.update_layout(
        title="Overall Model Performance Score",
        yaxis_title="Overall Score (%)",
        xaxis_title="Model",
    )


    st.plotly_chart(
        overall_score_chart,
        use_container_width=True,
    )


else:

    st.info(
        "Run evaluations with at least two "
        "different models to get an overall "
        "model recommendation."
    )
# ==================================================
# BASELINE COMPARISON
# ==================================================

st.divider()

st.subheader("🔬 Baseline Comparison")

if comparison:

    baseline_name = comparison.get(
        "baseline_name"
    )

    if baseline_name:

        st.markdown(
            f"**Baseline:** `{baseline_name}`"
        )

        baseline_col1, baseline_col2, baseline_col3, baseline_col4 = (
         st.columns(4)
)

        with baseline_col1:

            st.metric(
                "🎯 Accuracy",
                f'{comparison.get("current_accuracy", "N/A")}%',
                f'{comparison.get("delta", "N/A")}%'
            )

            st.caption(
                f'Baseline: '
                f'{comparison.get("previous_accuracy", "N/A")}%'
            )

        with baseline_col2:

            st.metric(
                "⚡ Average Latency",
                (
                    f'{comparison.get("current_average_latency", "N/A")}s'
                ),
                (
                    f'{comparison.get("latency_delta", "N/A")}%'
                )
            )

            st.caption(
                f'Baseline: '
                f'{comparison.get("previous_average_latency", "N/A")}s'
            )

        with baseline_col3:

            st.metric(
                "🧠 Semantic Similarity",
                comparison.get(
                    "current_average_similarity",
                    "N/A"
                ),
                (
                    f'{comparison.get("similarity_delta", "N/A")}%'
                )
            )

            st.caption(
                f'Baseline: '
                f'{comparison.get("previous_average_similarity", "N/A")}'
            )
        with baseline_col4:
            st.metric(
                "🤖 DeepEval Relevancy",
                comparison.get(
                    "current_average_deepeval_relevancy",
                    "N/A"
                ),
                (
                    f'{comparison.get("deepeval_delta", "N/A")}%'
                )
            )

            st.caption(
                f'Baseline: '
                f'{comparison.get("previous_average_deepeval_relevancy", "N/A")}'
            )
        st.markdown("### Regression Status")

        status_col1, status_col2, status_col3, status_col4 = (
            st.columns(4)
        )

        with status_col1:

            st.write(
                f"**Accuracy:** "
                f"{comparison.get('status', 'N/A')}"
            )

        with status_col2:

            st.write(
                f"**Latency:** "
                f"{comparison.get('latency_status', 'N/A')}"
            )

        with status_col3:

            st.write(
                f"**Similarity:** "
                f"{comparison.get('similarity_status', 'N/A')}"
            )
        with status_col4:
            st.write(
                f"**DeepEval Relevancy:** "
                f"{comparison.get('current_average_deepeval_relevancy', 'N/A')}"
                    )
        regressions_count = len(
            comparison.get(
                "regressions",
                []
            )
        )

        improvements_count = len(
            comparison.get(
                "improvements",
                []
            )
        )

        count_col1, count_col2 = st.columns(2)

        with count_col1:

            st.metric(
                "🔴 Regressions",
                regressions_count
            )

        with count_col2:

            st.metric(
                "🟢 Improvements",
                improvements_count
            )

    else:

        st.info(
            "No named baseline is currently being compared."
        )

else:

    st.info(
        "No regression comparison report found."
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