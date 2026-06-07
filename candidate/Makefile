PYTHON ?= python3

.PHONY: setup dev logs seed index test test-unit test-integration eval clean

setup:
	$(PYTHON) -m pip install -e .[test]

dev:
	docker compose up -d

logs:
	docker compose logs -f

seed: setup
	$(PYTHON) -m src.metadata_store migrate
	$(PYTHON) -m src.storage seed
	$(PYTHON) -m src.indexer --fixture fixtures/public/documents.jsonl

index: setup
	$(PYTHON) -m src.indexer --fixture fixtures/public/documents.jsonl

test: setup
	$(PYTHON) -m pytest tests/public

test-unit: setup
	$(PYTHON) -m pytest tests/public/test_unit_contract.py

test-integration: setup
	$(PYTHON) -m pytest tests/public/test_integration_rag.py

eval: setup
	$(PYTHON) -m src.eval_runner --queries fixtures/public/queries.jsonl --out results/retrieval_report.json

clean:
	docker compose down -v
