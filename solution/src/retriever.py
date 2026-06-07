from __future__ import annotations

from typing import Any

import requests

from .citations import build_answer_package
from .config import get_settings
from .embedding_client import embed_text
from .metadata_store import get_user_context
from .ranker import rank_chunks


def _qdrant_search(query: str, limit: int = 12) -> list[dict[str, Any]]:
    settings = get_settings()
    vector = embed_text(query)
    response = requests.post(
        f"{settings.qdrant_url}/collections/{settings.qdrant_collection}/points/search",
        json={"vector": vector, "limit": limit, "with_payload": True},
        timeout=10,
    )
    response.raise_for_status()
    chunks = []
    for item in response.json().get("result", []):
        payload = item.get("payload", {})
        payload["score"] = item.get("score", 0.0)
        chunks.append(payload)
    return chunks


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


def retrieve(query: str, *, tenant_id: str, user_id: str, limit: int = 4) -> dict[str, Any]:
    user_context = get_user_context(user_id)
    user_context["tenant_id"] = tenant_id
    raw_chunks = _qdrant_search(query)
    ranked = rank_chunks(query, raw_chunks, user_context=user_context, limit=limit)
    result = build_answer_package(query, ranked)
    result["tenant_id"] = tenant_id
    result["user_id"] = user_id
    return result
