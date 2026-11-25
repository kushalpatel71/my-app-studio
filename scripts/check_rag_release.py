"""Repeatable retrieval evaluation; hosted checks require an explicit bounded flag."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import time

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.rag_store import RagStore  # noqa: E402


def rank_metrics(hits, expected):
    """Source hit and reciprocal rank; no fabricated gold chunk/answer scores."""
    if not expected:
        return {"hit_at_1": None, "hit_at_3": None, "reciprocal_rank": None}
    ranks = [i for i, p in enumerate(hits, 1) if p["source_id"] in expected]
    return {
        "hit_at_1": bool(ranks and ranks[0] == 1),
        "hit_at_3": bool(ranks),
        "reciprocal_rank": 1 / ranks[0] if ranks else 0,
        "expected_source_coverage_at_3": len(
            {p["source_id"] for p in hits} & set(expected)
        )
        / len(expected),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--hosted-origin", help="Explicit real hosted calls; never sends a key"
    )
    parser.add_argument("--delay", type=float, default=13)
    args = parser.parse_args()
    if args.hosted_origin and (
        not args.hosted_origin.startswith("https://") or args.delay < 13
    ):
        parser.error(
            "Hosted evaluation requires HTTPS and at least 13 seconds between questions."
        )
    questions = json.loads((ROOT / "docs/rag/review3/questions.json").read_text())
    index = RagStore(args.index)
    report = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "revision": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "working_tree_dirty": bool(
            subprocess.check_output(
                ["git", "status", "--porcelain"], cwd=ROOT, text=True
            ).strip()
        ),
        "import": index.ingest(),
        "repeat_import": index.ingest(),
        "generation_target": args.hosted_origin or "not-executed",
        "maximum_hosted_requests": 8,
        "evaluation": [],
    }
    fields = ("id", "source_id", "version", "score", "metric", "location")
    calls = 0
    with httpx.Client(timeout=30, follow_redirects=False) as client:
        for case in questions:
            row = dict(case)
            for kind in ["vector", "keyword"]:
                start = time.perf_counter()
                hits = index.retrieve(case["question"], keyword=kind == "keyword")
                row[kind] = {
                    "latency_seconds": round(time.perf_counter() - start, 4),
                    "hits": [{k: p[k] for k in fields} for p in hits],
                    "metrics": rank_metrics(hits, case["expected_sources"]),
                }
            # Offline alternative only: six nearest chunks, then one per source.
            # Production selection remains top-three chunks at cosine >= 0.30.
            start = time.perf_counter()
            collection = index.client.get_collection(
                "snapshot-" + index.active(), embedding_function=None
            )
            candidate = collection.query(
                query_embeddings=index.embedder([case["question"]]),
                n_results=min(6, collection.count()),
            )
            diverse, seen = [], set()
            for ident, distance in zip(candidate["ids"][0], candidate["distances"][0]):
                hit = index.source(ident)
                if hit["source_id"] not in seen and len(diverse) < 3:
                    diverse.append(
                        dict(hit, score=round(1 - distance, 5), metric="cosine")
                    )
                    seen.add(hit["source_id"])
            row["diversified_experiment"] = {
                "latency_seconds": round(time.perf_counter() - start, 4),
                "hits": [{k: p[k] for k in fields} for p in diverse],
                "metrics": rank_metrics(diverse, case["expected_sources"]),
                "production_behavior_changed": False,
            }
            if args.hosted_origin and case.get("hosted") and calls < 8:
                if calls:
                    time.sleep(args.delay)
                calls += 1
                start = time.perf_counter()
                try:
                    response = client.post(
                        args.hosted_origin.rstrip("/") + "/api/rag/ask",
                        json={"question": case["question"]},
                    )
                    data = response.json()
                    live = {
                        "status": response.status_code,
                        "latency_seconds": round(time.perf_counter() - start, 4),
                        "response": data,
                    }
                    if response.status_code == 200:
                        ids = {p["id"] for p in data["trace"] if p["score"] >= 0.30}
                        live["citation_ids_valid"] = all(
                            p["id"] in ids for p in data["citations"]
                        )
                        live["expected_abstention_matches"] = data["insufficient"] == (
                            not case["answerable"]
                        )
                        live["opened_sources"] = [
                            {
                                "id": p["id"],
                                "status": client.get(
                                    args.hosted_origin.rstrip("/") + p["url"]
                                ).status_code,
                            }
                            for p in data["citations"]
                        ]
                        live["claim_support_review"] = (
                            "Pending explicit comparison of answer with opened passages; valid IDs alone are insufficient."
                        )
                    row["hosted"] = live
                except (httpx.HTTPError, ValueError) as error:
                    row["hosted"] = {
                        "status": "transport-error",
                        "type": type(error).__name__,
                    }
            report["evaluation"].append(row)
            # Preserve partial results if interrupted; no hidden retries.
            args.output.write_text(json.dumps(report, indent=2) + "\n")
    report["actual_hosted_requests"] = calls
    report["metrics_note"] = (
        "Source-level retrieval metrics; unsupported cases measure scope-source retrieval, not factual answer correctness. Latency includes cold startup on first vector call."
    )
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(
        json.dumps(
            {
                "output": str(args.output),
                "cases": len(questions),
                "hosted_requests": calls,
                "import": report["import"],
                "repeat_import": report["repeat_import"],
            }
        )
    )


if __name__ == "__main__":
    main()
