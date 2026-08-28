from deepeval.models import OllamaModel
from deepeval.metrics import AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase

from app.config import OLLAMA_HOST, OLLAMA_MODEL


class DeepEvalEvaluator:

    def __init__(self):

        self.model = OllamaModel(
            model=OLLAMA_MODEL,
            base_url=OLLAMA_HOST,
            temperature=0.0,
        )

        self.metric = AnswerRelevancyMetric(
            threshold=0.5,
            model=self.model,
            include_reason=True,
            async_mode=False,
        )

    def evaluate_result(
        self,
        input_text,
        actual_output,
    ):

        test_case = LLMTestCase(
            input=input_text,
            actual_output=actual_output,
        )

        self.metric.measure(test_case)

        return {
            "score": self.metric.score,
            "reason": self.metric.reason,
            "success": self.metric.is_successful(),
        }