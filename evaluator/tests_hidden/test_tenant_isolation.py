from __future__ import annotations

from src.ranker import rank_chunks
from src.retriever import retrieve_from_chunks


def collision_chunks():
    return [
        {
            "tenant_id": "tenant_alpha",
            "doc_id": "alpha-billing-current",
            "chunk_id": "alpha-billing-current::chunk-0",
            "title": "Atlas billing export",
            "text": "Alpha users export invoices from Workspace Billing.",
            "effective_date": "2026-02-11",
            "acl_groups": ["support_basic"],
            "score": 0.88,
        },
        {
            "tenant_id": "tenant_beta",
            "doc_id": "beta-billing-secret",
            "chunk_id": "beta-billing-secret::chunk-0",
            "title": "Atlas billing export",
            "text": "Beta private billing export runbook with privileged tenant-only steps.",
            "effective_date": "2026-05-08",
            "acl_groups": ["support_basic"],
            "score": 0.99,
        },
    ]


def test_same_product_name_does_not_cross_tenant():
    result = retrieve_from_chunks(
        "How do I export Atlas billing data?",
        collision_chunks(),
        tenant_id="tenant_alpha",
        user_id="hidden-alpha-basic",
        groups=["support_basic"],
    )
    doc_ids = [chunk["doc_id"] for chunk in result["chunks"]]
    assert doc_ids == ["alpha-billing-current"]
    assert "beta-billing-secret" not in doc_ids


def test_acl_collision_blocks_admin_only_doc():
    chunks = collision_chunks() + [
        {
            "tenant_id": "tenant_alpha",
            "doc_id": "alpha-admin-billing",
            "chunk_id": "alpha-admin-billing::chunk-0",
            "title": "Admin billing override",
            "text": "Only support_admin users can override invoices and credits.",
            "effective_date": "2026-05-01",
            "acl_groups": ["support_admin"],
            "score": 0.98,
        }
    ]
    ranked = rank_chunks(
        "override invoices and credits",
        chunks,
        user_context={"tenant_id": "tenant_alpha", "groups": ["support_basic"]},
    )
    assert all("support_admin" not in chunk["acl_groups"] for chunk in ranked)
