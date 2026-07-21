from dotenv import load_dotenv
import os

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")

OLLAMA_HOST = os.getenv(
    "OLLAMA_HOST",
    "http://localhost:11434"
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "llama3.2"
)

DATABASE_PATH = os.getenv(
    "DATABASE_PATH",
    "history/evals.db"
)

SLACK_WEBHOOK_URL = os.getenv(
    "SLACK_WEBHOOK_URL"
)