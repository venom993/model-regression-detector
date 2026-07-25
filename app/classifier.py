import json
import re

from pydantic import BaseModel

from app.llm_client import LLMClient
from app.prompt_loader import PromptConfig


class ClassificationResult(BaseModel):
    category: str
    summary: str


class EmailClassifier:

    def __init__(self, prompt: PromptConfig):
        self.prompt = prompt
        self.llm = LLMClient()

    def _parse_json(self, response: str):
        """
        Extract and repair JSON returned by the LLM.
        """

        # Remove markdown code fences if present
        response = response.replace("```json", "").replace("```", "").strip()

        # Extract JSON object
        match = re.search(r"\{.*", response, re.DOTALL)

        if not match:
            raise ValueError(f"No JSON found:\n{response}")

        json_text = match.group().strip()

        # Auto-fix missing closing brace
        if not json_text.endswith("}"):
            json_text += "}"

        return json.loads(json_text)

    def classify(self, email: str) -> ClassificationResult:

        prompt = f"""
Classify this customer email.

Email:
{email}

Return ONLY valid JSON.

Example:

{{
  "category":"billing",
  "summary":"Customer requests a refund."
}}

Do not include explanations.
Do not include markdown.
"""

        MAX_RETRIES = 2

        for attempt in range(MAX_RETRIES):

            response = self.llm.generate(
                system_prompt=self.prompt.system_prompt,
                user_prompt=prompt
            )

            try:
                data = self._parse_json(response)
                return ClassificationResult(**data)

            except Exception:

                if attempt == MAX_RETRIES - 1:
                    raise ValueError(
                        f"LLM returned invalid JSON:\n{response}"
                    )

        raise RuntimeError("Unexpected classifier failure.")