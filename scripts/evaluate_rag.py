"""Reproduce retrieval evidence; generation runs only with an explicit flag."""

import argparse
import json
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.rag_store import INDEX_CONFIG, MODEL, RagStore  # noqa: E402
from app.rag_generation import GenerationError, generate  # noqa: E402

QUESTIONS = [
    ("exact", "Where does View Details take me?", "CBP-S01"),
    ("paraphrase", "Where can I look at the upgrades on one example car?", "CBP-S01"),
    ("relationship", "Which role may access the administration page?", "CBP-S04"),
    (
        "ordinary",
        "What does the suspension category describe in this assistant?",
        "CBP-S03",
    ),
    (
        "unanswerable",
        "What measured horsepower gain will this build give my car?",
        "CBP-S05",
    ),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", required=True, type=Path)
    parser.add_argument("--generate", action="store_true")
    args = parser.parse_args()
    index = RagStore(args.index)
    started = time.perf_counter()
    report = {"model": MODEL, "index_config": INDEX_CONFIG, "import": index.ingest()}
    report["repeat_import"] = index.ingest()
    report["evaluation"] = []
    for kind, question, expected in QUESTIONS:
        passages = index.retrieve(question)
        keyword = index.retrieve(question, keyword=True)
        fields = ("id", "source_id", "version", "score", "metric")
        result = {
            "kind": kind,
            "question": question,
            "expected_source": expected,
            "vector": [{k: p[k] for k in fields} for p in passages],
            "keyword": [{k: p[k] for k in fields} for p in keyword],
        }
        if args.generate:
            try:
                result["generation"] = generate(
                    question, [p for p in passages if p["score"] >= 0.30]
                )
            except GenerationError as error:
                result["generation"] = {"status": "unavailable", "detail": str(error)}
        else:
            result["generation"] = {
                "status": "not-executed",
                "reason": "No --generate flag",
            }
        report["evaluation"].append(result)
    report["elapsed_seconds"] = round(time.perf_counter() - started, 3)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
