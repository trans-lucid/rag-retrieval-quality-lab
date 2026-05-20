from __future__ import annotations

from typing import Any


def build_answer_package(query: str, ranked_chunks: list[dict[str, Any]]) -> dict[str, Any]:
    citations = []
    for index, chunk in enumerate(ranked_chunks[:3], start=1):
        citations.append(
            {
                "citation_id": f"c{index}",
                "chunk_id": chunk["chunk_id"],
                "doc_id": chunk["doc_id"],
                "title": chunk["title"],
                "supporting_text": chunk["text"][:240],
            }
        )
    if ranked_chunks:
        answer = f"Use the current guidance from {ranked_chunks[0]['title']} and verify the user's tenant context before acting."
    else:
        answer = "No accessible document supports an answer for this user and tenant."
    return {"query": query, "answer": answer, "chunks": ranked_chunks, "citations": citations}


def citation_ids(result: dict[str, Any]) -> set[str]:
    return {citation.get("chunk_id", "") for citation in result.get("citations", [])}
