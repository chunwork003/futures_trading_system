# GAP-08 W4R-C2A Authorization

Status:

`BOUNDED_AUTHORIZED_FOR_GAP08_W4R_C2A_ONLY`

Planning baseline:

`d41a0f2a3f760e7c70e60f395cc6aec5c41d046e`

Dependencies:

- W4R-A ACCEPTED / FROZEN
- W4R-B ACCEPTED / FROZEN
- W4R-C1 ACCEPTED / FROZEN

Execution plan:

`docs/work/GAP08_W4R_C2_EXECUTION_PLAN.md`

## Goal

Implement only deterministic minimum recovery-root authority.

Do not implement Fill/Event closure yet.
Do not implement W4R-D.

## C2A-1 BrokerAction account-scoped root owner

Extend `BrokerActionRepository` with a deterministic account-scoped head read:

`list_heads(account: BrokerAccount) -> tuple[BrokerActionHead, ...]`

PostgreSQL implementation must:

- filter exact broker/account_ref;
- return all actions for that BrokerAccount;
- deterministic ORDER BY order_id, action;
- never perform global Order scan;
- no commit/rollback.

C2A may then exact-read the Order projection for each head order_id.

Rules:

- nonterminal head-owned Order => root;
- unresolved head => root even if projection is terminal;
- terminal resolved head alone => not a root unless another source includes it;
- missing Order referenced by head => integrity failure.

## C2A-2 Reconstruction roots

Use B2 trusted core exact reconstruction receipt IDs/fingerprints.

Re-read each receipt from `BrokerRecoveryRepository`.

Require:

- exact account;
- exact generation;
- full receipt fingerprint matches the B2 core one-to-one binding.

Add exact `receipt.order_id` as root.

Mismatch/missing => fail closed.

## C2A-3 Expected snapshot source-event root

Re-read B2 core exact expected snapshot.

Resolve its exact `source_event_id` through `EventLedgerRepository.get`.

Require event exists and is an ORDER entity.

Add event.entity_id as root.

No timestamp/latest fallback.

## C2A-4 Material broker-report root extraction

C2A accepts a tuple explicitly named `material_report_entries`.

These entries are not themselves declared current by C2A; W4R-D must supply them from the final same-world report resolver.

For each entry:

- account/generation must equal B2 trusted core world;
- payload `order_id` string => normalize and add as root;
- missing `order_id` => preserve ingress ID in `ambiguous_report_ingress_ids`;
- non-string/blank order_id => integrity failure.

Never infer order from correlation, quantities, timestamps, broker IDs, or substring matching.

## C2A-5 Immutable root-set evidence

Add resolver-produced immutable evidence binding at least:

- account;
- recovery_generation;
- `order_ids` deterministic sorted unique;
- per-order deterministic source categories;
- `ambiguous_report_ingress_ids`;
- deterministic full root-set fingerprint.

Recommended source enum/categories:

- `BROKER_ACTION_NONTERMINAL`
- `BROKER_ACTION_UNRESOLVED`
- `RECONSTRUCTION_RECEIPT`
- `EXPECTED_SNAPSHOT_SOURCE_EVENT`
- `BROKER_REPORT_EXACT_ORDER`

Same Order may carry multiple source categories.

Caller cannot supply arbitrary root IDs/fingerprint to bypass resolver.

## Required counterexamples first

1. BrokerAction `list_heads` SQL is exact BrokerAccount scoped;
2. other-account head is absent;
3. head-owned nonterminal Order becomes root;
4. terminal resolved head alone does not become root;
5. terminal Order with unresolved BrokerAction remains root;
6. head references missing Order => fail closed;
7. reconstruction receipt missing => fail closed;
8. reconstruction receipt full fingerprint differs from B2 core => fail closed;
9. reconstruction receipt account/generation mismatch => fail closed;
10. expected snapshot missing => fail closed;
11. expected snapshot source event missing => fail closed;
12. expected snapshot source event is not ORDER => fail closed;
13. explicit report payload order_id becomes root;
14. report without order_id is recorded as ambiguous and no root is guessed;
15. malformed report order_id => fail closed;
16. report account/generation mismatch => fail closed;
17. duplicate roots from different sources dedupe deterministically while preserving all source categories;
18. caller cannot inject arbitrary root IDs/fingerprint;
19. no global orders/fills/events scan;
20. output has no READY/finalize/handoff surface.

## Exact writable files

Production:

- `persistence/broker_action.py`
- `persistence/postgres/broker_action.py`
- `persistence/recovery.py`

Tests:

- `tests/unit/test_c06_broker_action_safety.py`
- `tests/unit/test_c15_account_recovery_readiness.py`
- `tests/unit/test_operational_postgres.py`

Exactly these six files.

No new files.

## Protected / read only

- `persistence/reconciliation.py` (C1 frozen)
- `persistence/execution.py`
- `persistence/postgres/execution.py`
- `persistence/events.py`
- `persistence/postgres/event_ledger.py`
- `persistence/broker_recovery.py`
- `persistence/postgres/broker_recovery.py`
- `persistence/account.py`
- `persistence/postgres/account.py`
- all migrations
- W4R-A/B frozen code
- broker network code
- docs
- `data/`

Need outside scope => `STOP / REAUTHORIZATION`.

## Test gates

Targeted:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/test_c06_broker_action_safety.py tests/unit/test_c15_account_recovery_readiness.py tests/unit/test_operational_postgres.py -q --basetemp .\.tmp\pytest-w4r-c2a-targeted
```

Compatibility:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/test_c10_broker_reconstruction.py tests/unit/test_c12_recovery_cut.py tests/unit/test_c13_reconciliation_case_scope.py -q --basetemp .\.tmp\pytest-w4r-c2a-compat
```

Full regression exactly once after targeted/compatibility pass:

```powershell
.\.venv\Scripts\python.exe -m pytest -q --basetemp .\.tmp\pytest-w4r-c2a-full
```

## Tooling mode

`CONTROLLED_STAGING_ROOT_FIRST`

Use one controlled staging root containing exactly the six writable files.

One sync-back only, then immediate hash/diff/scope guard.

Planned use of controlled staging is not a tooling retry.

## Efficiency report

Report:

- actual changed files;
- additions/deletions;
- semantic correction cycles;
- unexpected tooling retries;
- 5HR consumption.

Pytest count is verification, not workload.

## Git

Exactly one runtime commit:

`feat(recovery): bind W4R-C2A recovery root authority`

Push once after remote divergence guard.

Then STOP reviewer.

## Denied

- W4R-C2B/D
- global Order/history scan
- duplicate account-scope semantics
- migration edits/execution
- actual PostgreSQL/V07
- A08
- broker/paper/Shioaji I/O
- production
- P7
- W4 closure/credit
- files outside exact writable set
