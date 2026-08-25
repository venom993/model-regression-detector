import time

from app.classifier import EmailClassifier
from app.prompt_loader import PromptLoader
from app.dataset_loader import DatasetLoader
from app.semantic import SemanticSimilarity


class Evaluator:


    def __init__(self):

        loader = PromptLoader()

        self.prompt = loader.load("2")

        self.classifier = EmailClassifier(
            self.prompt
        )

        self.dataset_loader = DatasetLoader()
        self.semantic_similarity = SemanticSimilarity()


    def run(self):

        dataset = self.dataset_loader.load()

        results = []


        for item in dataset:

            print(
                f"Testing {item['id']}..."
            )


            start = time.time()


            try:

                prediction = self.classifier.classify(
                    item["input"]
                )


                latency = round(
                    time.time() - start,
                    3
                )
                summary_similarity = (
    self.semantic_similarity.calculate(
        item["expected_output"]["summary"],
        prediction.summary
    )
)


                results.append({

                    "id": item["id"],

                    "expected_category":
                    item["expected_output"]["category"],

                    "predicted_category":
                    prediction.category,

                    "expected_summary":
                    item["expected_output"]["summary"],

                    "summary_similarity":
                    summary_similarity,

                    "predicted_summary":
                    prediction.summary,

                    "latency":
                    latency,

                    "status":
                    "passed"
                    if prediction.category ==
                    item["expected_output"]["category"]
                    else
                    "failed"

                })


            except Exception as e:


                results.append({

                    "id": item["id"],

                    "error": str(e),

                    "status":
                    "error"

                })


        return results