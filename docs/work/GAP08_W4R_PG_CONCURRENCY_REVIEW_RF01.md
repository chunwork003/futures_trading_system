# GAP-08 W4R PostgreSQL Concurrency Gate Review RF01

Reviewed environment execution:

- PostgreSQL 17 configured and reachable;
- server_version_num = `170011`;
- Psycopg = `3.3.6`;
- TEST_DSN only;
- migrations through 0009 authorized on TEST_DSN.

Disposition:

`PG17_CONCURRENCY_EVIDENCE_PASS / COMPATIBILITY_FIXTURE_RF01_REQUIRED`

## Positive evidence retained

Real PostgreSQL 17 executed both W4R concurrency scenarios successfully.

Observed progress:

`tests/integration/test_w4r_recovery_concurrency.py .s.s`

Under the PG17/PG18 parametrization this means:
- PG17 handoff-lock scenario: PASS;
- PG18 handoff-lock scenario: SKIP;
- PG17 readiness-CAS scenario: PASS;
- PG18 readiness-CAS scenario: SKIP.

## Compatibility failure

`tests/integration/test_operational_persistence.py` constructs an initial durable `Order` without `broker_client_order_ref`.

Current canonical persistence contract requires initial durable order version 0 plus non-null stable `broker_client_order_ref`.

Observed fail-closed error:

`initial durable order requires sequence-0 broker client ref`

This is a stale integration fixture, not a production defect.

## RF01 correction

Modify only:

`tests/integration/test_operational_persistence.py`

Add a deterministic test-only value such as:

`broker_client_order_ref=f"PG{major}-CLIENT"`

Do not modify production code, migrations, or weaken repository validation.

## Runner tooling correction

The previous transient PowerShell runner used `$Args` as a named parameter, colliding with PowerShell's automatic variable. The targeted stage therefore ran the full suite.

Correct transient runner parameter name to `$PytestArgs`.

This is a `.tmp` tooling defect only.

## Required re-verification

With PG17 TEST_DSN still configured:

1. targeted concurrency;
2. PostgreSQL foundation + operational persistence compatibility;
3. full regression.

PG17 must actually execute. PG18 may remain skipped if not configured.

## Governance

W4R-D remains internally complete 18/18. PG17 concurrency evidence is retained. W4 remains HOLD until RF01 compatibility and final regression pass. P7 remains NOT_AUTHORIZED.
