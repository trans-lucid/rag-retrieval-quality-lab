#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/candidate"

docker compose config >/tmp/rag-retrieval-compose-config.txt
docker compose up -d

cleanup() {
  docker compose down -v
}
trap cleanup EXIT

make seed

set +e
python3 -m pytest tests/public/test_integration_rag.py 2>&1 | tee /tmp/rag-retrieval-integration-output.txt
status=${PIPESTATUS[0]}
set -e

if [ "$status" -eq 0 ]; then
  echo "candidate starter unexpectedly passed the Docker-backed public integration test"
  exit 1
fi

if ! grep -q "test_public_docker_rag_path_enforces_tenant_freshness_and_citations" /tmp/rag-retrieval-integration-output.txt; then
  echo "Docker-backed public integration test did not run"
  exit 1
fi

found=0
for expected in tenant_leak_detected stale_doc_ranked_first missing_grounded_citation; do
  if grep -q "$expected" /tmp/rag-retrieval-integration-output.txt; then
    found=1
  fi
done

if [ "$found" -ne 1 ]; then
  echo "Docker-backed public integration test failed for an unexpected reason"
  exit 1
fi

echo "candidate starter failed Docker-backed public integration test as expected"
