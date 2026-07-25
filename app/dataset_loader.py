import json
from pathlib import Path


class DatasetLoader:

    def __init__(
        self,
        dataset_path="datasets/golden_dataset_v1.json"
    ):
        self.dataset_path = Path(dataset_path)


    def load(self):

        with open(
            self.dataset_path,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)