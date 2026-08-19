"""
eval_groundedness.py - ShopSense M4
LLM-as-judge groundedness evaluation.

Groundedness: "Is every factual claim in the answer supported by the retrieved context?"
- Score 1 = fully grounded (no fabrication)
- Score 0 = fabricated info (invented return window / refund amount)

Logs scores to Langfuse for tracking.

Run: python eval_groundedness.py
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from langfuse import Langfuse
from litellm import completion

from rag_query import answer_with_rag, format_context
from retriever import HybridRetriever, RetrievedChunk

load_dotenv()

GOLDEN_SET_PATH = Path(__file__).parent / "golden_set.json"
LLM_MODEL = os.getenv("LLM_MODEL") or os.getenv("GROQ_MODEL") or "groq/llama-3.1-8b-instant"

GROUNDEDNESS_PROMPT = """\
You are an evaluator checking if an AI assistant's answer is grounded in the
provided context.

CONTEXT (retrieved policy excerpts):
{context}

QUESTION:
{question}

ANSWER TO EVALUATE:
{answer}

TASK:
Determine if every factual claim in the answer (return windows, refund amounts,
timeframes, conditions) is explicitly supported by the context above.

Respond with ONLY a JSON object:
{{
  "grounded": true or false,
  "score": 1 or 0,
  "reason": "one sentence explanation"
}}

Return ONLY valid JSON, no markdown fences."""


def eval_groundedness(
    question: str,
    answer: str,
    chunks: list[RetrievedChunk],
) -> dict:
    """Judge if an answer is grounded in the retrieved chunks."""
    context = format_context(chunks)
    prompt = GROUNDEDNESS_PROMPT.format(
        context=context,
        question=question,
        answer=answer,
    )
    resp = completion(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        response_format={"type": "json_object"},
    )
    raw = resp.choices[0].message.content
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"grounded": False, "score": 0, "reason": f"parse error: {raw[:100]}"}


def run_eval(golden_set: list[dict], langfuse: Langfuse | None = None) -> dict:
    """Run groundedness eval over a golden set and log to Langfuse."""
    retriever = HybridRetriever()

    scores = []
    results = []

    for i, case in enumerate(golden_set):
        question = case["question"]
        print(f"\n[{i + 1}/{len(golden_set)}] {question[:70]}...")

        rag_result = answer_with_rag(question, retriever)
        answer = rag_result["answer"]
        chunks = rag_result["chunks"]

        eval_result = eval_groundedness(question, answer, chunks)
        score = eval_result.get("score", 0)
        scores.append(score)

        print(f"  grounded={eval_result.get('grounded')} | score={score}")
        print(f"  reason: {eval_result.get('reason', '')}")

        if langfuse:
            trace = langfuse.trace(
                name="groundedness_eval",
                input={"question": question},
                output={"answer": answer, "score": score},
            )
            langfuse.score(
                trace_id=trace.id,
                name="groundedness",
                value=score,
                comment=eval_result.get("reason", ""),
            )

        results.append(
            {
                "question": question,
                "answer": answer,
                "grounded": eval_result.get("grounded"),
                "score": score,
                "reason": eval_result.get("reason", ""),
            }
        )

    avg_score = sum(scores) / len(scores) if scores else 0.0
    summary = {
        "total": len(scores),
        "grounded": sum(scores),
        "avg_score": round(avg_score, 3),
        "results": results,
    }

    print("\n" + "=" * 60)
    print(f"Groundedness: {sum(scores)}/{len(scores)} grounded  (avg={avg_score:.2f})")

    return summary


def main():
    if not GOLDEN_SET_PATH.exists():
        print(f"Golden set not found: {GOLDEN_SET_PATH}")
        print("Creating a minimal example golden set...")
        example = [
            {"question": "What is the return window for electronics?"},
            {"question": "Can I get a refund after 30 days?"},
            {"question": "What items are non-returnable?"},
            {"question": "How long does shipping take for standard orders?"},
            {"question": "What is the refund policy for damaged items?"},
        ]
        GOLDEN_SET_PATH.write_text(json.dumps(example, indent=2), encoding="utf-8")
        print(f"Created: {GOLDEN_SET_PATH}")

    golden_set = json.loads(GOLDEN_SET_PATH.read_text(encoding="utf-8"))
    print(f"Loaded {len(golden_set)} eval cases")

    langfuse = None
    if os.getenv("LANGFUSE_PUBLIC_KEY"):
        langfuse = Langfuse(
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            host=os.getenv("LANGFUSE_HOST", os.getenv("LANGFUSE_BASE_URL", "https://cloud.langfuse.com")),
        )

    summary = run_eval(golden_set, langfuse)

    out_path = Path(__file__).parent / "eval_results.json"
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\nResults saved: {out_path}")

    if langfuse:
        langfuse.flush()


if __name__ == "__main__":
    main()
