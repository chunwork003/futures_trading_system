# GAP-08 Bounded Runtime Authorization — C25

## 1. Authorization Status

BOUNDED_RUNTIME_AUTHORIZED。

Authorized leaf：

C25 — Durable-before-Strategy Delivery / Revision Ref Migration。

No other correction / implementation / verification leaf is authorized。

---

## 2. Baselines

Architecture Decision Baseline：

`22ceaa729ab6e9da9c00ae52e09ae7116be5a743`

Correction-Freeze Baseline：

`93fb846a9c9cd61eea44427a86a542fc95f9ac28`

Previous completed bounded execution：

`docs/work/GAP08_C24_CLOSURE.md`

C24 Closure Baseline：

`ce241cf01418c9d67a28bf112d0d906b45143c89`

Authorization Baseline：

the docs-only commit containing this authorization envelope。

---

## 3. Frozen C25 Acceptance Boundary

C25 PASS requires：

- recovery-capable strategy consumes only durable accepted MarketObservationRevision evidence。
- strategy callback/processing occurs only after the accepted observation transaction has committed。
- `StrategyStateSnapshot.last_market_observation_revision_id` is the canonical recovery authority。
- `ExecutionTriggerRef.market_observation_revision_id` is the canonical execution/audit observation authority。
- exact revision-specific references use C23 `MarketObservationRevisionId` semantics。
- bounded compatibility migration prevents arbitrary legacy ID from remaining recovery authority。
- legacy/canonical disagreement is typed integrity failure / recovery HALT。
- no arbitrary legacy observation ID is silently converted into a mor1 ID。

C25 MUST NOT：

- deliver a candidate/quarantined/non-durable observation to a recovery-capable strategy。
- deliver before successful UoW commit。
- treat candidate persistence as accepted-revision durability。
- treat legacy `last_market_observation_id` as recovery authority after canonical writer exists。
- silently choose legacy value when legacy/canonical references disagree。
- fabricate a canonical mor1 ID from BAR IDs、timestamps、symbols or row identity。
- absorb C05 durable initial PENDING semantics。
- absorb C18 strategy readiness composition。
- claim R14 completeness。
- implement K520。
- execute migration 0004。
- access actual PostgreSQL。

---

## 4. C23 / C24 Dependencies

C23：

COMPLETE / VERIFIED。

C24：

COMPLETE / VERIFIED。

C25 consumes the existing canonical concepts：

- `MarketObservationRevisionId`
- `MarketObservationRevision`
- accepted/quarantined C24 result semantics。
- caller-owned `PostgresUnitOfWork` transaction authority。

C25 MUST NOT redefine：

- mor1 construction。
- canonical market-observation identity。
- acceptance-policy semantics。
- revision_seq allocation。
- quarantine semantics。

C23 and C24 semantics are read-only dependencies unless a C25-specific read port extension is explicitly authorized below。

---

## 5. Durable-before-Strategy Ordering

Required recovery-capable paper/live ordering：

    source/candidate
        -> canonical C23 identity
        -> C24 acceptance transaction
        -> accepted revision evidence durable
        -> UoW commit success
        -> exact accepted revision resolution
        -> strategy delivery

Forbidden：

    candidate
        -> strategy
        -> best-effort persistence

Forbidden：

    C24 process_candidate(...)
        -> strategy callback
        -> UoW commit

Commit failure MUST prevent strategy delivery。

Quarantine/conflict MUST prevent material strategy delivery。

Durability latency is accepted by frozen architecture and MUST NOT be bypassed for convenience。

---

## 6. Accepted Revision Resolution

C25 may extend the storage-neutral C24 repository contract with an exact immutable read seam such as：

`get_revision(observation_revision_id) -> MarketObservationRevision | None`

or semantically equivalent。

PostgreSQL implementation must read by exact：

`observation_revision_id`

No：

- latest fallback。
- logical-key latest substitution。
- content fingerprint heuristic。
- candidate fallback。

A missing exact accepted revision after commit is an integrity failure and MUST block delivery。

---

## 7. Durable Delivery Coordinator

C25 may introduce a bounded orchestration primitive such as：

`DurableMarketObservationStrategyDelivery`

or semantically equivalent。

Its responsibility is limited to：

1. execute/obtain C24 acceptance result inside caller-owned transaction。
2. commit accepted/corroborated durable evidence。
3. reject quarantine/integrity-conflict delivery。
4. resolve exact accepted revision by revision-specific ID。
5. invoke recovery-capable strategy consumer only after commit。
6. return exact revision-specific trigger/reference evidence。

It MUST NOT：

- submit broker orders。
- create sequence-0 PENDING。
- decide account position。
- bypass Decision Layer。
- implement strategy cohort readiness。
- repair quarantined market evidence。

---

## 8. StrategyStateSnapshot Canonical Reference

Canonical target field：

`last_market_observation_revision_id`

Canonical type/validation：

C23 `MarketObservationRevisionId` or semantically exact mor1 value-object validation。

For newly written snapshots：

- canonical revision field is REQUIRED。
- it is the sole recovery authority。
- it must refer to an accepted durable revision。
- arbitrary free-form BAR IDs are forbidden。

Legacy name：

`last_market_observation_id`

may remain only as a bounded compatibility read surface。

For new in-memory snapshots it may project the canonical mor1 value for unaffected read callers。

It MUST NOT become a second independent authority field。

---

## 9. PostgreSQL Strategy Snapshot Compatibility

Current 0002 schema contains：

`last_market_observation_id`

C25 MUST NOT rewrite migration 0002。

C25 creates NEW migration：

`0004_strategy_market_observation_revision_ref.sql`

Minimum migration direction：

- add `last_market_observation_revision_id` to `trading.strategy_state_snapshots`。
- canonical column references accepted `trading.market_observation_revisions(observation_revision_id)` or equivalent database integrity constraint。
- preserve historical legacy column for bounded compatibility。
- do NOT invent canonical IDs for existing legacy rows。
- existing rows lacking canonical revision remain legacy/non-authoritative for recovery。
- new writer must persist canonical revision-specific reference。
- new writer may mirror canonical mor1 value into legacy compatibility column where required by old schema constraints。

Migration may keep the new canonical column nullable for historical compatibility if existing legacy rows cannot be safely backfilled。

Runtime writer/recovery rules—not fabricated migration data—must enforce canonical authority for new recovery-capable writes。

---

## 10. Legacy / Canonical Conflict Semantics

When persisted structured columns expose both：

- legacy `last_market_observation_id`
- canonical `last_market_observation_revision_id`

newly written rows MUST keep them equal where the legacy non-null column is still required。

If both are present and values differ：

typed integrity failure is required。

Suggested error family：

- `LegacyMarketObservationReferenceError`
- `StrategyStateReferenceConflictError`

or precise semantic equivalents。

Recovery consequence：

HALT。

MUST NOT：

- pick canonical and ignore disagreement。
- pick legacy and ignore disagreement。
- SELECT latest observation as repair。
- hash legacy value into a mor1 ID。

Existing rows where canonical reference is NULL are legacy-only evidence and MUST NOT satisfy canonical recovery authority。

---

## 11. Recovery Contract Migration

Canonical recovery input name：

`required_market_observation_revision_id`

Recovery compares exact canonical revision-specific reference：

    snapshot.last_market_observation_revision_id
        ==
    required_market_observation_revision_id

Legacy free-form `required_market_observation_id` MUST NOT remain independent recovery authority。

If a compatibility shim is required for an unaffected caller：

- it may accept only an already-valid mor1 revision-specific value。
- it must normalize into the single canonical argument。
- simultaneous conflicting legacy/canonical values MUST fail closed。

No arbitrary legacy ID may authorize READY。

---

## 12. ExecutionTriggerRef

C25 introduces or corrects canonical：

`ExecutionTriggerRef`

Required member：

`market_observation_revision_id`

This reference MUST use exact C23 revision-specific identity。

A recovery/audit-capable strategy-originated execution reference MUST NOT use：

- BAR-1。
- timestamp-only reference。
- symbol/timeframe tuple。
- candidate_id。
- logical-key-only reference。

A bounded optional `ExecutionTriggerRef` attachment to existing `OrderIntent` or equivalent execution provenance surface is allowed if required to make the frozen reference useful without breaking unaffected callers。

C25 MUST NOT implement C05 sequence-0 PENDING causal persistence。

---

## 13. Canonical Writer Rule

Once C25 canonical writer exists：

new recovery-capable strategy snapshots MUST write：

`last_market_observation_revision_id`

New strategy-originated execution trigger references MUST write：

`market_observation_revision_id`

Legacy arbitrary IDs are no longer authoritative。

Long-lived dual authority is forbidden。

Compatibility surface != authority surface。

---

## 14. PostgreSQL / Transaction Boundary

C25 continues to use existing：

`PostgresUnitOfWork`

C25 MUST NOT create a competing transaction authority。

Repository methods MUST NOT call commit/rollback。

Durable-before-delivery coordinator may call caller-owned UoW commit at the explicit durability boundary。

Strategy consumer invocation MUST occur only after successful commit and after leaving any lock-sensitive mutation phase。

No network I/O while C24 logical-key head lock is held。

---

## 15. Migration Rules

Authorized migration creation：

NEW：

`persistence/postgres/migrations/0004_strategy_market_observation_revision_ref.sql`

Historical migrations：

- 0001 MUST NOT be modified。
- 0002 MUST NOT be modified。
- 0003 MUST NOT be modified。

Migration execution：

NOT_AUTHORIZED。

Actual PostgreSQL 17：

NOT_AUTHORIZED。

Actual PostgreSQL 18：

NOT_AUTHORIZED。

V07：

NOT_AUTHORIZED。

---

## 16. Authorized Runtime Scope

Authorized existing runtime files：

- `trading/execution.py`
- `persistence/market_observation.py`
- `persistence/postgres/market_observation.py`
- `persistence/strategy_state.py`
- `persistence/postgres/strategy_state.py`
- `persistence/recovery.py`

Authorized NEW runtime files：

- `persistence/market_observation_delivery.py`
- `persistence/postgres/migrations/0004_strategy_market_observation_revision_ref.sql`

Authorized existing tests：

- `tests/unit/test_strategy_state_recovery.py`
- `tests/unit/test_operational_execution.py`

Authorized NEW direct tests：

- `tests/unit/test_c25_market_observation_delivery.py`
- `tests/unit/test_c25_revision_reference_migration.py`

No other runtime/test file is authorized for modification。

If C25 requires changing another runtime file：

STOP。

Do not widen scope。

---

## 17. Read-Only Compatibility Surfaces

C25 compatibility must verify without modification unless a new explicit authorization is created：

- `tests/unit/test_market_observation_identity.py`
- `tests/unit/test_market_observation_acceptance.py`
- `tests/unit/test_market_observation_postgres.py`
- `tests/unit/test_postgres_foundation.py`
- `tests/unit/test_operational_postgres.py`

C23/C24 direct tests remain authoritative compatibility evidence。

---

## 18. Required Positive Tests — Snapshot References

Tests must prove at least：

1. canonical StrategyStateSnapshot requires valid mor1 revision reference。
2. arbitrary `BAR-1` cannot become canonical recovery authority。
3. compatibility `last_market_observation_id` read surface, if retained, returns canonical mor1 only。
4. new PostgreSQL writer persists canonical revision column。
5. new writer mirrors legacy column only with the exact same canonical value when schema compatibility requires it。
6. legacy-only persisted row cannot satisfy recovery authority。
7. legacy/canonical disagreement produces typed integrity failure。
8. exact canonical revision match permits the existing recovery path to continue to its next gate。
9. canonical mismatch HALTs recovery。
10. no latest-observation fallback exists。

---

## 19. Required Positive Tests — Durable Delivery

Tests must prove at least：

1. strategy consumer is NOT invoked before commit。
2. successful accepted revision commit occurs before consumer invocation。
3. commit failure causes zero strategy delivery。
4. quarantined candidate causes zero strategy delivery。
5. integrity-conflict result causes zero strategy delivery。
6. exact accepted revision is resolved by revision ID after commit。
7. missing exact revision after commit fails closed。
8. same-content corroboration resolves/delivers the existing exact accepted revision only after durable evidence commit。
9. no broker side effect occurs。
10. no DB lock remains intentionally held across strategy callback。

---

## 20. Required Positive Tests — ExecutionTriggerRef

Tests must prove at least：

1. `ExecutionTriggerRef.market_observation_revision_id` accepts valid mor1 revision identity。
2. arbitrary free-form observation ID is rejected。
3. strategy-originated optional OrderIntent trigger provenance preserves exact revision reference if integrated。
4. legacy candidate_id/logical-key reference cannot substitute for revision identity。
5. unaffected OrderIntent callers remain compatible when trigger provenance is optional。

---

## 21. Migration Contract Tests

0004 tests must prove at least：

1. migration version is 0004。
2. 0001/0002/0003 remain unchanged。
3. canonical strategy snapshot revision column is added。
4. FK/reference targets accepted market_observation_revisions evidence。
5. migration does not fabricate/backfill arbitrary legacy IDs。
6. legacy column remains only for bounded compatibility。
7. important new TABLE/COLUMN/constraint semantics include Traditional Chinese PostgreSQL COMMENT。
8. no destructive migration/drop/rewrite。
9. migration is not executed by C25 tests。

---

## 22. C05 Boundary

C05 — Durable Initial PENDING + Causal Execution Boundary：

NOT_AUTHORIZED。

C25 may provide exact `ExecutionTriggerRef` provenance primitive。

C25 MUST NOT：

- persist sequence-0 PENDING。
- invoke broker。
- bind BrokerActionAttempt。
- implement AccountAuthorityCommit。
- claim broker-side causal durability completion。

C05 remains dependent on C25 plus C04/C08。

---

## 23. C18 Boundary

C18 — Strategy Recovery Frontier + Readiness Composition：

NOT_AUTHORIZED。

C25 may correct exact revision-reference validation in the existing recovery compatibility path。

C25 MUST NOT implement：

- BrokerAccountExecutionReady composition。
- StrategyTradingReady。
- DecisionCohortTradingReady。
- catch-up isolation。
- governing cohort authority。

---

## 24. R14 / K520 Boundary

R14 completeness：

NOT IMPLEMENTED by C25。

C25 MUST NOT interpret：

    no observation == legitimate no-trade interval

K520：

NOT IMPLEMENTED by C25。

K520 remains GAP-09-owned。

Revision-specific reference correctness does not prove completeness or feature-state irrelevance。

---

## 25. Environment / External Side Effects

Migration creation：

AUTHORIZED_FOR_0004_ONLY。

Migration execution：

NOT_AUTHORIZED。

Actual PostgreSQL：

NOT_AUTHORIZED。

V07：

NOT_AUTHORIZED。

Broker I/O：

NOT_AUTHORIZED。

Market-data network I/O：

NOT_AUTHORIZED。

Paper broker I/O：

NOT_AUTHORIZED。

Production broker I/O：

NOT_AUTHORIZED。

`data/`：

MUST NOT be modified or staged。

---

## 26. Stop Conditions

STOP without widening scope if：

- C25 requires changing C23 mor1 identity semantics。
- C25 requires changing C24 acceptance/quarantine semantics。
- migration 0001/0002/0003 would require rewrite。
- arbitrary legacy IDs would need to be guessed/backfilled。
- existing strategy consumer requires a broad strategy-framework rewrite。
- ExecutionTriggerRef requires account/execution authority semantics belonging to C05。
- readiness composition requires C18。
- actual PostgreSQL execution becomes necessary。
- R14 completeness becomes necessary。
- K520 becomes necessary。
- broker/live-money semantics become necessary。
- unrelated full-regression failure exposes architecture contradiction。
- more than two scope-internal correction cycles are required。

---

## 27. Required Verification Sequence

    exact Authorization Baseline precheck
    -> inspect C24 accepted revision read needs
    -> add exact revision read seam if required
    -> implement durable-before-strategy coordinator
    -> migrate StrategyStateSnapshot canonical reference
    -> migrate PostgreSQL strategy snapshot writer/reader
    -> add ExecutionTriggerRef exact revision reference
    -> create NEW 0004 migration
    -> targeted C25 tests
    -> C23/C24 compatibility
    -> strategy/recovery/execution compatibility
    -> full regression
    -> exact diff validation
    -> commit
    -> push
    -> final report
    -> STOP

Suggested runtime commit：

`feat(recovery): enforce durable market observation references`

No amend。

No rebase。

No force push。

After C25：

STOP。

A docs-only C25 closure is required before any next leaf authorization。

---

## 28. Expected Post-C25 Planning State

C25 weight：

4。

If C25 runtime and closure PASS：

    completed / verified
    27 / 113

Remaining：

    86

Frozen P2 then becomes：

    C23 COMPLETE
        -> C24 COMPLETE
        -> C25 COMPLETE

Next phase candidate after closure：

P3 / C02 — BrokerAccount Revision Head + Exact Checkpoint。

C02 remains NOT_AUTHORIZED by this document。
