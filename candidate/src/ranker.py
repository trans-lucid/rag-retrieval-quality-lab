from __future__ import annotations

import re
from typing import Any


def tokenize(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9]+", text.lower()) if len(token) > 2}


def keyword_overlap(query: str, chunk: dict[str, Any]) -> int:
    query_terms = tokenize(query)
    text_terms = tokenize(f"{chunk.get('title', '')} {chunk.get('text', '')}")
    return len(query_terms & text_terms)


def rank_chunks(query: str, chunks: list[dict[str, Any]], user_context: dict[str, Any] | None = None, limit: int = 4) -> list[dict[str, Any]]:
    """Starter ranking is intentionally flawed.

    It overweights lexical overlap, ignores freshness, and does not filter by
    tenant or ACL group. The public and hidden tests are expected to catch this.
    """

    ranked = sorted(
        chunks,
        key=lambda chunk: (keyword_overlap(query, chunk), chunk.get("score", 0.0)),
        reverse=True,
    )
    return ranked[:limit]
