# GAP-08 W4R PostgreSQL Gate Review RF02

Baseline governance commit:

`0898cc0702d5fff2cb0328716c474e74768e775f`

Disposition:

`PG17_CONCURRENCY_PASS / PG_RF01_FIXTURE_RETAINED / RF02_PRODUCTION_ADAPTER_REQUIRED`

## Retained positive evidence

Real PostgreSQL 17 concurrency evidence remains valid:

- handoff-lock scenario: PASS;
- readiness-CAS scenario: PASS;
- PG18 cases: SKIP because PG18 TEST_DSN is not configured.

The RF01 test fixture correction adding:

`broker_client_order_ref=f"PG{major}-CLIENT"`

is retained in the working tree.

## New real PostgreSQL defect

After the RF01 fixture correction, PG17 compatibility reached:

`PostgresStrategyInstanceRepository.append(instance)`

and Psycopg 3.3.6 raised:

`ProgrammingError: cannot adapt type 'dict' using placeholder '%s'`

The production adapter currently passes raw Python dict values into JSONB placeholders.

Affected production paths:

1. `PostgresStrategyInstanceRepository.append()`:
   - `instance.config_json`

2. `PostgresStrategyStateRepository.append()`:
   - `snapshot.state_json`

Both target JSONB columns.

Other PostgreSQL adapters in this repository serialize structured JSON material with `json.dumps(...)` / model JSON before binding.

## Additional stale integration fixture

The same operational persistence smoke still constructs strategy state using:

`last_market_observation_id="BAR"`

Current canonical strategy recovery authority requires a `mor1_` revision identity.

This line has not yet executed because the production JSONB defect stopped the test earlier.

RF02 includes this bounded fixture refresh to avoid a predictable second compatibility cycle.

## RF02 correction

Exact production correction:

- serialize `instance.config_json` with deterministic `json.dumps(...)`;
- serialize `snapshot.state_json` with deterministic `json.dumps(...)`;
- retain `instance.model_dump_json()` / `snapshot.model_dump_json()` for complete evidence payloads;
- no commit inside repositories.

Exact integration correction:

- retain RF01 `broker_client_order_ref`;
- replace legacy `"BAR"` with a canonical `last_market_observation_revision_id`.

Regression guard:

- add one unit test proving both JSONB structured parameters are strings;
- JSON round-trip equals canonical dict material;
- repositories still do not commit.

## No architecture change

This is PostgreSQL adapter conformance to already-frozen JSON/domain contracts.

No migration change.

No D3/concurrency authority change.

No broker behavior change.

## Required verification

1. unit PostgreSQL adapter regression;
2. real PG17 W4R concurrency targeted;
3. real PG17 operational compatibility;
4. one full regression;
5. exact three-file scope;
6. one commit / one push;
7. STOP for Result Intake and final independent W4 review.
