from __future__ import annotations

from typing import Any

from .citations import citation_ids


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
