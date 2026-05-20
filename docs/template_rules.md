# Template Rules And Build Instructions

These rules apply to every Translucid internal challenge template, including `async-webhook-ledger`, `rag-retrieval-quality-lab`, and the next templates in the library.

## Purpose

- Build internal template repos, not one-off candidate challenge repos.
- Use public sources only as reference architecture, not copied assessments or copied implementations.
- Generate original Translucid-owned code, fixtures, tests, docs, and rubrics.
- Recruiter source repos may personalize generated challenges, but they must not become the challenge repo unless an explicit source-slice mode is approved.

## Required Repo Shape

Each template repo should include:

- `README.md`: internal template overview.
- `README.md.j2`: candidate-facing generated README.
- `DEBRIEF.md.j2`: candidate-facing debrief questions.
- `template.yaml`: template metadata, local service contract, roles, time, signals, expected starter failures, and hidden-test strategy.
- `candidate/`: runnable starter repo with public tests only.
- `solution/`: reference implementation, solution notes, and expected outputs.
- `evaluator/`: hidden tests, hidden fixtures, rubric, evaluator compose file, and evaluator scripts.
- `generators/`: deterministic fixture generator and scenario definitions.
- `metadata/`: source mapping rules and safety policy.
- `source-dossiers/`: source-inspiration notes and reuse boundaries.
- `tools/`: render, safety scan, and expected-failure validation scripts.
- `.github/workflows/template-validation.yml`: remote CI validation.
- `docs/template_rules.md`: reusable rules for future templates.
- `docs/template_progress.md`: template library progress tracker.

## Candidate Main Contract

- Candidate main must be clean and candidate-safe.
- Candidate main must include a runnable repo, public tests, stubs or flawed starter code, fixtures, README, DEBRIEF, local simulator config, and commands.
- Candidate main must not include hidden tests, hidden fixtures, evaluator material, solution code, `SOLUTION.md`, rubrics, source dossiers, internal metadata, or expected private outputs.
- Candidate work must exercise a realistic production path across multiple files.
- Do not make the task solvable by a one-file helper, hardcoded fixture table, parser-only patch, or pure unit-test gimmick.

## Solution And Evaluator Contract

- `solution/` must contain a reference implementation that passes public and hidden tests.
- `evaluator/` must contain hidden tests that can run against the reference solution and a submitted candidate implementation.
- Hidden tests must use harder fixtures and stricter behavior than public tests.
- Hidden tests should defeat hardcoding, public-fixture-only solutions, overbroad retrieval/processing, shallow helper patches, and solutions that bypass the production path.
- Hidden evaluator material must never appear in rendered candidate main.

## Local Production Simulator Rule

- Prefer a local production simulator over pure unit tests when the domain involves queues, storage, databases, vector search, workflows, traces, streaming, retries, or external APIs.
- Use Docker Compose for candidate-facing local services.
- Use local emulators and fakes instead of real credentials or cloud services.
- Add readiness retry logic inside application scripts, not fragile `sleep 10` waits in CI.
- Public tests may include fast unit tests, but at least one public integration path should use local services when service behavior is core to the challenge.
- Hidden/evaluator tests should add stricter service behavior, harder data, duplicate/retry/delay/restart cases, missing metadata, and ambiguity traps where relevant.

## Candidate Command Contract

Each candidate repo should expose a small, predictable command set. Use domain-specific names only when they are clearer.

Recommended Python-heavy pattern:

- `make dev`
- `make logs`
- `make seed`
- `make test`
- `make test-unit`
- `make test-integration`
- `make eval` or `make run`
- `make clean`

Recommended TypeScript-heavy pattern:

- `make dev`
- `make logs`
- `make seed`
- `make test`
- `make run`
- `make clean`

Commands must work from a fresh clone after dependency install.

## Expected Starter Failure Contract

- The starter should fail public validation for known, intentional reasons.
- Wrapper scripts must confirm the failure is expected, not random.
- Expected-failure wrappers should grep for stable markers such as `tenant_leak_detected`, `duplicate_deliveries`, `stale_doc_ranked_first`, or `missing_grounded_citation`.
- Do not claim a template passes because the starter failed. It passes only when the wrapper confirms the intended failure.

## Root Validation Contract

Every golden template must expose these root commands through `Makefile`, `package.json`, or both:

- `validate-solution`
- `validate-candidate-main-expected-failure`
- `validate-docker-integration`
- `render`
- `scan-safety`
- `validate`

Expected behavior:

- `validate-solution`: reference solution passes public and hidden tests.
- `validate-candidate-main-expected-failure`: unsolved starter fails public unit/contract tests for expected markers.
- `validate-docker-integration`: Docker services start, seed/index/setup runs, public integration test runs, and the unsolved starter fails for expected markers.
- `render`: creates `generated/main` and `generated/solution`.
- `scan-safety`: fails if generated candidate main leaks private/internal material or secrets.
- `validate`: runs all required gates, including Docker-backed integration unless explicitly documented as unavailable.

## Render Contract

`tools/render_template.py` must create:

- `generated/main`
- `generated/solution`

`generated/main` may include only:

- `README.md`
- `DEBRIEF.md`
- local simulator files such as `docker-compose.yml`
- candidate commands such as `Makefile`
- candidate dependency manifests
- `src/`
- candidate simulators/fakes needed to run locally
- public fixtures
- public tests
- empty result directory placeholders

`generated/solution` may include:

- all candidate-safe material
- `solution/`
- `evaluator/`
- `SOLUTION.md`
- rubric
- hidden fixtures
- hidden tests
- expected outputs

## Safety Scan Contract

`tools/scan_safety.py` must fail if `generated/main` contains:

- `solution/`
- `evaluator/`
- `tests_hidden/`
- `fixtures_hidden/`
- `SOLUTION.md` or `SOLUTION.md.j2`
- `rubric.md`
- private `expected/` outputs
- `source-dossiers/`
- `template.yaml`
- private keys
- `.env` files
- GitHub tokens
- AWS keys
- OpenAI keys
- Pinecone keys
- Supabase service role keys
- customer source paths
- real customer data markers

This is a lightweight local scan. Production release can still add gitleaks/trufflehog, but the template repo must have this baseline scan.

## Metadata Contract

`template.yaml` must include:

- stable `id`
- title
- area/domain
- language or stack
- roles
- seniority
- time estimates
- local services
- no external credential rule
- evaluation axes
- source/repo matching signals
- candidate expected failures
- hidden-test strategy
- forbidden shortcut patterns

`metadata/source_mapping_rules.json` must help the template suggestion agent map recruiter repo signals to this template. Include:

- `template_id`
- positive signals
- negative signals
- stack matches
- best roles
- personalization knobs

`metadata/safety_policy.json` must state:

- no external credentials
- no cloud calls
- no startup source copying
- no real customer data
- candidate-main forbidden paths
- required scans
- allowed local services

## Source Dossier Contract

Each template needs a dossier under `source-dossiers/`.

The dossier must list:

- sources studied
- what architecture ideas are allowed to inspire the template
- what is forbidden

Allowed:

- architecture patterns
- generic benchmark structure
- public API concepts
- terminology
- metric names
- local emulator patterns

Forbidden:

- copying source code
- copying datasets wholesale
- copying complete exercises
- copying real customer code
- requiring live cloud services
- requiring credentials

## CI Contract

Remote GitHub Actions must run before a template is treated as a pattern for later templates.

CI should run:

- dependency install
- `validate-solution`
- `validate-candidate-main-expected-failure`
- `render`
- `scan-safety`
- `validate-docker-integration`
- Docker logs on failure

Do not call a template golden if remote CI has not passed.

## Fresh-Clone Proof

Before final acceptance, run a fresh clone check:

- clone the pushed repo into `/tmp`
- verify important files have real line counts, especially `Makefile`, workflow YAML, Docker Compose, candidate Makefile, and `template.yaml`
- run the root validation command
- confirm no Docker containers are left running

If Docker image pulls are too slow or Docker validation cannot finish, say `not completed` and leave it as a blocker. Do not claim the integration path passes.

## GitHub Workflow

- Use the `trans-lucid` organization namespace.
- Create repos with `gh repo create trans-lucid/REPO_NAME --private --source=. --remote=origin --push` unless the user explicitly asks to keep it public during active work.
- Clone with `gh repo clone trans-lucid/REPO_NAME`.
- Fork into the org with `gh api repos/OWNER/REPO/forks -f organization='trans-lucid'`.
- Never fork into the personal account.
- Keep commits scoped and named around the template being created.

## Template Progress Tracking

Update `docs/template_progress.md` when a template moves stages:

- planned
- in progress
- golden-template-candidate
- golden

Include coverage areas, local services, validation status, remote CI status, and remaining cleanup notes.

## Final Acceptance Checklist

Do not mark a template as a golden pattern until:

- solution passes public and hidden tests
- unsolved candidate fails public tests for known expected reasons
- Docker-backed public integration expected failure is validated locally and remotely
- render passes
- safety scan passes
- generated candidate main contains no hidden tests
- generated candidate main contains no `SOLUTION.md`
- generated candidate main contains no evaluator material
- generated candidate main contains no source dossier
- generated candidate main contains no private metadata
- source dossier is present
- source mapping rules are present
- safety policy is present
- remote GitHub Actions pass
- fresh-clone validation passes
