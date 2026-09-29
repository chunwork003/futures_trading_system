# GAP-08 W4R-D3 Authorization — Trusted C15 + Atomic Final Handoff

Status:

`BOUNDED_AUTHORIZED_FOR_GAP08_W4R_D3_ONLY`

Execution baseline:

`6aa0b51b6c550a4eef46b680de70b7f326c216f8`

Dependencies:

- W4R-A ACCEPTED / FROZEN
- W4R-B ACCEPTED / FROZEN
- W4R-C ACCEPTED / FROZEN
- W4R-D1A ACCEPTED / FROZEN
- W4R-D1B ACCEPTED / FROZEN
- W4R-D2 ACCEPTED / FROZEN

Parent plan:

`docs/work/GAP08_W4R_D_EXECUTION_PLAN.md`

## Goal

Implement only W4R-D3:

1. trusted-bundle C15 readiness projection;
2. one PostgreSQL caller-owned final handoff UoW;
3. active-control lock before D2 re-resolution;
4. non-READY rollback/no handoff;
5. READY exact fence recheck;
6. existing C09 `finalize_handoff()` in the same UoW;
7. one commit only after the conditional handoff succeeds.

D3 does not change D2 authority owners.

D3 does not perform broker I/O.

## Exact writable files

Production:

- `persistence/recovery.py`
- `persistence/postgres/recovery.py`

Tests:

- `tests/unit/test_c15_account_recovery_readiness.py`
- `tests/unit/test_operational_postgres.py`

Exactly these four files.

No new files.

A legitimate smaller subset is allowed.

## Protected / read only

Including:

- `persistence/broker_recovery.py`
- `persistence/postgres/broker_recovery.py`
- `persistence/postgres/uow.py`
- all W4R-A/B/C/D1/D2 frozen owners outside the exact scope;
- all migrations;
- broker adapters;
- docs;
- `data/`.

D3 must reuse, not modify:

- `PostgresUnitOfWork`;
- `PostgresBrokerRecoveryRepository.finalize_handoff()`;
- `PostgresTrustedReadinessEvidenceResolver`;
- `TrustedReadinessEvidenceBundle`.

Need protected production changes => STOP / REAUTHORIZATION.

## D3-A — pure trusted readiness projection

Add an immutable evaluation model, suggested name:

`TrustedReadinessEvaluation`

Minimum fields:

- `state: RecoveryReadinessState`
- `reasons`
- BrokerAccount
- `bundle_fingerprint`
- recovery generation
- recovery-cut revision
- ingress version
- readiness revision
- formal run ID

It is evidence/audit output only.

It has no finalize/handoff/activation capability.

Add a pure evaluator, suggested name:

`evaluate_trusted_readiness(...)`

It must accept only trusted, resolver-backed material.

Required authority inputs:

- `TrustedReadinessEvidenceBundle`
- exact durable `BrokerDiscoveryReceipt` re-read by the D3 PostgreSQL service in the same UoW

Do not accept convenience authority booleans such as:

- `discovery_complete`
- `continuity_current`
- `pending_material_inbox`
- `reconstruction_complete`
- `mandatory_capabilities_available`
- `exact_correlation_integrity`
- `ready`

Do not reuse caller-built `AccountReadinessEvidence` as final authority.

The legacy pure evaluator remains a compatibility/read-only surface unless a bounded additive helper is needed. Do not weaken its behavior.

## D3-A1 — discovery

The exact discovery receipt passed to the pure evaluator must be canonical-redecoded and must match the bundle trusted core:

- account;
- recovery generation;
- discovery run ID;
- result fingerprint;
- full receipt fingerprint.

Mismatch:

`TrustedRecoveryEvidenceError`

Discovery classification:

- COMPLETE + CONSISTENT => gate passes;
- incomplete/unresolved discovery => REVIEW;
- ambiguous/integrity-conflicted discovery => REVIEW or fail closed according to existing typed discovery contract;
- caller cannot substitute a typed result unrelated to the durable receipt.

## D3-A2 — continuity

Use the bundle head-selected current epoch.

- `trusted_current == True` => continuity gate may pass;
- `trusted_current == False` => REVIEW;
- historical gaps alone do not force REVIEW when the accepted current epoch is a valid trusted re-anchor;
- D2 gap/transition fingerprint binding remains authority.

Never select an older trusted epoch.

## D3-A3 — broker report disposition

Use only:

`bundle.broker_report_witness`

which D2 now scopes to the selected recovery generation.

The evaluator may parse the canonical witness representation but must fail closed on malformed/cross-generation material.

Mirror C09 terminal disposition semantics:

for `recovery_active_at_capture == True`, the latest application must be one of:

- `APPLIED`
- `DUPLICATE`
- `CORROBORATED`

Otherwise the report gate is REVIEW.

Latest application authority is `application_sequence`, not timestamp.

The existing C09 `finalize_handoff()` remains the final SQL/CAS guard and must still be called on READY.

## D3-A4 — BrokerAction

If any bundle BrokerAction head has:

`unresolved_attempt_id != None`

readiness is REVIEW.

Do not infer resolution from timestamps or absence of an external lookup.

## D3-A5 — C13 blocker

Use only:

`bundle.reconciliation_blocker`

Precedence:

- HALT blocker => HALT;
- REVIEW_REQUIRED blocker => REVIEW;
- no blocker => no C13 block.

Do not rerun/duplicate the C13 blocker algorithm inside the pure evaluator.

The D2 resolver already re-resolves C13 in the final transaction.

## D3-A6 — formal reconciliation

Use exact bundle C14 boundary/outcome.

Same-world identity/linkage is already D2 authority.

Classification:

- technical outcome `FAILED` => HALT;
- input qualification not `QUALIFIED` => REVIEW;
- technical outcome not `COMPLETED` => REVIEW;
- any reconciliation result not `MATCH` => REVIEW;
- qualified/completed all-MATCH including exact empty/empty evidence may pass because D2 already positively resolved the exact expected snapshot and exact broker observation bound to the same C14 run/world.

Do not trust caller completeness booleans.

## D3-A7 — reconstruction / capability / closure

D2 trusted core/root/closure are positive authority prerequisites.

D3 must not replace them with booleans.

At minimum preserve/validate:

- reconstruction ID/output/full-receipt arrays remain internally coherent;
- capability evidence corresponds to the D3 service configured required capability set;
- required verification mode equals D3 configured mode;
- required capability source provenance remains resolver-backed;
- root/closure exact fingerprint linkage remains;
- ambiguous report roots (`root_set.ambiguous_report_ingress_ids`) => REVIEW.

If the trusted core cannot prove the service-configured required capabilities, fail closed.

## D3-B — PostgreSQL finalizer service

Add one PostgreSQL orchestration service in:

`persistence/postgres/recovery.py`

Suggested name:

`PostgresTrustedReadinessFinalizer`

It owns the final transaction orchestration only.

It must use a caller-owned/injected UoW factory whose UoW exposes the existing PostgreSQL connection and commit/rollback behavior.

### Policy/config authority

Required capabilities and required verification mode must be constructor/configuration state of the finalizer.

They must NOT be optional per-finalize convenience inputs that a caller can weaken to an empty/lower requirement at handoff time.

The finalizer passes its configured requirements to D2 resolver.

Exact evidence IDs remain finalize selectors, not authority:

- BrokerAccount
- discovery run ID
- reconstruction receipt IDs
- broker observation ID
- formal run ID
- recorded_at

Selectors are re-read/revalidated inside the transaction.

## D3-C — exact final transaction order

One UoW:

1. enter existing PostgreSQL UoW;
2. `SELECT` exact active `AccountRecoveryControl ... FOR UPDATE`;
3. fail closed if control missing/inactive;
4. capture exact:
   - generation;
   - recovery-cut revision;
   - ingress version;
   - readiness revision;
5. construct/use D2 `PostgresTrustedReadinessEvidenceResolver` on this same connection;
6. re-resolve the complete D2 bundle under the held control lock;
7. require bundle fence values exactly equal the captured locked control;
8. re-read exact durable `BrokerDiscoveryReceipt` in this same transaction and bind it to bundle trusted-core fingerprints;
9. run pure trusted C15 evaluator;
10. if state != READY:
    - explicit rollback;
    - no `finalize_handoff`;
    - return immutable evaluation;
11. if state == READY:
    - re-read/recheck the same active control under lock;
    - all captured generation/cut/ingress/readiness values must still match;
12. build inactive completed control using canonical aware UTC `recorded_at`;
13. call existing:
    `PostgresBrokerRecoveryRepository.finalize_handoff(...)`
    with exact expected generation/ingress/readiness;
14. if C09 conditional handoff rejects:
    - no commit;
    - rollback by UoW/error path;
15. commit exactly once;
16. return READY evaluation.

No broker I/O occurs.

No other durable write occurs.

## D3-D — control-lock helper

A private helper inside `persistence/postgres/recovery.py` may perform the exact control lock.

It must:

- select one BrokerAccount row;
- use `FOR UPDATE`;
- decode an `AccountRecoveryControl`;
- require active state;
- perform no commit/rollback;
- not create a second authority model.

Do not add a new public repository owner solely for D3.

## D3-E — errors

Authority/integrity conflicts:

- fail closed;
- no handoff;
- no commit.

Database operational/programming errors:

- propagate;
- do not convert them into READY/REVIEW convenience states.

Do not broadly catch `Exception` around the whole finalizer.

The UoW rollback behavior remains the transaction cleanup authority on raised errors.

## Mandatory counterexamples first

Pure evaluator:

1. caller cannot pass legacy readiness booleans to trusted evaluator;
2. forged/cross-account discovery receipt fails;
3. discovery receipt fingerprint mismatch fails;
4. incomplete discovery => REVIEW;
5. untrusted head-selected continuity epoch => REVIEW;
6. historical gap + trusted current re-anchor is not automatically blocked;
7. malformed/cross-generation report witness fails closed;
8. pending current-generation material report => REVIEW;
9. resolved current-generation report disposition does not block;
10. unresolved BrokerAction => REVIEW;
11. C13 HALT => HALT;
12. C13 REVIEW_REQUIRED => REVIEW;
13. formal technical FAILED => HALT;
14. formal unqualified/incomplete/non-MATCH => REVIEW;
15. ambiguous recovery-root report evidence => REVIEW;
16. fully trusted world => READY;
17. evaluation is immutable and carries exact bundle fingerprint/fence values.

Final transaction:

18. active control lock is the first readiness-authority operation and uses `FOR UPDATE`;
19. missing/inactive control fails before D2 resolver;
20. D2 resolver runs after control lock on the same connection;
21. bundle control/fence mismatch fails before evaluator/handoff;
22. exact discovery receipt is re-read in the same transaction;
23. non-READY explicitly rolls back and never calls handoff;
24. READY rechecks locked control before handoff;
25. control drift fails closed;
26. C09 `finalize_handoff()` receives exact generation/ingress/readiness;
27. finalize conflict => no commit;
28. READY success => one handoff + exactly one commit;
29. configured required capabilities/mode cannot be weakened by finalize-call arguments;
30. no broker I/O surface;
31. no migration/schema surface;
32. no D2 semantic duplication/weakening.

## Test gates

Targeted:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/test_c15_account_recovery_readiness.py -q --basetemp .\.tmp\pytest-w4r-d3-targeted
```

Compatibility:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/test_operational_postgres.py tests/unit/test_c09_broker_recovery_fence.py tests/unit/test_c13_reconciliation_case_scope.py tests/unit/test_c14_reconciliation_run.py tests/unit/test_c10_broker_reconstruction.py -q --basetemp .\.tmp\pytest-w4r-d3-compat
```

Full regression exactly once after targeted/compatibility pass:

```powershell
.\.venv\Scripts\python.exe -m pytest -q --basetemp .\.tmp\pytest-w4r-d3-full
```

If production code changes after final full regression, rerun final full regression and report transparently.

## Tooling

`CONTROLLED_ROUTE_SET`

Known reparse-point repository-local edit restriction is already established.

Codex may go directly to controlled staging for edit transport.

Requirements:

- stage/materialize only exact authorized files;
- copy back exact changed authorized files only;
- immediate repository-local scope/diff guard;
- pytest runs only in repository checkout;
- repository-local basetemp;
- do not retry known equivalent reparse routes.

Tooling-route switches inside this set do not require reauthorization.

## Compatibility corridor

Within the two authorized D3 test files, bounded fixtures/test doubles may be adjusted to express the frozen D3 contract.

No other test file write is authorized.

No production file expansion is authorized.

## Git

Exactly one runtime commit:

`feat(recovery): add W4R-D3 atomic trusted handoff`

Before push:

- origin/master must still equal the D3 governance execution baseline;
- no amend/rebase/force push.

Push once, then STOP for independent review.

## Completion report

Report:

- initial/final HEAD and origin;
- exact changed files;
- diff size;
- pure evaluator counterexample results;
- final transaction ordering evidence;
- targeted/compat/full regression;
- semantic correction cycles;
- tooling route switches/retries;
- 5HR consumption when available;
- migration/actual PostgreSQL/broker I/O = NO;
- STOP.

## After D3

D3 acceptance does NOT close W4.

If D3 is independently accepted:

- W4R-D becomes internally complete;
- internal W4R package weight may become `18/18`;
- official W4 weight remains NOT_CREDITED;
- next mandatory gate is isolated PostgreSQL integration/concurrency verification for the shared recovery fence / atomic handoff claim;
- then final independent W4 review/closure decision;
- P7 remains NOT_AUTHORIZED until W4 closure.
