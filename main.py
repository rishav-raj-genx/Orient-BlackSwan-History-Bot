import os
import sys
import traceback
import warnings

# Suppress library deprecation and info warnings for screenshot clarity
os.environ["TOKENIZERS_PARALLELISM"] = "false"
warnings.filterwarnings("ignore")

from typing import List
from src.rag_pipeline import ask_question, init_rag_chain

TEST_QUESTIONS: List[str] = [
    "On what date were the prices in this catalogue last updated?",
    "In which year was the publisher (Orient BlackSwan) incorporated?",
    "What is the price of a Physics textbook?",
    "Who is the current Minister of Education?",
    'Which is the "best" history book for a beginner?',
]

SEPARATOR: str = "-" * 50


def run_benchmark() -> None:
    # Warm up RAG chain so initial model load and diagnostics finish before test output
    init_rag_chain()

    print("\nStarting RAG benchmark evaluation...")
    print(SEPARATOR)

    for idx, question in enumerate(TEST_QUESTIONS, start=1):
        print(f"Question: {question}")
        try:
            answer = ask_question(question)
            print(f"Answer: {answer}")
        except Exception:
            print("Answer: [EXECUTION ERROR]")
            print(f"Traceback for question {idx}:", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
        print(SEPARATOR)


if __name__ == "__main__":
    run_benchmark()
