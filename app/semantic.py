import re


class SemanticSimilarity:

    def tokenize(self, text):

        if not text:
            return set()

        words = re.findall(
            r"\b[a-zA-Z]+\b",
            text.lower()
        )

        return set(words)

    def calculate(
        self,
        expected_summary,
        predicted_summary
    ):

        expected_words = self.tokenize(
            expected_summary
        )

        predicted_words = self.tokenize(
            predicted_summary
        )

        if (
            not expected_words
            or not predicted_words
        ):
            return 0.0

        intersection = (
            expected_words
            & predicted_words
        )

        union = (
            expected_words
            | predicted_words
        )

        similarity = (
            len(intersection)
            / len(union)
        )

        return round(
            similarity,
            3
        )