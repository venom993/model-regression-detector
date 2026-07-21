from app.prompt_loader import PromptLoader
from app.classifier import EmailClassifier



loader = PromptLoader()

prompt = loader.load("1")


classifier = EmailClassifier(
    prompt
)



email = """
I was charged twice for my monthly subscription.
Please refund the extra payment.
"""


result = classifier.classify(email)


print(result)