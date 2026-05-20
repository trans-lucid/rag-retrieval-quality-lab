from __future__ import annotations

from src.citations import citation_ids
from src.retriever import retrieve_from_chunks


def test_changed_ids_and_wording_do_not_break_behavior():
    chunks = [
        {
            "tenant_id": "tenant_delta",
            "doc_id": "delta-workspace-current",
            "chunk_id": "delta-workspace-current::chunk-0",
            "title": "Workspace recovery",
            "text": "Members regain workspace access through identity verification and an email confirmation link.",
            "effective_date": "2026-05-09",
            "acl_groups": ["support_basic"],
            "score": 0.87,
        },
        {
            "tenant_id": "tenant_other",
            "doc_id": "other-workspace-private",
            "chunk_id": "other-workspace-private::chunk-0",
            "title": "Workspace recovery",
            "text": "Other tenant private access recovery runbook.",
            "effective_date": "2026-05-10",
            "acl_groups": ["support_basic"],
            "score": 0.99,
        },
    ]
    result = retrieve_from_chunks(
        "A member is locked out of the workspace; what current recovery guidance applies?",
        chunks,
        tenant_id="tenant_delta",
        user_id="delta-basic",
        groups=["support_basic"],
    )
    assert [chunk["doc_id"] for chunk in result["chunks"]] == ["delta-workspace-current"]
    assert citation_ids(result) == {"delta-workspace-current::chunk-0"}
