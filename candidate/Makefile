PYTHON ?= python3

.PHONY: dev logs seed index test test-unit test-integration eval clean

dev:
	docker compose up -d

logs:
	docker compose logs -f

seed:
	$(PYTHON) -m src.metadata_store migrate
	$(PYTHON) -m src.storage seed
	$(PYTHON) -m src.indexer --fixture fixtures/public/documents.jsonl

index:
	$(PYTHON) -m src.indexer --fixture fixtures/public/documents.jsonl

test:
	$(PYTHON) -m pytest tests/public

test-unit:
	$(PYTHON) -m pytest tests/public/test_unit_contract.py

test-integration:
	$(PYTHON) -m pytest tests/public/test_integration_rag.py

eval:
	$(PYTHON) -m src.eval_runner --queries fixtures/public/queries.jsonl --out results/retrieval_report.json

clean:
	docker compose down -v
