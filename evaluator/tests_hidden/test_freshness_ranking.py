from __future__ import annotations

from src.ranker import rank_chunks


def test_fresh_paraphrased_doc_beats_stale_keyword_stuffed_doc():
    chunks = [
        {
            "tenant_id": "tenant_gamma",
            "doc_id": "gamma-legacy-keyword",
            "chunk_id": "gamma-legacy-keyword::chunk-0",
            "title": "Reset password password password",
            "text": "Old reset password password password troubleshooting flow.",
            "effective_date": "2023-08-01",
            "acl_groups": ["support_basic"],
            "score": 0.86,
        },
        {
            "tenant_id": "tenant_gamma",
            "doc_id": "gamma-current-access",
            "chunk_id": "gamma-current-access::chunk-0",
            "title": "Current account recovery",
            "text": "Restore account access through verified identity and email confirmation.",
            "effective_date": "2026-05-10",
            "acl_groups": ["support_basic"],
            "score": 0.84,
        },
    ]
    ranked = rank_chunks(
        "password reset account access",
        chunks,
        user_context={"tenant_id": "tenant_gamma", "groups": ["support_basic"]},
    )
    assert ranked[0]["doc_id"] == "gamma-current-access"


def test_missing_effective_date_does_not_crash_or_win_by_default():
    chunks = [
        {
            "tenant_id": "tenant_gamma",
            "doc_id": "gamma-missing-date",
            "chunk_id": "gamma-missing-date::chunk-0",
            "title": "Current access recovery",
            "text": "Restore account access through support verification.",
            "effective_date": None,
            "acl_groups": ["support_basic"],
            "score": 0.88,
        },
        {
            "tenant_id": "tenant_gamma",
            "doc_id": "gamma-dated-current",
            "chunk_id": "gamma-dated-current::chunk-0",
            "title": "Current access recovery",
            "text": "Restore account access through support verification.",
            "effective_date": "2026-05-12",
            "acl_groups": ["support_basic"],
            "score": 0.88,
        },
    ]
    ranked = rank_chunks(
        "account access recovery",
        chunks,
        user_context={"tenant_id": "tenant_gamma", "groups": ["support_basic"]},
    )
    assert ranked[0]["doc_id"] == "gamma-dated-current"
