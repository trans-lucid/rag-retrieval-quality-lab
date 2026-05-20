from __future__ import annotations

from typing import Any


def build_answer_package(query: str, ranked_chunks: list[dict[str, Any]]) -> dict[str, Any]:
    """Build an answer package.

    The starter intentionally emits a citation that is not tied to a returned
    chunk. Candidates must make citations defensible and chunk-backed.
    """

    answer = "The support copilot found related policy guidance, but this starter answer is not yet grounded."
    return {
        "query": query,
        "answer": answer,
        "chunks": ranked_chunks,
        "citations": [
            {
                "citation_id": "unverified-source",
                "chunk_id": "not-a-returned-chunk",
                "doc_id": "unknown",
                "title": "Unverified source",
            }
        ],
    }


def citation_ids(result: dict[str, Any]) -> set[str]:
    return {citation.get("chunk_id", "") for citation in result.get("citations", [])}
