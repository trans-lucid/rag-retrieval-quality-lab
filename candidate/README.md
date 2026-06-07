# RAG Retrieval Quality Lab

Your support copilot is citing the wrong knowledge-base articles.

The local simulator includes Qdrant, Postgres, MinIO, and a deterministic fake embedding API. Your task is to repair the retrieval path so answers are tenant-scoped, ACL-aware, fresh enough, and backed by citations that map to returned chunks.

## Commands

```bash
make setup
make dev
make seed
make index
make test
make eval
make clean
```

## Main Files

- `src/retriever.py`
- `src/ranker.py`
- `src/citations.py`
- `src/eval_runner.py`

The starter is intentionally flawed. Public tests show the visible contract.
