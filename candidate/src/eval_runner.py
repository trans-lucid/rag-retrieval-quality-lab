from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .citations import citation_ids
from .metadata_store import record_eval_run
from .report import write_summary
from .retriever import retrieve


def load_queries(path: str | Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


def evaluate_result(query_case: dict[str, Any], result: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    chunks = result.get("chunks", [])
    doc_ids = [chunk.get("doc_id") for chunk in chunks]
    tenant_ids = {chunk.get("tenant_id") for chunk in chunks}
    returned_chunk_ids = {chunk.get("chunk_id") for chunk in chunks}

    if any(tenant != query_case["tenant_id"] for tenant in tenant_ids):
        reasons.append("tenant_leak_detected")
    if query_case.get("expected_top_doc_id") and doc_ids[:1] != [query_case["expected_top_doc_id"]]:
        reasons.append("stale_doc_ranked_first")
    if not citation_ids(result) or not citation_ids(result).issubset(returned_chunk_ids):
        reasons.append("missing_grounded_citation")
    for forbidden in query_case.get("forbidden_doc_ids", []):
        if forbidden in doc_ids:
            reasons.append("tenant_leak_detected")
    return sorted(set(reasons))


def run_eval(queries_path: str | Path, out: str | Path) -> dict[str, Any]:
    cases = load_queries(queries_path)
    results = []
    all_failures: list[str] = []
    for case in cases:
        result = retrieve(case["query"], tenant_id=case["tenant_id"], user_id=case["user_id"])
        failures = evaluate_result(case, result)
        all_failures.extend(failures)
        results.append({"query_id": case["query_id"], "failures": failures, "result": result})

    report = {
        "summary": {
            "queries": len(results),
            "passed": sum(1 for result in results if not result["failures"]),
            "failed": sum(1 for result in results if result["failures"]),
            "failure_reasons": sorted(set(all_failures)),
        },
        "results": results,
    }
    output = Path(out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2))
    write_summary(report)
    record_eval_run("public", report["summary"])
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--queries", default="fixtures/public/queries.jsonl")
    parser.add_argument("--out", default="results/retrieval_report.json")
    args = parser.parse_args()
    report = run_eval(args.queries, args.out)
    print(json.dumps(report["summary"], indent=2))


if __name__ == "__main__":
    main()
