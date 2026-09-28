# GAP-08 W4R-B2 Authorization

Status:

`BOUNDED_AUTHORIZED_FOR_GAP08_W4R_B2_ONLY`

Planning baseline:

`92092c02170197767de32dad25aa17323e98cb1b`

Dependencies:

- W4R-A ACCEPTED / FROZEN
- W4R-B1 ACCEPTED / FROZEN

Parent execution plan:

`docs/work/GAP08_W4R_B_EXECUTION_PLAN.md`

## Goal

Implement only W4R-B2:

1. trusted immutable broker capability registry snapshot/provider;
2. deterministic registry ID/version/fingerprint;
3. exact durable discovery/reconstruction receipt read ports;
4. trusted resolver core that re-reads exact B1/account evidence and capability evidence;
5. typed resolver output preserving identity/provenance/currentness inputs for later W4R-D.

B2 must not make C15 READY and must not perform final handoff.

## Trusted capability contract

Reuse existing:

- `BrokerCapabilityMatrix`
- `BrokerCapabilityEvidence`
- `BrokerVerificationMode`
- Sinopac capability matrix

Add a trusted snapshot/provider abstraction.

A capability registry snapshot must bind at least:

- registry_id;
- contract_version;
- broker;
- deterministic matrix fingerprint;
- exact matrix;
- sdk version evidence already present in entries.

Rules:

- fingerprint derives from canonical matrix material;
- arbitrary caller fingerprint cannot override derivation;
- broker must match matrix broker;
- exact capability entries remain immutable;
- verification modes do not imply one another;
- DOCUMENTATION does not imply SIMULATION or PRODUCTION;
- missing/UNKNOWN/UNSUPPORTED required capability fails closed.

No PostgreSQL capability table.

## Exact receipt read ports

Extend broker-recovery repository contract with exact readers:

- discovery receipt by exact `discovery_run_id` + BrokerAccount;
- reconstruction receipt by exact receipt ID + BrokerAccount.

PostgreSQL adapter must:

- use exact ID + broker + account_ref query;
- decode canonical JSON;
- positively verify decoded identity/account against requested scope;
- return `None` for missing/wrong-scope row;
- raise integrity error for malformed or internally mismatched durable material;
- never use latest/timestamp fallback.

No write semantics change in B2.

## Trusted resolver core

Add a resolver-core model/service in persistence recovery layer.

Suggested semantic output:

`TrustedRecoveryEvidenceCore`

It must be resolver-produced, immutable, and bind at least:

- BrokerAccount;
- recovery generation;
- recovery cut fingerprint supplied by current recovery context;
- exact discovery receipt identity/fingerprint;
- exact reconstruction receipt identities/fingerprints;
- exact expected snapshot identity;
- exact broker observation identity;
- capability registry ID/version/fingerprint;
- required verification mode;
- exact capability evidence/source IDs.

Resolver inputs must include exact IDs; no latest fallback.

The resolver must positively prove:

### Discovery

- receipt exists;
- account matches;
- generation matches expected recovery generation;
- discovery_run_id matches requested/formal reference;
- canonical result fingerprint is internally valid.

### Reconstruction

For every requested positive reconstruction receipt:

- exact receipt exists;
- account/generation match;
- recovery_cut_fingerprint matches requested current cut;
- discovery_run_id matches the selected discovery receipt;
- internally canonical derived fingerprints remain valid on decode.

Missing required positive reconstruction receipt => no positive authority.

### Expected / Actual batches

- exact expected snapshot exists for requested ID/account;
- exact broker observation exists for requested ID/account;
- no latest/as-of fallback.

### Capability

- trusted provider broker matches BrokerAccount broker;
- registry fingerprint validates;
- every required capability is supported;
- every required capability includes the requested `BrokerVerificationMode`;
- source IDs are preserved exactly.

## Trust boundary

B2 establishes trusted resolver-core evidence only.

B2 does NOT:

- build final `TrustedReadinessEvidenceBundle`;
- resolve C13 reconciliation cases;
- resolve C14 formal run;
- resolve continuity current head/gap set;
- build recovery-root Fill/Event closure;
- evaluate C15;
- finalize handoff;
- grant runtime authorization.

Those remain C/D.

## Required counterexamples first

1. capability registry caller fingerprint mismatch => validation failure;
2. registry broker != matrix broker => validation failure;
3. DOCUMENTATION evidence requested as PRODUCTION => unavailable;
4. missing capability => unavailable;
5. UNKNOWN capability => unavailable;
6. exact discovery read DB columns correct but receipt JSON belongs to another account => integrity failure;
7. exact reconstruction read JSON receipt ID mismatch => integrity failure;
8. discovery receipt generation != expected recovery generation => resolver rejects;
9. reconstruction recovery_cut_fingerprint != expected cut => resolver rejects;
10. reconstruction discovery_run_id != selected discovery => resolver rejects;
11. missing requested reconstruction receipt => no positive authority;
12. exact snapshot missing => resolver rejects positive completeness;
13. exact observation missing => resolver rejects positive completeness;
14. resolver cannot accept arbitrary caller `source_refs` or availability boolean as capability authority.

## Exact writable files

Production:

- `adapters/capabilities.py`
- `adapters/sinopac/capabilities.py`
- `persistence/broker_recovery.py`
- `persistence/postgres/broker_recovery.py`
- `persistence/recovery.py`

Tests:

- `tests/unit/test_broker_capabilities.py`
- `tests/unit/test_c15_account_recovery_readiness.py`
- `tests/unit/test_operational_postgres.py`

Exactly these eight files.

No new files.

## Protected / read only

- `persistence/account.py`
- `persistence/postgres/account.py`
- `persistence/postgres/recovery.py`
- `persistence/reconciliation.py`
- `persistence/postgres/reconciliation.py`
- `persistence/account_authority.py`
- `persistence/postgres/account_authority.py`
- `persistence/broker_action.py`
- `persistence/postgres/broker_action.py`
- `trading/broker_recovery.py`
- `trading/reconciliation.py`
- all migrations including 0009
- strategy code
- broker network adapters
- docs
- `data/`

Need outside scope => `STOP / REAUTHORIZATION`.

## Test gates

Targeted:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/test_broker_capabilities.py tests/unit/test_c15_account_recovery_readiness.py tests/unit/test_operational_postgres.py -q --basetemp .\.tmp\pytest-w4r-b2-targeted
```

Compatibility:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/test_c07_broker_discovery.py tests/unit/test_c10_broker_reconstruction.py tests/unit/test_c09_broker_recovery_fence.py -q --basetemp .\.tmp\pytest-w4r-b2-compat
```

Full regression exactly once after targeted/compatibility pass:

```powershell
.\.venv\Scripts\python.exe -m pytest -q --basetemp .\.tmp\pytest-w4r-b2-full
```

## Efficiency policy

Measure efficiency primarily from:

- actual changed files;
- approximate diff size;
- semantic correction cycles;
- tooling retries;
- 5HR consumption;
- scope expansion.

Do not treat total pytest pass count as workload.

Known patch/reparse issue: use direct/controlled patch interface immediately.

## Git

Exactly one runtime commit:

`feat(recovery): add W4R-B2 trusted evidence resolver`

Before push:

- origin/master must remain B2 authorization baseline;
- no amend/rebase/force push.

Push once then STOP reviewer.

## Side effects

ALLOW:
- exact eight-file source/test changes;
- local tests;
- one commit/push.

DENY:
- any migration edit/execution;
- actual PostgreSQL/V07;
- A08;
- broker/paper/Shioaji I/O;
- credentials;
- production activation;
- W4R-C/D;
- P7;
- W4 closure/credit.

## Completion report

Report:

- initial HEAD;
- final HEAD/origin;
- commit;
- actual changed file count/list;
- approximate diff size if available;
- counterexample evidence;
- targeted/compat/full results;
- tooling retries;
- semantic correction cycles;
- 5HR consumption;
- migrations unchanged;
- actual PostgreSQL/V07 = NO;
- broker I/O = NO;
- STOP.
