# 🤖 LLM Regression Detection Pipeline

An automated **LLM evaluation and regression detection system** for testing AI-powered applications against a golden dataset.

The project evaluates an LLM's classification accuracy, response latency, semantic similarity, and DeepEval relevancy. It maintains evaluation history, detects regressions between runs, generates reports and trend charts, sends Slack notifications, and can fail CI when a critical regression is detected.

The system currently uses **Ollama** to run local LLMs, with `llama3.2:3b` as the default model.

---

## 📌 Project Overview

LLM applications can silently become worse when:

* the underlying model changes
* the prompt changes
* the model configuration changes
* the application code changes
* a new model version is introduced
* multilingual or noisy inputs are introduced

Traditional unit tests are not enough for these situations because LLMs produce probabilistic outputs.

This project solves that problem by maintaining a **golden evaluation dataset** and automatically testing the model against it.

The pipeline:


                    ┌─────────────────────┐
                    │   Golden Dataset    │
                    │  100 Test Cases     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    LLM Evaluator    │
                    │      Ollama         │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Classification      │
                    │ Results             │
                    └──────────┬──────────┘
                               │
             ┌─────────────────┼─────────────────┐
             │                 │                 │
             ▼                 ▼                 ▼
        Accuracy           Latency         Similarity
             │                 │                 │
             └─────────────────┼─────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     DeepEval        │
                    │    Relevancy        │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Regression Detector │
                    └──────────┬──────────┘
                               │
             ┌─────────────────┼──────────────────┐
             │                 │                  │
             ▼                 ▼                  ▼
          HTML              Slack             CI/CD
          Report            Alert             Pass/Fail


---

# ✨ Features

## 1. Golden Dataset Evaluation

The project contains a 100-case golden dataset:

```text
datasets/golden_dataset_v1.json
```

The dataset includes:

* billing cases
* technical cases
* account cases
* general inquiries
* ambiguous inputs
* empty input
* noisy input
* misspelled input
* slang
* multilingual messages
* mixed-language messages
* difficult classification cases

Example:


{
  "id": "email_001",
  "input": "I was charged twice for my subscription this month.",
  "expected_output": {
    "category": "billing",
    "summary": "Customer was charged twice for a subscription."
  },
  "expected_difficulty": "easy",
  "notes": "Basic duplicate charge detection"
}


---

# 2. LLM Classification

The application uses Ollama to run a local LLM.

Default configuration:


Provider: Ollama
Model: llama3.2:3b
Host: http://localhost:11434


The classifier expects the model to return structured JSON:


{
  "category": "billing",
  "summary": "Customer requests a refund."
}


The classifier also contains JSON extraction and retry handling for malformed LLM responses.

---

# 3. Multiple Evaluation Metrics

The pipeline evaluates several dimensions of model quality.

### Accuracy

Measures whether the predicted category matches the expected category.

Example:


Expected: billing
Predicted: billing

Result: PASS


---

### Latency

Measures how long the LLM takes to produce a response.

Example:


Average latency: 2.431 seconds


Latency is tracked over time and can participate in regression detection.

---

### Semantic Similarity

The system compares the generated summary with the expected summary.

This helps detect situations where the category is correct but the generated explanation becomes significantly worse.

---

### DeepEval Relevancy

DeepEval is used to evaluate how relevant the generated response is to the original input.

The project uses:


AnswerRelevancyMetric


with:


threshold = 0.5


The DeepEval evaluator uses the same Ollama model configuration.

---

# 4. Regression Detection

The project compares the current evaluation with a previous run or a named baseline.

Example:


Previous Accuracy : 94.0%
Current Accuracy  : 89.0%

Delta             : -5.0%
Status            : CRITICAL


The pipeline can detect regressions in:

* accuracy
* latency
* semantic similarity
* DeepEval relevancy

Each test case can also be classified as:


Regression
Improvement
Unchanged


---

# 5. Baseline Support

Named baselines can be created.

For example:

powershell
python -m app.runner --save-baseline production-v1


Later, the current model can be compared against that baseline:

powershell
python -m app.runner --baseline production-v1


Available baselines can be listed with:

powershell
python -m app.runner --list-baselines


This makes it possible to compare a new prompt or model against a known-good version rather than only against the immediately previous run.

---

# 6. Model-to-Model Comparison

The project supports comparing two Ollama models.

Run:

powershell
python -m app.runner --compare-models


The comparison evaluates:

* accuracy
* average latency
* semantic similarity
* DeepEval relevancy

A weighted score is calculated.

Current weights:

| Metric              | Weight |
| ------------------- | -----: |
| Accuracy            |    50% |
| Semantic Similarity |    20% |
| DeepEval Relevancy  |    20% |
| Latency             |    10% |

Accuracy has the highest weight because this application is primarily an email classification system.

The result identifies the overall winner.

Example:

text
Weighted Score:

llama3.2:3b: 0.8421
other-model: 0.8174

Winner: llama3.2:3b


The comparison is saved to:


reports/model_comparison.json


---

# 7. Historical Tracking

Every evaluation run can be stored in the history system.

The database is configured as:


history/evals.db


Historical runs can be used to determine whether model quality is improving or degrading.

The project also stores run information under:


history/


---

# 8. HTML Reports

After an evaluation, the application generates an HTML report:


reports/evaluation_report.html


The report contains:

* evaluation date
* prompt version
* model
* comparison target
* accuracy
* latency
* semantic similarity
* DeepEval relevancy
* category accuracy
* regressions
* improvements
* historical charts

Open the report directly in your browser.

On Windows:

powershell
start reports\evaluation_report.html


---

# 9. Trend Charts

Historical performance is visualized using Matplotlib.

The project generates charts for:

### Accuracy


reports/accuracy.png


and:


reports/accuracy_trend.png


### Latency


reports/latency.png


and:


reports/latency_trend.png


### DeepEval Relevancy

text
reports/deepeval_relevancy.png


These charts make it easier to see long-term model performance changes.

---

# 10. Slack Notifications

The project supports Slack notifications through a webhook.

Notifications can contain:

* model
* prompt version
* previous accuracy
* current accuracy
* accuracy delta
* latency
* similarity
* DeepEval relevancy
* regression count
* improvement count

Configure the webhook in `.env`:

env
SLACK_WEBHOOK_URL=https://hooks.slack.com/...


If the webhook is not configured, the application continues without sending a notification.

---

# 🏗️ Project Structure

The main project structure is:


model-regression-detector/
│
├── app/
│   ├── __init__.py
│   ├── classifier.py
│   ├── config.py
│   ├── deepeval_evaluator.py
│   ├── evaluator.py
│   ├── history.py
│   ├── llm_client.py
│   ├── metrics.py
│   ├── model_comparison.py
│   ├── prompt_loader.py
│   ├── regression.py
│   ├── report.py
│   ├── runner.py
│   ├── slack.py
│   └── trends.py
│
├── datasets/
│   └── golden_dataset_v1.json
│
├── prompts/
│   └── ...
│
├── history/
│   └── ...
│
├── reports/
│   └── ...
│
├── tests/
│   └── ...
│
├── .env
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md


---

# 💻 Requirements

Before running the project locally, install:

* Windows 10/11
* Python 3.11+
* Git
* Ollama
* Docker Desktop — optional for local Docker execution

The project has been developed and tested around a Windows development environment.

---

# 🐍 Python Setup

Clone the repository:

powershell
git clone <YOUR-GITHUB-REPOSITORY-URL>


Enter the project:

powershell
cd model-regression-detector


Create a virtual environment:

powershell
python -m venv .venv


Activate it:

powershell
.venv\Scripts\Activate.ps1


If PowerShell blocks script execution, you can activate the environment using:

powershell
.venv\Scripts\activate


or run Python directly from the environment:

powershell
.venv\Scripts\python.exe --version


---

# 📦 Install Dependencies

Install the required packages:

powershell
pip install -r requirements.txt


The project uses packages including:


ollama
deepeval
pydantic
pydantic-settings
python-dotenv
PyYAML
requests
aiohttp
aiosqlite
pandas
numpy
matplotlib
plotly
streamlit
Jinja2
tqdm
pytest
pytest-asyncio


---

# 🦙 Ollama Setup

Install Ollama and make sure the Ollama service is running.

Check:

powershell
ollama --version


Check installed models:

powershell
ollama list


The default model is:


llama3.2:3b


If it is not installed:

powershell
ollama pull llama3.2:3b


Test it:

powershell
ollama run llama3.2:3b


Then exit the model session.

Verify that the API is available:

powershell
curl http://localhost:11434/api/tags


The application expects Ollama to be available at:

text
http://localhost:11434


---

# 🔐 Environment Configuration

Create a `.env` file in the project root.

Example:


LLM_PROVIDER=ollama

OLLAMA_HOST=http://localhost:11434

OLLAMA_MODEL=llama3.2:3b

DATABASE_PATH=history/evals.db

SLACK_WEBHOOK_URL=


### Important

Do **not** commit your real `.env` file to GitHub if it contains secrets.

Add `.env` to `.gitignore`.

Use `.env.example` for the safe configuration template.

---

# ▶️ Run the Evaluation

With the virtual environment activated and Ollama running:

powershell
python -m app.runner


The pipeline will:

1. Load the prompt configuration.
2. Load the golden dataset.
3. Send each test case to Ollama.
4. Parse the LLM response.
5. Calculate classification accuracy.
6. Measure latency.
7. Calculate semantic similarity.
8. Run DeepEval relevancy evaluation.
9. Compare against previous history.
10. Detect regressions.
11. Save evaluation results.
12. Generate an HTML report.
13. Generate trend charts.
14. Send a Slack notification if configured.
15. Return an appropriate process exit code.

---

# 📊 Example Output

A successful evaluation may look similar to:


Total results: 100

===================
Evaluation Results
===================

Accuracy: 94.0%

Average DeepEval Relevancy: 0.873

Category Breakdown:
{
    ...
}

Regression Report
=================

Previous Accuracy : 95.0
Current Accuracy  : 94.0
Delta             : -1.0%
Status            : WARNING

Performance Regression
======================

Previous Avg Latency : 2.431 seconds
Current Avg Latency  : 2.512 seconds
Latency Delta        : 3.33%
Status               : PASS

Semantic Similarity
===================

Previous Avg Similarity : 0.891
Current Avg Similarity  : 0.884
Similarity Delta        : -0.79%
Status                  : PASS

DeepEval Relevancy
==================

Previous Avg Relevancy : 0.875
Current Avg Relevancy  : 0.873
DeepEval Delta         : -0.23%
Status                 : PASS

Regressions: 2
Improvements: 1


---

# 🚨 CI Exit Codes

The runner is designed to work with CI/CD systems.

The process exits with:

text
0 = successful evaluation
1 = critical regression detected


A critical regression occurs when one of the monitored metrics has a `CRITICAL` status:


Accuracy
Latency
Semantic Similarity
DeepEval Relevancy


This is important because GitHub Actions can use the process exit code to automatically mark the workflow as failed.

---

# 🐳 Docker

The project also supports Docker execution.

Build the image:

powershell
docker compose build


Start the service:

powershell
docker compose up


The Docker configuration uses:

LLM_PROVIDER=ollama
OLLAMA_HOST=http://host.docker.internal:11434
OLLAMA_MODEL=llama3.2:3b


The `host.docker.internal` address allows the container to communicate with Ollama running on the Windows host.

---

# 🔎 Docker + Ollama Architecture

When running the application in Docker on Windows:


┌───────────────────────────────┐
│          Windows Host         │
│                               │
│   ┌───────────────────────┐   │
│   │       Ollama           │   │
│   │   llama3.2:3b          │   │
│   │   :11434               │   │
│   └───────────▲───────────┘   │
│               │               │
│     host.docker.internal      │
│               │               │
│   ┌───────────┴───────────┐   │
│   │      Docker           │   │
│   │                       │   │
│   │ Regression Detector   │   │
│   └───────────────────────┘   │
│                               │
└───────────────────────────────┘


---

# 🧪 DeepEval

DeepEval is integrated through:


app/deepeval_evaluator.py


The evaluator uses:

python
OllamaModel


and:

python
AnswerRelevancyMetric


The configured threshold is:


0.5


DeepEval results are stored with the individual evaluation results and aggregated into:


average_deepeval_relevancy


This value is also used by regression detection and model comparison.

---

# 📈 Model Comparison

To compare the configured models:

powershell
python -m app.runner --compare-models


The project uses:


OLLAMA_MODEL


and:


OLLAMA_COMPARE_MODEL


for the two models.

The comparison produces:


reports/model_comparison.json


You can use this to determine which model provides the best balance between:


Accuracy
Similarity
DeepEval Relevancy
Latency


---

# 🏁 Baselines

## Save a baseline

Create a named baseline:

powershell
python -m app.runner --save-baseline production-v1


This allows you to preserve a known-good model evaluation.

---

## List baselines

powershell
python -m app.runner --list-baselines


Example:


Available baselines:

 - production-v1
 - production-v2
 - pre-release


---

## Compare against a baseline

powershell
python -m app.runner --baseline production-v1


This is useful before deploying a new model or changing a prompt.

---

# 🔄 Recommended Development Workflow

A recommended workflow is:


1. Modify prompt/model
          ↓
2. Run evaluation
          ↓
3. Compare against baseline
          ↓
4. Inspect regression report
          ↓
5. Review HTML report
          ↓
6. Compare models if necessary
          ↓
7. Commit changes
          ↓
8. Push to GitHub
          ↓
9. GitHub Actions runs regression tests
          ↓
10. CI passes or fails


---

# 🌿 Git Workflow

Check the current branch:

powershell
git branch --show-current


Switch to `main`:

powershell
git switch main


Update it:

powershell
git pull origin main


Check status:

powershell
git status


Add changes:

powershell
git add .


Commit:

powershell
git commit -m "Add LLM regression detection pipeline"


Push:

powershell
git push origin main


---

# 🤖 GitHub Actions CI

The intended CI workflow runs the regression detector automatically when code is pushed to GitHub.

The workflow should:


Git Push
   │
   ▼
GitHub Actions
   │
   ▼
Build Docker image
   │
   ▼
Start regression environment
   │
   ▼
Run golden dataset
   │
   ▼
Evaluate model
   │
   ├── PASS ──► Workflow succeeds
   │
   └── CRITICAL ──► Workflow fails


Because `app/runner.py` returns:


exit code 0


for success and:


exit code 1


for critical regressions, GitHub Actions can directly use the result to determine whether the workflow succeeds.

---

# 📁 Generated Files

After running the pipeline, you may see:


reports/
│
├── evaluation_report.html
├── evaluation_result.json
├── regression_comparison.json
├── model_comparison.json
├── accuracy.png
├── latency.png
├── deepeval_relevancy.png
├── accuracy_trend.png
└── latency_trend.png


Historical data:


history/
│
├── evals.db
└── run_*.json


---

# 🧩 Main Components

## `app/classifier.py`

Responsible for:

* sending classification prompts
* communicating with the LLM client
* parsing JSON
* repairing common JSON formatting problems
* retrying invalid responses
* validating output with Pydantic

Main class:

python
EmailClassifier


---

## `app/evaluator.py`

Responsible for running the golden dataset through the classifier and collecting evaluation results.

---

## `app/deepeval_evaluator.py`

Responsible for DeepEval-based relevancy evaluation.

Main class:

python
DeepEvalEvaluator


---

## `app/regression.py`

Responsible for determining whether the current evaluation represents a regression.

---

## `app/history.py`

Responsible for storing and retrieving historical evaluation information and named baselines.

---

## `app/model_comparison.py`

Responsible for evaluating two models and calculating weighted model scores.

---

## `app/report.py`

Responsible for generating:


HTML reports
Accuracy charts
Latency charts
DeepEval charts


---

## `app/trends.py`

Responsible for loading historical runs and generating long-term trend charts.

---

## `app/slack.py`

Responsible for sending evaluation results to Slack.

---

## `app/runner.py`

The main orchestration layer.

It connects:


Evaluator
       ↓
Metrics
       ↓
DeepEval
       ↓
RegressionDetector
       ↓
History
       ↓
Reports
       ↓
Trends
       ↓
Slack
       ↓
CI Exit Code


---

# 🛡️ Why This Project Is Useful

Without regression testing, a prompt change can look harmless:


Old Prompt → 95% accuracy
New Prompt → 88% accuracy


The application may still technically run without errors.

Traditional tests could therefore pass.

This project instead treats model behavior as something that needs continuous testing.

For example:


Prompt Version 1
Accuracy: 95%
Similarity: 0.91
DeepEval: 0.89
Latency: 2.1s


After a prompt modification:


Prompt Version 2
Accuracy: 86%
Similarity: 0.79
DeepEval: 0.76
Latency: 2.5s


The regression detector can identify the degradation and stop the CI pipeline.

---

# 🌍 Dataset Coverage

The current golden dataset contains 100 cases covering:

### Billing

Examples include:


Duplicate charges
Refund requests
Payment failures
Recurring charges
Unknown charges
Premium feature access


### Technical

Examples include:


Application crashes
Slow websites
File upload problems
Notifications
Update problems
Service outages


### Account

Examples include:


Forgotten passwords
Login failures
Account lockouts
Email changes
Account deletion
Unauthorized access


### General

Examples include:


Product questions
Pricing questions
Support contact
Discount questions
General feedback


### Difficult Cases

The dataset also includes:


Empty messages
Random text
Typos
Slang
Emotional language
Ambiguous requests
Mixed-language messages
Spanish
French
German
Arabic

---

# 🧪 Testing

The project is prepared for automated testing with:


pytest
pytest-asyncio


Run:

powershell
pytest


Currently, the project does not contain a complete automated unit-test suite, so this is an area for future development.

---

# 🔮 Future Improvements

Potential future improvements include:

* GitHub Actions CI
* automatic PR regression comments
* automatic HTML report artifacts
* test result artifacts
* more unit tests
* more golden dataset cases
* RAGAS integration
* multiple model providers
* OpenAI evaluation support
* Anthropic evaluation support
* configurable regression thresholds
* dashboard improvements
* Streamlit monitoring dashboard
* scheduled nightly evaluations
* automatic baseline management
* prompt A/B testing
* model performance history
* production monitoring

---

# 🔐 Security

Never commit secrets such as:


.env
Slack webhooks
API keys
tokens
credentials


Use environment variables or GitHub Actions Secrets instead.

The repository should contain:


.env.example


rather than your real `.env`.

---

# 📜 License

Add your preferred license here.

For example:


MIT License


---

# 👨‍💻 Author

Developed as an LLM evaluation and CI/CD project demonstrating:


Python
Ollama
DeepEval
Pydantic
LLM Evaluation
Regression Testing
Docker
GitHub Actions
Slack
Matplotlib
SQLite
CI/CD


---

# 🚀 Quick Start

For someone who has just cloned the repository:

powershell
git clone <YOUR-GITHUB-REPOSITORY-URL>

cd model-regression-detector

python -m venv .venv

.venv\Scripts\Activate.ps1

pip install -r requirements.txt

ollama pull llama3.2:3b

python -m app.runner


Then open:

text
reports/evaluation_report.html


On Windows:

\powershell
start reports\evaluation_report.html


---

# ✅ Project Status

Current capabilities:

`
✅ Golden dataset
✅ 100 evaluation cases
✅ Ollama integration
✅ JSON response validation
✅ Retry handling
✅ Accuracy evaluation
✅ Latency evaluation
✅ Semantic similarity
✅ DeepEval relevancy
✅ Regression detection
✅ Historical evaluation storage
✅ Named baselines
✅ Model-to-model comparison
✅ Weighted model scoring
✅ HTML reports
✅ Accuracy trends
✅ Latency trends
✅ DeepEval trends
✅ Slack notifications
✅ CI failure exit codes
✅ Docker support



The next major CI/CD step is to connect the existing `app/runner.py` exit-code behavior to a GitHub Actions workflow so that every push can automatically execute the Docker regression test and prevent a merge/deployment when a critical model or prompt regression is detected.
