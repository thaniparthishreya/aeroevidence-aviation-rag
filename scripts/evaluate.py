from __future__ import annotations

import json
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from aviation_rag.retrieval import HybridIndex


def main() -> None:
    index = HybridIndex.load(Path("data/index/index.json"))
    cases = json.loads(Path("evaluation/questions.json").read_text())
    recalls, reciprocal_ranks, latencies = [], [], []
    failures = []
    for case in cases:
        started = time.perf_counter()
        results = index.search(case["question"], top_k=case.get("top_k", 5), filters=case.get("filters"))
        latencies.append((time.perf_counter() - started) * 1000)
        ids = [result.chunk.document_id for result in results]
        expected = set(case["expected_document_ids"])
        relevant_ranks = [rank for rank, document_id in enumerate(ids, 1) if document_id in expected]
        recalls.append(len(set(ids) & expected) / len(expected))
        reciprocal_ranks.append(1 / min(relevant_ranks) if relevant_ranks else 0)
        if not relevant_ranks:
            failures.append(case["id"])
    report = {
        "cases": len(cases),
        "recall_at_k": round(statistics.mean(recalls), 3),
        "mrr": round(statistics.mean(reciprocal_ranks), 3),
        "p50_latency_ms": round(statistics.median(latencies), 2),
        "max_latency_ms": round(max(latencies), 2),
        "failed_cases": failures,
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
