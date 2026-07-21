import json
from pydantic import BaseModel

from app.llm_client import LLMClient
from app.prompt_loader import PromptConfig


class ClassificationResult(BaseModel):

    category: str

    summary: str



class EmailClassifier:


    def __init__(
        self,
        prompt: PromptConfig
    ):

        self.prompt = prompt
        self.llm = LLMClient()



    def classify(
        self,
        email: str
    ) -> ClassificationResult:


        response = self.llm.generate(

            system_prompt=self.prompt.system_prompt,

            user_prompt=f"""
Classify this customer email:

{email}

Return only JSON.
"""
        )


        try:

            data = json.loads(response)


        except json.JSONDecodeError:

            raise ValueError(
                f"LLM returned invalid JSON:\n{response}"
            )


        return ClassificationResult(
            **data
        )