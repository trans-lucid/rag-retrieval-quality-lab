from __future__ import annotations

from src.citations import build_answer_package, citation_ids


def test_correct_answer_still_needs_supporting_citation_chunk():
    chunks = [
        {
            "tenant_id": "tenant_alpha",
            "doc_id": "alpha-current-access",
            "chunk_id": "alpha-current-access::chunk-0",
            "title": "Current access recovery",
            "text": "Users recover access through verified email.",
            "effective_date": "2026-05-01",
            "acl_groups": ["support_basic"],
            "score": 0.9,
        }
    ]
    result = build_answer_package("How do users recover access?", chunks)
    returned = {chunk["chunk_id"] for chunk in result["chunks"]}
    assert result["citations"]
    assert citation_ids(result).issubset(returned)
    assert all(citation.get("supporting_text") for citation in result["citations"])


def test_overbroad_retrieval_is_limited_for_precision_budget():
    chunks = [
        {
            "tenant_id": "tenant_alpha",
            "doc_id": f"alpha-doc-{index}",
            "chunk_id": f"alpha-doc-{index}::chunk-0",
            "title": f"Doc {index}",
            "text": "Account recovery support text.",
            "effective_date": "2026-05-01",
            "acl_groups": ["support_basic"],
            "score": 0.9 - (index / 100),
        }
        for index in range(10)
    ]
    result = build_answer_package("account recovery", chunks[:4])
    assert len(result["chunks"]) <= 4
    assert len(result["citations"]) <= 3
