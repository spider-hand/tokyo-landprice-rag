# ruff: noqa: E402

# Add the project root directory to sys.path so that modules under
# `server/` can be imported when running this script from `scripts/`Ï
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Load environment variables instead of using secrets manager
from dotenv import load_dotenv

load_dotenv(".env.localstack")

from ragas import evaluate as ragas_evaluate
from ragas.metrics import _faithfulness, _answer_relevancy
from ragas import EvaluationDataset, SingleTurnSample
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from server.src.core.openai import embed, extract_intent, generate_with_llm
from server.src.core.qdrant import build_filter, retrieve_contexts
from typing import TypedDict

# Configuration
llm = LangchainLLMWrapper(ChatOpenAI(model="gpt-4o-mini"))
embeddings = LangchainEmbeddingsWrapper(
    OpenAIEmbeddings(model="text-embedding-3-small")
)

TEST_QUESTIONS = [
    "Which areas in Tokyo have the highest land prices?",
    "Where are good residential areas near Shibuya?",
]


class PipelineResult(TypedDict):
    question: str
    contexts: list[str]
    response: str


def run_pipeline(question: str) -> PipelineResult:
    intent = extract_intent(question)
    query_filter = build_filter(intent)
    vector = embed(question)
    result = retrieve_contexts(vector, query_filter)
    response = generate_with_llm(question, result.contexts)

    return {
        "question": question,
        "contexts": result.contexts,
        "response": response,
    }


def evaluate():
    samples = []

    for question in TEST_QUESTIONS:
        result = run_pipeline(question)
        sample = SingleTurnSample(
            user_input=result["question"],
            response=result["response"],
            retrieved_contexts=result["contexts"],
        )
        samples.append(sample)

    dataset = EvaluationDataset(samples=samples)
    results = ragas_evaluate(
        dataset=dataset,
        metrics=[_faithfulness, _answer_relevancy],
        llm=llm,
        embeddings=embeddings,
    )

    return results


def main():
    results = evaluate()
    print(results)


if __name__ == "__main__":
    main()
