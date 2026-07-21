from pathlib import Path
import yaml
from pydantic import BaseModel


class FewShotExample(BaseModel):
    input: str
    output: dict


class PromptConfig(BaseModel):

    version: str

    created_at: str

    description: str

    system_prompt: str

    few_shot_examples: list[FewShotExample]


class PromptLoader:


    def __init__(self, prompt_directory="prompts"):

        self.prompt_directory = Path(prompt_directory)


    def load(self, version: str) -> PromptConfig:

        file_path = (
            self.prompt_directory
            / f"prompt_v{version}.yaml"
        )


        if not file_path.exists():
            raise FileNotFoundError(
                f"Prompt {version} not found"
            )


        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            data = yaml.safe_load(file)


        return PromptConfig(**data)