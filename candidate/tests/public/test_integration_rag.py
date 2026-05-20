from __future__ import annotations

from src.citations import citation_ids
from src.retriever import retrieve


def test_public_docker_rag_path_enforces_tenant_freshness_and_citations():
    result = retrieve(
        "How should I help an alpha customer recover account access when they ask about password reset?",
        tenant_id="tenant_alpha",
        user_id="user_alpha_basic",
    )

    chunks = result["chunks"]
    doc_ids = [chunk["doc_id"] for chunk in chunks]
    tenant_ids = {chunk["tenant_id"] for chunk in chunks}
    returned_chunk_ids = {chunk["chunk_id"] for chunk in chunks}

    assert tenant_ids <= {"tenant_alpha"}, f"tenant_leak_detected: returned tenants {tenant_ids}"
    assert "beta-password-private" not in doc_ids, "tenant_leak_detected: returned tenant_beta private document"
    assert doc_ids[:1] == ["alpha-password-current"], (
        f"stale_doc_ranked_first: expected alpha-password-current first, got {doc_ids[:1]}"
    )
    assert citation_ids(result).issubset(returned_chunk_ids), (
        "missing_grounded_citation: citations must reference returned chunks"
    )
