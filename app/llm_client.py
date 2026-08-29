from ollama import Client

from app.config import (
    OLLAMA_HOST,
    OLLAMA_MODEL,
)


class LLMClient:
    """
    Wrapper around Ollama.
    """

    def __init__(self, model=None):

        self.client = Client(
            host=OLLAMA_HOST
        )

        self.model = model or OLLAMA_MODEL

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.0,
    ) -> str:

        response = self.client.chat(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            format="json",
            options={
                "temperature": temperature,
                "num_predict": 128,
                "seed": 42,
            },
        )

        return response["message"]["content"]
