from __future__ import annotations

import os
import sys
from pathlib import Path


TARGET = os.environ.get("EVAL_TARGET")
if TARGET:
    sys.path.insert(0, str(Path(TARGET).resolve()))

from src.citations import build_answer_package, citation_ids
from src.ranker import rank_chunks


def sample_chunks():
    return [
        {
            "tenant_id": "tenant_alpha",
            "doc_id": "alpha-password-legacy",
            "chunk_id": "alpha-password-legacy::chunk-0",
            "title": "Password reset keywords legacy notice",
            "text": "Legacy password reset instructions with exact reset password keywords.",
            "effective_date": "2024-01-10",
            "acl_groups": ["support_basic", "support_admin"],
            "score": 0.91,
        },
        {
            "tenant_id": "tenant_alpha",
            "doc_id": "alpha-password-current",
            "chunk_id": "alpha-password-current::chunk-0",
            "title": "Current account access recovery",
            "text": "Current guidance for recovering account access through verified email.",
            "effective_date": "2026-04-15",
            "acl_groups": ["support_basic", "support_admin"],
            "score": 0.89,
        },
        {
            "tenant_id": "tenant_beta",
            "doc_id": "beta-password-private",
            "chunk_id": "beta-password-private::chunk-0",
            "title": "Password reset premium playbook",
            "text": "Tenant beta private password reset operating steps.",
            "effective_date": "2026-05-01",
            "acl_groups": ["support_basic", "support_admin"],
            "score": 0.95,
        },
    ]


def test_result_schema_valid():
    ranked = rank_chunks(
        "password reset",
        sample_chunks(),
        user_context={"tenant_id": "tenant_alpha", "groups": ["support_basic"]},
    )
    result = build_answer_package("password reset", ranked)
    assert isinstance(result["answer"], str)
    assert isinstance(result["chunks"], list)
    assert isinstance(result["citations"], list)


def test_obvious_tenant_filter_contract():
    ranked = rank_chunks(
        "password reset",
        sample_chunks(),
        user_context={"tenant_id": "tenant_alpha", "groups": ["support_basic"]},
    )
    leaked = [chunk["doc_id"] for chunk in ranked if chunk["tenant_id"] != "tenant_alpha"]
    assert not leaked, f"tenant_leak_detected: returned cross-tenant docs {leaked}"


def test_freshness_beats_stale_keyword_trap():
    ranked = rank_chunks(
        "password reset account access",
        sample_chunks(),
        user_context={"tenant_id": "tenant_alpha", "groups": ["support_basic"]},
    )
    assert ranked[0]["doc_id"] == "alpha-password-current", (
        "stale_doc_ranked_first: current account access recovery should outrank the legacy keyword-heavy article"
    )


def test_citations_map_to_returned_chunks():
    ranked = rank_chunks(
        "password reset account access",
        sample_chunks()[:2],
        user_context={"tenant_id": "tenant_alpha", "groups": ["support_basic"]},
    )
    result = build_answer_package("password reset account access", ranked)
    returned_chunk_ids = {chunk["chunk_id"] for chunk in result["chunks"]}
    assert citation_ids(result).issubset(returned_chunk_ids), (
        "missing_grounded_citation: every citation chunk_id must map to a returned chunk"
    )
