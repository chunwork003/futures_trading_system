# GAP-08 W4R-D2 Authorization

Status:

`BOUNDED_AUTHORIZED_FOR_GAP08_W4R_D2_ONLY`

Execution baseline:

`ef3400a0cbabc52b45cb2e4f5e69bae0711b64ba`

Dependencies:

- W4R-A ACCEPTED / FROZEN
- W4R-B ACCEPTED / FROZEN
- W4R-C ACCEPTED / FROZEN
- W4R-D1A ACCEPTED / FROZEN
- W4R-D1B ACCEPTED / FROZEN

Parent plan:

`docs/work/GAP08_W4R_D_EXECUTION_PLAN.md`

## Goal

Implement only W4R-D2:

`TrustedReadinessEvidenceBundle`

D2 must produce one immutable same-world trusted bundle from already accepted A/B/C/D1 evidence.

D2 is pure read/resolution work.

D2 must not:

- evaluate or grant C15 READY;
- finalize C09 handoff;
- change `AccountRecoveryControl.active`;
- change any readiness writer;
- commit/rollback;
- perform broker I/O;
- modify migrations.

## Ownership

Domain bundle/resolution composition owner:

`persistence/recovery.py`

PostgreSQL exact same-world resolver owner:

`persistence/postgres/recovery.py`

Reuse accepted owners rather than duplicate their semantics:

- `TrustedRecoveryEvidenceResolver`
- `TrustedReconciliationBlockerResolver`
- `RecoveryRootResolver`
- `RecoveryClosureResolver`
- C13 repository semantics
- C14 exact boundary/outcome reads
- existing exact account/recovery/currentness helpers
- existing capability provider semantics
- existing BrokerAction repository semantics

Do not move ownership into C15 evaluator.

## Immutable bundle

Add a frozen typed model named:

`TrustedReadinessEvidenceBundle`

It must bind one authoritative world at least across:

### Recovery/control identity

- BrokerAccount;
- active recovery generation;
- recovery cut revision;
- ingress version;
- readiness revision;
- canonical RecoveryCut fingerprint.

### Account authority closure

- AccountStateHead identity/current revision;
- exact checkpoint;
- exact authority-commit receipt;
- expected snapshot identity;
- authority commit identity.

### Continuity authority

- exact current `ExecutionContinuityHead`;
- exact current epoch selected by that head;
- exact transition receipt selected by that head;
- deterministic current gap semantic fingerprint.

Do not infer current epoch from latest timestamp, lexical order or an epoch `trusted_current` flag alone.

### Broker report disposition

Bind deterministic current broker-report disposition/evidence for the selected BrokerAccount/generation.

Caller booleans such as `pending_material_inbox=False` are not authority.

### BrokerAction semantic state

Bind deterministic exact BrokerAccount-scoped BrokerAction semantic state required by current recovery roots/currentness.

Use existing BrokerAction owner semantics/read port where possible; do not duplicate action SQL if an accepted repository read already exists.

### C13 blocker evidence

Bind resolver-produced:

`TrustedReconciliationBlockerEvidence`

No caller-provided blocking state or fingerprint may substitute for C13 re-resolution.

### B1/B2 trusted recovery core

Bind resolver-produced:

`TrustedRecoveryEvidenceCore`

including:

- exact discovery receipt identity/fingerprint;
- exact reconstruction receipt identities/full fingerprints;
- exact expected snapshot;
- exact broker observation;
- capability registry/version/fingerprint;
- capability source IDs / verification mode.

### C14 formal run

Bind exact:

- `ReconciliationRunBoundary`
- `ReconciliationRunOutcome`

The outcome must belong to the exact selected boundary/run.

### C2 root/closure evidence

Bind resolver-produced:

- `RecoveryRootSetEvidence`
- `RecoveryClosureEvidence`

Their account/generation/root-set fingerprint must agree exactly.

## Bundle canonicalization

The bundle must be immutable and deterministic.

Add a derived canonical `bundle_fingerprint`.

Rules:

- caller-supplied `bundle_fingerprint` cannot override canonical derivation;
- canonical serialization/fingerprint excludes only the fingerprint field itself;
- nested evidence must be canonical decoded/revalidated before inclusion;
- mismatched account/generation/cut/run/root/closure identity fails closed;
- the model/service must not contain `ready`, `finalize`, `handoff`, `activate`, or broker mutation capability.

## Same-world invariants

Resolver construction must positively enforce at least:

1. requested account equals RecoveryCut/account authority scope;
2. active recovery control exists;
3. control account matches requested account;
4. selected generation matches all generation-scoped evidence;
5. control recovery-cut revision matches account authority/current recovery cut revision;
6. selected RecoveryCut fingerprint matches B2/reconstruction/C14 references;
7. AccountStateHead/checkpoint/receipt form exact accepted closure;
8. expected snapshot ID matches checkpoint and B2 exact snapshot;
9. C14 boundary account/revision/snapshot/authority/generation/ingress/cut matches the same world;
10. C14 outcome run ID equals boundary run ID;
11. continuity head account/generation is exact;
12. continuity head exact epoch and transition receipt exist and match;
13. transition receipt account/generation/head revision/current epoch/cut/account revision/snapshot/authority linkage agrees;
14. current gap semantic fingerprint is derived from durable exact gap evidence;
15. C13 blocker evidence account matches;
16. C2 root set account/generation matches B2/current recovery generation;
17. C2 closure account/generation/root-set fingerprint matches the selected root set;
18. BrokerAction/read-report evidence belongs to the same BrokerAccount/current generation where applicable.

Any mismatch:

`TrustedRecoveryEvidenceError`

or an existing more-specific integrity error.

Do not silently downgrade a material identity conflict into a boolean or REVIEW state in D2.

## PostgreSQL D2 resolver

Add a pure PostgreSQL resolver in `persistence/postgres/recovery.py`.

Suggested name:

`PostgresTrustedReadinessEvidenceResolver`

It must work in a caller-owned transaction/connection and must not commit.

It may accept exact identifiers/configuration required to select already-known evidence, for example:

- BrokerAccount;
- discovery run ID;
- reconstruction receipt IDs;
- broker observation ID;
- formal run ID;
- required capabilities;
- required verification mode.

Exact identifiers are selectors only.

Selectors do not become authority until the resolver re-reads and validates their durable sources.

Caller-provided booleans/fingerprints must not bypass any durable read.

### Required reuse

Where accepted exact read helpers/owners already exist, reuse them.

In particular:

- existing account/currentness witness logic may be factored/reused rather than duplicated;
- C13 must go through `PostgresReconciliationCaseRepository` + `TrustedReconciliationBlockerResolver`;
- C14 must go through exact boundary/outcome repository reads;
- B2 trusted core must remain `TrustedRecoveryEvidenceResolver`;
- C2 roots/closure must remain `RecoveryRootResolver` + `RecoveryClosureResolver`.

Do not change accepted B/C semantics to make D2 easier.

## Transaction boundary

D2 itself:

- reads only;
- does not acquire final handoff authority;
- does not flip active recovery;
- does not commit/rollback.

D3 will later call/re-run the accepted D2 resolver under the final locked control fence.

D2 must not pre-implement D3 locking/handoff.

## Required counterexamples first

At minimum prove:

1. typed bundle with cross-account nested evidence is rejected;
2. generation mismatch across B2/root/closure/continuity is rejected;
3. cut fingerprint mismatch is rejected;
4. caller-provided bundle fingerprint cannot override derived fingerprint;
5. active recovery control missing/inactive is rejected;
6. account head/checkpoint/receipt missing or inconsistent is rejected;
7. expected snapshot identity drift is rejected;
8. stale historical continuity epoch cannot substitute for head-selected epoch;
9. head/epoch/transition receipt identity mismatch is rejected;
10. continuity transition cut/account/snapshot/authority mismatch is rejected;
11. durable gap-set material change produces a different semantic fingerprint;
12. forged C13 blocking state/fingerprint cannot bypass resolver;
13. C14 outcome for another/missing run is rejected;
14. C14 boundary cross-world account/revision/generation/ingress/cut mismatch is rejected;
15. C2 root-set vs closure fingerprint mismatch is rejected;
16. missing exact discovery/reconstruction/observation/capability evidence fails closed;
17. BrokerAction/report evidence for another account/world is rejected;
18. bundle exposes no READY/finalize/handoff/activation surface;
19. resolver performs no commit/rollback;
20. no broker I/O surface is introduced.

## Exact writable files

Production:

- `persistence/recovery.py`
- `persistence/postgres/recovery.py`

Tests:

- `tests/unit/test_c15_account_recovery_readiness.py`
- `tests/unit/test_operational_postgres.py`

Exactly these four files.

No new files.

## Protected / read only

Including:

- all W4R-A/B/C/D1 frozen production files outside the exact scope;
- `persistence/broker_recovery.py`
- `persistence/postgres/broker_recovery.py`
- `persistence/account.py`
- `persistence/postgres/account.py`
- `persistence/account_authority.py`
- `persistence/postgres/account_authority.py`
- `persistence/broker_action.py`
- `persistence/postgres/broker_action.py`
- `persistence/reconciliation.py`
- `persistence/postgres/reconciliation.py`
- all migrations;
- adapters/capability source;
- broker network adapters;
- docs;
- `data/`.

Need outside scope:

`STOP / REAUTHORIZATION`

## Test gate

Targeted:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/test_c15_account_recovery_readiness.py -q --basetemp .\.tmp\pytest-w4r-d2-targeted
```

Compatibility:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/test_operational_postgres.py tests/unit/test_c13_reconciliation_case_scope.py tests/unit/test_c14_reconciliation_run.py tests/unit/test_c09_broker_recovery_fence.py tests/unit/test_c10_broker_reconstruction.py -q --basetemp .\.tmp\pytest-w4r-d2-compat
```

Full regression exactly once after targeted/compatibility pass:

```powershell
.\.venv\Scripts\python.exe -m pytest -q --basetemp .\.tmp\pytest-w4r-d2-full
```

If production changes after full regression, rerun the final full regression and report transparently.

## Tooling mode

`CONTROLLED_STAGING_ROOT_FIRST`

Repository-local/direct test execution is the known-good route.

The external-staging/common-root pytest route is a known failing route and MUST NOT be attempted.

Trying that known failing route counts as avoidable tooling failure.

## Efficiency report

Report:

- actual changed file count/list;
- additions/deletions;
- semantic correction cycles;
- tooling retries;
- 5HR consumption.

Pytest count is verification, not workload.

## Git

Exactly one runtime commit:

`feat(recovery): add W4R-D2 trusted readiness bundle`

Before push:

- origin/master must still equal the D2 execution baseline produced by governance materialization;
- no amend/rebase/force push.

Push once then STOP reviewer.

## Side effects

ALLOW:

- exact four-file source/test work;
- local tests;
- one commit/push.

DENY:

- D3;
- C15 READY/evaluator semantic changes;
- final handoff;
- recovery-control activation/deactivation;
- readiness writer changes;
- migrations;
- actual PostgreSQL/V07;
- A08;
- broker/paper/Shioaji I/O;
- production;
- P7;
- W4 closure/credit.
