# RAG Retrieval Quality Lab

This is an internal Translucid challenge template repository. It is not a generated candidate challenge.

The template generates RAG/retrieval debugging challenges for AI backend, backend, staff backend, and ML engineering roles. A generated candidate repo asks the candidate to repair a support copilot that is citing the wrong knowledge-base articles because retrieval leaks tenant data, ranks stale keyword-heavy documents too highly, and returns answers without defensible citations.

## Template Contents

- `candidate/`: starter repo with Docker Compose, public fixtures, public tests, and intentionally flawed retrieval code.
- `solution/`: reference implementation and solution-only notes.
- `evaluator/`: hidden tests, hidden fixtures, rubric, and evaluator compose file.
- `generators/`: deterministic fixture generator for public and hidden scenarios.
- `metadata/`: source mapping and safety policy for template-aware suggestion.
- `tools/`: render, safety scan, and expected-failure validation scripts.
- `source-dossiers/`: source-inspiration notes and reuse boundaries.

## Local Simulator

The candidate path is a local production simulator, not a pure unit-test repo:

```txt
MinIO documents
-> indexer reads document objects
-> fake embedding API returns deterministic vectors
-> Qdrant stores vectors with tenant, ACL, freshness, and citation payloads
-> Postgres stores tenants, users, ACLs, document metadata, and eval runs
-> retriever receives query and user context
-> ranker/citations build a grounded answer package
-> eval_runner writes retrieval_report.json and summary.md
```

No external credentials are required. The template must not call OpenAI, Pinecone, Supabase cloud, AWS, or customer services.

## Validation

Run these from the template root:

```bash
make validate-solution
make validate-candidate-main-expected-failure
make render
make scan-safety
make validate-docker-integration
make validate
```

`make validate-docker-integration` starts the Docker-backed local simulator and confirms the unsolved starter fails for the intended reasons:

- `tenant_leak_detected`
- `stale_doc_ranked_first`
- `missing_grounded_citation`

`make render` creates:

- `generated/main`: candidate-safe preview with public material only.
- `generated/solution`: private preview with solution, evaluator, rubric, hidden fixtures, and expected outputs.

## Golden Template Bar

This template is ready to use as a golden pattern only when local validation and remote GitHub Actions both pass.

## For Challenge Creation Agents

Do not infer how to use this template from README prose.

Read `translucid-template.json`.

Normal use:

```bash
make render
make scan-safety
make validate-solution
make validate-candidate-main-expected-failure
make validate-docker-integration
```

Use:

- `generated/main` as candidate-facing main branch
- `generated/solution` as private solution/evaluator branch

Do not manually copy `candidate/` to root.
Do not manually restructure `solution/`.
Do not edit hidden tests or evaluator imports unless a validation command fails and the exact blocker is recorded.

