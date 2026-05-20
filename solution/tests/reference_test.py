from __future__ import annotations

from src.citations import citation_ids
from src.ranker import rank_chunks
from src.retriever import retrieve_from_chunks


def chunks():
    return [
        {
            "tenant_id": "tenant_alpha",
            "doc_id": "alpha-password-legacy",
            "chunk_id": "alpha-password-legacy::chunk-0",
            "title": "Password reset keywords legacy notice",
            "text": "Legacy reset password reset password reset password process.",
            "effective_date": "2024-01-10",
            "acl_groups": ["support_basic"],
            "score": 0.90,
        },
        {
            "tenant_id": "tenant_alpha",
            "doc_id": "alpha-password-current",
            "chunk_id": "alpha-password-current::chunk-0",
            "title": "Current account access recovery",
            "text": "Recover account access through verified email and security settings.",
            "effective_date": "2026-04-15",
            "acl_groups": ["support_basic"],
            "score": 0.89,
        },
        {
            "tenant_id": "tenant_beta",
            "doc_id": "beta-password-private",
            "chunk_id": "beta-password-private::chunk-0",
            "title": "Password reset premium playbook",
            "text": "Private tenant beta password reset steps.",
            "effective_date": "2026-05-01",
            "acl_groups": ["support_basic"],
            "score": 0.99,
        },
    ]


def test_reference_filters_and_ranks():
    ranked = rank_chunks(
        "password reset account access",
        chunks(),
        user_context={"tenant_id": "tenant_alpha", "groups": ["support_basic"]},
    )
    assert [chunk["doc_id"] for chunk in ranked] == ["alpha-password-current", "alpha-password-legacy"]


def test_reference_citations_are_grounded():
    result = retrieve_from_chunks(
        "password reset account access",
        chunks(),
        tenant_id="tenant_alpha",
        user_id="user_alpha_basic",
        groups=["support_basic"],
    )
    returned_ids = {chunk["chunk_id"] for chunk in result["chunks"]}
    assert citation_ids(result).issubset(returned_ids)
    assert result["citations"]
