import os

from ollama import Client

from app.config import (
    LLM_PROVIDER,
    OLLAMA_HOST,
    OLLAMA_MODEL,
)


class LLMClient:
    """
    Provider-aware LLM client.

    Currently supported:
    - Ollama

    The provider is selected using the LLM_PROVIDER
    environment variable.
    """

    def __init__(self, model=None):

        self.provider = LLM_PROVIDER.lower()

        self.model = model or OLLAMA_MODEL

        if self.provider == "ollama":

            self.client = Client(
                host=OLLAMA_HOST
            )

        elif self.provider == "openai":

            try:
                from openai import OpenAI
            except ImportError as e:
                raise ImportError(
                    "OpenAI provider requires the openai package."
                ) from e

            api_key = os.getenv(
                "OPENAI_API_KEY"
            )

            if not api_key:
                raise ValueError(
                    "OPENAI_API_KEY is required "
                    "when LLM_PROVIDER=openai."
                )

            self.client = OpenAI(
                api_key=api_key
            )

            self.model = os.getenv(
                "OPENAI_MODEL",
                "gpt-4o-mini"
            )

        else:

            raise ValueError(
                f"Unsupported LLM provider: "
                f"{self.provider}"
            )

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.0,
    ) -> str:

        if self.provider == "ollama":

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

            return response[
                "message"
            ][
                "content"
            ]

        elif self.provider == "openai":

            response = self.client.chat.completions.create(

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

                temperature=temperature,

                response_format={
                    "type": "json_object"
                },
            )

            return response.choices[
                0
            ].message.content

        raise RuntimeError(
            f"Unsupported provider: "
            f"{self.provider}"
        )