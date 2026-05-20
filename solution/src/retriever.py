from __future__ import annotations

from typing import Any

from .citations import build_answer_package
from .ranker import rank_chunks


def retrieve_from_chunks(
    query: str,
    chunks: list[dict[str, Any]],
    *,
    tenant_id: str,
    user_id: str,
    groups: list[str],
    limit: int = 4,
) -> dict[str, Any]:
    user_context = {"tenant_id": tenant_id, "user_id": user_id, "groups": groups}
    ranked = rank_chunks(query, chunks, user_context=user_context, limit=limit)
    result = build_answer_package(query, ranked)
    result["tenant_id"] = tenant_id
    result["user_id"] = user_id
    return result
