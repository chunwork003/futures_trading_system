# GAP-08 W4R PostgreSQL Gate Authorization Amendment 01

Status:

`BOUNDED_AUTHORIZED_FOR_W4R_PG_RF01_TEST_FIXTURE_ONLY`

Execution baseline:

`d47e0ded3424f84e9953d25027ad9366d660a7ed`

## Exact writable source file

`tests/integration/test_operational_persistence.py`

Exactly one repository source file.

## Exact correction

Add a deterministic non-null test client ref to the initial Order:

`broker_client_order_ref=f"PG{major}-CLIENT"`

Do not change production code, migrations, Order semantics, or repository validation.

## Existing real evidence

PG17 W4R concurrency scenarios already executed and passed. RF01 must rerun the targeted harness.

## Authorized environment

- `POSTGRES17_TEST_DSN`: explicit TEST database;
- `POSTGRES18_TEST_DSN`: optional.

Never print DSN values.

## Test gates

Targeted:
`tests/integration/test_w4r_recovery_concurrency.py`

Compatibility:
`tests/integration/test_postgres_foundation.py`
`tests/integration/test_operational_persistence.py`

Then one full regression.

## Git

Exactly one test correction commit:

`test(persistence): refresh PostgreSQL operational smoke fixture`

Then STOP for Result Intake and independent W4 final review.

## Denied

Production changes, migration changes, broker I/O, V07 production conformance, W4 closure by executor, P7.
