# Source Dossier: RAG Retrieval Quality Lab

This dossier records architectural inspiration and reuse boundaries for the template.

## Sources Studied

- BEIR: benchmark shape for corpus, queries, qrels, and retrieval evaluation.
- Qdrant: local vector search service and payload filtering.
- Ragas: RAG evaluation metric language such as context precision, recall, and grounding.
- MinIO: S3-compatible object storage simulation.
- Testcontainers and Docker Compose: real local service testing patterns.

## Allowed Reuse

- Architecture ideas.
- Generic benchmark structure.
- Metric names.
- Local service pattern.
- Public API concepts such as vector payload filters and object storage buckets.

## Forbidden

- Copying source code from public repos.
- Copying datasets wholesale.
- Copying private customer code.
- Using live cloud services.
- Requiring credentials.
- Embedding real customer data into fixtures.

All code and fixtures in this template are Translucid-owned synthetic material.
