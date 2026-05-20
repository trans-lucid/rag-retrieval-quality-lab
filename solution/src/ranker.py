from __future__ import annotations

import math
import re
from datetime import date, datetime
from typing import Any


def tokenize(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9]+", text.lower()) if len(token) > 2}


def keyword_overlap(query: str, chunk: dict[str, Any]) -> float:
    query_terms = tokenize(query)
    text_terms = tokenize(f"{chunk.get('title', '')} {chunk.get('text', '')}")
    if not query_terms:
        return 0.0
    return len(query_terms & text_terms) / len(query_terms)


def parse_effective_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def freshness_score(value: str | None, *, today: date = date(2026, 5, 20)) -> float:
    parsed = parse_effective_date(value)
    if parsed is None:
        return 0.05
    age_days = max((today - parsed).days, 0)
    return math.exp(-age_days / 540)


def is_authorized(chunk: dict[str, Any], user_context: dict[str, Any] | None) -> bool:
    if not user_context:
        return False
    if chunk.get("tenant_id") != user_context.get("tenant_id"):
        return False
    required_groups = set(chunk.get("acl_groups") or [])
    user_groups = set(user_context.get("groups") or [])
    return bool(required_groups & user_groups)


def score_chunk(query: str, chunk: dict[str, Any]) -> float:
    semantic = float(chunk.get("score", chunk.get("qdrant_score", 0.0)) or 0.0)
    lexical = keyword_overlap(query, chunk)
    fresh = freshness_score(chunk.get("effective_date"))
    return (0.55 * semantic) + (0.15 * lexical) + (0.30 * fresh)


def rank_chunks(query: str, chunks: list[dict[str, Any]], user_context: dict[str, Any] | None = None, limit: int = 4) -> list[dict[str, Any]]:
    filtered = [chunk for chunk in chunks if is_authorized(chunk, user_context)]
    ranked = sorted(filtered, key=lambda chunk: score_chunk(query, chunk), reverse=True)
    return ranked[:limit]
