from __future__ import annotations

import hashlib
import math
import re

from fastapi import FastAPI
from pydantic import BaseModel


VECTOR_SIZE = 16
app = FastAPI(title="Fake Embedding API")


class EmbedRequest(BaseModel):
    text: str


def token_vector(text: str) -> list[float]:
    vector = [0.0 for _ in range(VECTOR_SIZE)]
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = digest[0] % VECTOR_SIZE
        sign = 1.0 if digest[1] % 2 == 0 else -1.0
        vector[index] += sign * (1.0 + min(len(token), 12) / 12.0)
    norm = math.sqrt(sum(value * value for value in vector)) or 1.0
    return [round(value / norm, 6) for value in vector]


@app.post("/embed")
def embed(request: EmbedRequest):
    return {"vector": token_vector(request.text)}


@app.get("/healthz")
def healthz():
    return {"ok": True}
