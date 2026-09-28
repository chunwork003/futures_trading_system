# GAP-08 W4R-B2 Authorization Amendment 01

Status:

`BOUNDED_AUTHORIZED_FOR_GAP08_W4R_B2_RF01_ONLY`

Correction base:

`b505c41a7c46a6dbe335cb3cb738270f1acbac32`

Parent authorization:

`docs/work/GAP08_W4R_B2_AUTHORIZATION.md`

Independent review:

`docs/work/GAP08_W4R_B2_REVIEW_RF01.md`

## Goal

Seal the B2 resolver provenance contract by binding exact full durable receipt material.

No W4R-C/D implementation is authorized.

## Exact writable files

Production:

- `persistence/broker_recovery.py`
- `persistence/recovery.py`

Tests:

- `tests/unit/test_c15_account_recovery_readiness.py`

Exactly these three files.

No new files.

## RF01-1 Full discovery receipt fingerprint

Add a deterministic full-receipt fingerprint for `BrokerDiscoveryReceipt`.

Fingerprint must derive from normalized canonical receipt material and include all receipt-level identity/provenance fields.

It must not trust an arbitrary caller-supplied fingerprint.

## RF01-2 Full reconstruction receipt fingerprint

Add a deterministic full-receipt fingerprint for `BrokerReconstructionReceipt`.

Fingerprint must derive from normalized canonical receipt material after existing canonicalization/derived-field validation.

It must bind all canonical reconstruction material and receipt-level provenance.

## RF01-3 Resolver-core exact receipt binding

`TrustedRecoveryEvidenceCore` must preserve:

- discovery receipt ID + full receipt fingerprint;
- canonical reconstruction receipt IDs + corresponding full receipt fingerprints.

Identity/fingerprint order must be deterministic and one-to-one.

Do not use reconstruction `output_fingerprint` as the only receipt authority fingerprint.

## RF01-4 Duplicate/canonical requested receipt identities

Resolver must establish one explicit deterministic contract.

Preferred:

- normalize reconstruction receipt IDs;
- reject duplicate requested IDs;
- sort unique IDs deterministically before exact reads.

The returned core must follow the same deterministic ordering.

Do not silently treat duplicated caller IDs as separate positive evidence.

## Required counterexamples first

1. same reconstruction plan / different canonical input material => different full receipt fingerprint;
2. same reconstruction material / different producer or contract version => different full receipt fingerprint;
3. same discovery result / different producer or contract version => different full receipt fingerprint;
4. model dump/reload => identical full receipt fingerprint;
5. reconstruction input ID ordering => deterministic core ordering;
6. duplicate requested reconstruction receipt ID => fail closed;
7. changed accepted Fill set => changed reconstruction full receipt fingerprint;
8. core still exposes no READY/finalize/handoff authority.

## Protected / read only

- `adapters/capabilities.py`
- `adapters/sinopac/capabilities.py`
- `persistence/postgres/broker_recovery.py`
- `persistence/account.py`
- `persistence/postgres/account.py`
- `persistence/postgres/recovery.py`
- `persistence/reconciliation.py`
- `persistence/postgres/reconciliation.py`
- all migrations
- W4R-A/B1 frozen code outside exact writable files
- broker network code
- docs
- `data/`

Need outside scope => `STOP / REAUTHORIZATION`.

## Test gates

Targeted:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/test_c15_account_recovery_readiness.py -q --basetemp .\.tmp\pytest-w4r-b2-rf01-targeted
```

Compatibility:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/test_broker_capabilities.py tests/unit/test_c07_broker_discovery.py tests/unit/test_c10_broker_reconstruction.py tests/unit/test_operational_postgres.py -q --basetemp .\.tmp\pytest-w4r-b2-rf01-compat
```

Full regression exactly once after targeted/compatibility pass:

```powershell
.\.venv\Scripts\python.exe -m pytest -q --basetemp .\.tmp\pytest-w4r-b2-rf01-full
```

## Efficiency policy

Report:

- actual changed files;
- approximate diff size;
- semantic correction cycles;
- tooling retries;
- 5HR consumption.

Do not use total pytest pass count as workload.

Use known-working direct/controlled patch interface immediately.

## Git

Exactly one correction commit:

`fix(recovery): bind W4R-B2 full receipt provenance`

Push once after remote ancestry guard.

Then STOP reviewer.

## Denied

- capability semantic changes;
- provider production composition changes;
- W4R-C/D;
- migrations;
- actual PostgreSQL/V07;
- A08;
- broker/paper/Shioaji I/O;
- production;
- P7;
- W4 closure/credit;
- files outside exact writable set.
