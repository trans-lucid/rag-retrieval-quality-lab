from __future__ import annotations

import time
from typing import Sequence

import requests

from .config import get_settings


def embed_text(text: str, *, retries: int = 30) -> list[float]:
    settings = get_settings()
    last_error: Exception | None = None
    for _ in range(retries):
        try:
            response = requests.post(settings.embedding_url, json={"text": text}, timeout=5)
            response.raise_for_status()
            vector = response.json()["vector"]
            return [float(value) for value in vector]
        except Exception as exc:  # pragma: no cover - exercised by integration retry path
            last_error = exc
            time.sleep(1)
    raise RuntimeError(f"embedding API did not become ready: {last_error}")


def cosine_hint(query_vector: Sequence[float], chunk_vector: Sequence[float]) -> float:
    dot = sum(a * b for a, b in zip(query_vector, chunk_vector))
    left = sum(a * a for a in query_vector) ** 0.5
    right = sum(b * b for b in chunk_vector) ** 0.5
    if left == 0 or right == 0:
        return 0.0
    return dot / (left * right)
