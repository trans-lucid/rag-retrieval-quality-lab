from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from .retriever import retrieve


class SearchRequest(BaseModel):
    query: str
    tenant_id: str
    user_id: str


app = FastAPI(title="RAG Retrieval Quality Lab")


@app.post("/search")
def search(request: SearchRequest):
    return retrieve(request.query, tenant_id=request.tenant_id, user_id=request.user_id)
