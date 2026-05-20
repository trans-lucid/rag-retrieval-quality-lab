from __future__ import annotations

import argparse
import hashlib
import json
import time
import uuid
from pathlib import Path
from typing import Any

import requests

from .config import get_settings
from .embedding_client import embed_text
from .metadata_store import migrate, seed_tenants, upsert_document_metadata


def wait_for_qdrant(retries: int = 30) -> None:
    settings = get_settings()
    last_error: Exception | None = None
    for _ in range(retries):
        try:
            response = requests.get(f"{settings.qdrant_url}/collections", timeout=5)
            response.raise_for_status()
            return
        except Exception as exc:  # pragma: no cover - integration retry path
            last_error = exc
            time.sleep(1)
    raise RuntimeError(f"qdrant did not become ready: {last_error}")


def point_id(value: str) -> str:
    return str(uuid.UUID(hashlib.md5(value.encode("utf-8")).hexdigest()))


def create_collection() -> None:
    settings = get_settings()
    wait_for_qdrant()
    response = requests.put(
        f"{settings.qdrant_url}/collections/{settings.qdrant_collection}",
        json={"vectors": {"size": settings.vector_size, "distance": "Cosine"}},
        timeout=10,
    )
    if response.status_code == 409:
        return
    response.raise_for_status()


def iter_documents(fixture: str | Path) -> list[dict[str, Any]]:
    documents: list[dict[str, Any]] = []
    for line in Path(fixture).read_text().splitlines():
        if line.strip():
            documents.append(json.loads(line))
    return documents


def chunk_document(document: dict[str, Any]) -> dict[str, Any]:
    chunk_id = f"{document['doc_id']}::chunk-0"
    return {
        "tenant_id": document["tenant_id"],
        "doc_id": document["doc_id"],
        "chunk_id": chunk_id,
        "title": document["title"],
        "text": document["body"],
        "effective_date": document.get("effective_date"),
        "acl_groups": document.get("acl_groups", []),
        "object_key": document["object_key"],
    }


def index_documents(fixture: str | Path = "fixtures/public/documents.jsonl") -> None:
    settings = get_settings()
    migrate()
    seed_tenants("fixtures/public/tenants.json")
    create_collection()

    points = []
    for document in iter_documents(fixture):
        upsert_document_metadata(document)
        chunk = chunk_document(document)
        vector = embed_text(f"{chunk['title']}\n{chunk['text']}")
        points.append({"id": point_id(chunk["chunk_id"]), "vector": vector, "payload": chunk})

    response = requests.put(
        f"{settings.qdrant_url}/collections/{settings.qdrant_collection}/points?wait=true",
        json={"points": points},
        timeout=30,
    )
    response.raise_for_status()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", default="fixtures/public/documents.jsonl")
    args = parser.parse_args()
    index_documents(args.fixture)


if __name__ == "__main__":
    main()
