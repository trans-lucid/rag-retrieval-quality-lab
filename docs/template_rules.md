# Template Rules And Build Instructions

These rules apply to Translucid internal challenge templates, including `async-webhook-ledger` and `rag-retrieval-quality-lab`.

## Repo Contract

- The repo is an internal template repo, not a generated candidate repo.
- It may contain `candidate`, `solution`, `evaluator`, `metadata`, `generators`, and `source-dossiers`.
- Rendered candidate main must contain only candidate-safe files.
- Rendered candidate main must not contain hidden tests, hidden fixtures, evaluator material, solution code, `SOLUTION.md`, rubric files, source dossiers, or internal-only metadata.

## Candidate Contract

- Candidate work must exercise a realistic production path.
- Public tests may include unit tests, but at least one public integration path must use local services when the challenge domain requires service behavior.
- The starter should fail public validation for known, intentional reasons.
- Expected starter failures must be checked by wrapper scripts so random failures are not treated as success.

## Local Simulator Contract

- Use local services instead of live cloud credentials.
- Add readiness retry logic in application scripts, not fragile sleeps in CI.
- Prefer Docker Compose for candidate-facing commands.
- Use hidden/evaluator tests to add stricter service behavior and harder fixtures.

## Safety Contract

- Do not copy startup source code.
- Do not copy real customer data.
- Do not require OpenAI, Pinecone, AWS, Supabase cloud, Stripe, or other external credentials.
- Use public repos and docs only as architecture inspiration.
- Run render and safety scan before pushing.

## Validation Contract

Every golden template should expose:

- `validate-solution`
- `validate-candidate-main-expected-failure`
- `validate-docker-integration`
- `render`
- `scan-safety`
- `validate`

Remote GitHub Actions must run the same gates before a template is treated as a pattern for later templates.
