# GAP-08 Bounded Runtime Authorization — C24

## 1. Authorization Status

BOUNDED_RUNTIME_AUTHORIZED。

Authorized leaf：

C24 — Operational MarketObservation Evidence / Acceptance。

No other correction / implementation / verification leaf is authorized。

---

## 2. Baselines

Architecture Decision Baseline：

`22ceaa729ab6e9da9c00ae52e09ae7116be5a743`

Correction-Freeze Baseline：

`93fb846a9c9cd61eea44427a86a542fc95f9ac28`

Previous completed bounded execution：

`docs/work/GAP08_C23_CLOSURE.md`

C23 Closure Baseline：

`1116a5d722dd7d4b1c1eac7a6956ae927ac100f5`

Authorization Baseline：

the docs-only commit containing this authorization envelope。

---

## 3. Frozen C24 Contract

C24 PASS requires：

- candidate/provenance evidence separated from accepted revision。
- explicit versioned MarketObservationAcceptancePolicy。
- per-logical-key accepted revision ordering。
- authority-local contiguous revision_seq。
- database-enforced atomic uniqueness。
- explicit duplicate vs integrity-conflict classification。
- conflict/quarantine evidence。
- immutable evidence history。
- mutable logical-key head only as concurrency/current-state projection。

C24 MUST NOT implement：

- last-write-wins。
- newest-arrival-wins。
- majority vote。
- source tier automatically becomes price truth。
- routing PRIMARY automatically becomes truth authority。
- application SELECT-if-missing -> INSERT as uniqueness authority。
- silent identity-collision retry。
- regenerated/salted mor1 ID。
- strategy delivery before C25。
- StrategyStateSnapshot revision-reference migration。

---

## 4. C23 Dependency

C23 is COMPLETE / VERIFIED。

C24 MUST consume the C23 canonical primitives：

- `MarketObservationLogicalKey`
- `CanonicalMarketObservationContent`
- `MarketObservationContentFingerprint`
- `MarketObservationRevisionId`

C24 MUST NOT redefine：

- logical-key semantics。
- decimal normalization。
- timeframe normalization。
- UTC normalization。
- content fingerprint。
- mor1 construction。

`domain/market_observation.py` is read-only compatibility input for C24。

Modification of that file is NOT_AUTHORIZED。

---

## 5. Versioned Acceptance Policy

C24 introduces an explicit immutable/versioned：

`MarketObservationAcceptancePolicy`

Minimum policy identity：

- policy_id。
- version。
- scope_ref。

Minimum source-policy rule semantics：

- source_id。
- evidence_eligible。
- can_seed_initial_truth。
- authoritative_for_scope。
- can_accept_formal_correction。

Routing role and truth authority MUST remain separate。

Candidate routing roles may include：

- PRIMARY。
- SECONDARY。
- VALIDATION。

Routing role alone MUST NOT authorize canonical truth。

Source Registry S0/S1/S2 documentation tier MUST NOT be used as market-price truth precedence。

Policy version/context MUST be retained for audit but MUST NOT enter mor1 identity。

Changing policy MUST NOT rewrite historical accepted evidence。

---

## 6. Candidate Evidence

C24 introduces immutable：

`MarketObservationCandidateEvidence`

Candidate evidence must retain at least：

- candidate_id。
- logical_key。
- canonical content。
- content_fingerprint。
- observation_revision_id。
- source_id。
- routing_role。
- source_record_ref when present。
- formal_correction_ref when present。
- received_at。
- provenance_json。
- exact acceptance-policy identity used for evaluation or decision linkage。

Candidate evidence and accepted revision are separate records。

Candidate persistence does NOT imply acceptance。

Provenance-only changes MUST NOT create a new accepted content revision。

No local-now fallback may be fabricated for missing source occurrence semantics。

---

## 7. Accepted Revision

C24 introduces immutable：

`MarketObservationRevision`

Accepted revision retains structured canonical evidence：

- observation_revision_id。
- logical key fields。
- content schema version。
- canonical content fields。
- content_fingerprint。
- revision_seq。
- supersedes_revision_id when applicable。
- accepted_at。
- acceptance_policy_id。
- acceptance_policy_version。
- acceptance_scope_ref。

Accepted revision source/provenance corroboration remains separate evidence。

One opaque mor1 ID MUST NOT replace structured query columns。

---

## 8. Same-Content Semantics

For an evidence-eligible candidate where canonical logical key and content fingerprint match an existing accepted revision：

    CORROBORATE_EXISTING

Required effects：

- persist candidate evidence。
- link candidate evidence to existing accepted revision。
- append decision/audit evidence。
- do NOT create a new accepted revision。
- do NOT advance revision_seq。
- do NOT change mor1 identity。
- do NOT change revision head solely because provenance changed。

Applies to：

- same source + same content。
- different source + same content。
- re-ingestion + same content。
- newer provenance metadata + same content。

---

## 9. Initial Acceptance

Where no accepted revision exists for the logical key：

automatic first acceptance requires：

- candidate canonical validation already passed through C23。
- source is evidence-eligible。
- policy explicitly grants `can_seed_initial_truth`。
- current policy scope matches the supplied acceptance context。
- per-key head precondition succeeds atomically。

Successful initial accepted revision：

    revision_seq = 1

Routing PRIMARY alone is insufficient。

---

## 10. Different-Content Correction

Different content MUST NOT be accepted because it arrived later。

Automatic correction requires all of：

- evidence_eligible source。
- policy authorizes source for formal correction。
- explicit nonblank formal_correction_ref。
- canonical C23 validation passes。
- exact current revision-head precondition succeeds。
- database transaction atomically advances revision head。

Successful correction：

    revision_seq = previous + 1

and：

    supersedes_revision_id = exact previous accepted revision

If proof/policy is insufficient：

    QUARANTINE_CONFLICT

No accepted revision is created。

Current accepted revision is not overwritten。

---

## 11. AUTHORITATIVE_FOR_SCOPE Boundary

`authoritative_for_scope` is an explicit policy fact。

It is NOT inferred from：

- PRIMARY routing。
- source registry documentation tier。
- arrival order。
- historical success。
- majority agreement。

`authoritative_for_scope` alone does NOT waive formal-correction proof。

A conflicting validation candidate may be retained as discrepancy evidence while the previous accepted revision remains the accepted revision。

The logical key may still enter QUARANTINED operational state until policy-resolved evidence exists。

---

## 12. Quarantine / Conflict

C24 introduces explicit operational decision evidence such as：

- ACCEPTED_NEW_REVISION。
- CORROBORATED_EXISTING。
- QUARANTINED_INELIGIBLE_SOURCE。
- QUARANTINED_UNPROVEN_CORRECTION。
- QUARANTINED_CROSS_SOURCE_CONFLICT。
- IDENTITY_CONFLICT。

Exact names may vary if semantic meaning remains explicit and typed。

Quarantine scope：

MarketObservationLogicalKey。

Quarantine MUST NOT mutate/delete historical candidate or accepted evidence。

A quarantined key is NOT strategy-consumable material evidence。

Downstream Strategy/Data review propagation is NOT implemented by C24；that belongs to later authorized work。

---

## 13. Identity Conflict

C24 must implement typed integrity failures：

- MarketObservationIdentityConflictError or equivalent。
- MarketObservationCandidateConflictError or equivalent。
- MarketObservationPolicyConflictError or equivalent where immutable policy identity conflicts。

When database atomic insertion reports an existing observation_revision_id：

repository must compare persisted structured canonical identity/content evidence。

If exact same evidence：

    IDEMPOTENT / DUPLICATE

If different canonical evidence under same mor1：

    IDENTITY_CONFLICT

Required behavior：

- quarantine affected logical key。
- preserve evidence。
- no retry as ordinary duplicate。
- no new/salted mor1 ID。
- no automatic READY claim。

---

## 14. PostgreSQL Atomicity

V1 operational implementation family：

PostgreSQL。

C24 migration creation is authorized：

NEW：

`persistence/postgres/migrations/0003_market_observation_evidence.sql`

Historical migrations：

- 0001 MUST NOT be modified。
- 0002 MUST NOT be modified。

Migration execution：

NOT_AUTHORIZED。

Required database uniqueness includes conceptually：

1. unique observation_revision_id。
2. unique logical key + content schema version + content fingerprint。
3. unique logical key + revision_seq。
4. unique versioned policy identity。
5. unique candidate identity。
6. unique logical-key head。

Nullable contract_id MUST still participate in logical-key uniqueness semantics。

PostgreSQL 17/18 compatible `NULLS NOT DISTINCT` or an equivalent explicit representation may be used。

---

## 15. Required Operational Tables

The 0003 migration must provide equivalent operational structures for：

- immutable acceptance-policy evidence。
- immutable candidate evidence。
- immutable accepted revisions。
- immutable candidate decision history。
- immutable candidate-to-revision evidence/corroboration links。
- mutable per-logical-key revision/quarantine head。

Suggested table family：

- `market_observation_acceptance_policies`
- `market_observation_candidates`
- `market_observation_revisions`
- `market_observation_candidate_decisions`
- `market_observation_revision_evidence`
- `market_observation_heads`

Exact table names may differ only if the same authority boundaries remain explicit。

All important TABLE / COLUMN semantics require Traditional Chinese PostgreSQL COMMENT text。

---

## 16. Atomic Write Pattern

Application-level：

    SELECT
    -> if missing
    -> INSERT

is forbidden as uniqueness authority。

Permitted pattern：

    INSERT ... ON CONFLICT DO NOTHING RETURNING ...

followed by exact persisted canonical comparison when conflict classification is required。

For per-logical-key revision sequencing：

1. atomically ensure logical-key head exists using database uniqueness。
2. lock exact logical-key head using `SELECT ... FOR UPDATE`。
3. evaluate exact current accepted revision/head state。
4. persist candidate/decision/revision/link evidence。
5. advance head only for a newly accepted revision。
6. caller-owned UoW commits。

Repositories MUST NOT call commit/rollback。

No network I/O may occur while a logical-key head lock is held。

---

## 17. Transaction Boundary

C24 runtime uses existing caller-owned：

`PostgresUnitOfWork`

No new transaction authority is created。

Evidence acceptance for one candidate must be crash-consistent。

The successful unit must atomically preserve the applicable combination of：

- candidate evidence。
- policy evidence/reference。
- candidate decision。
- accepted revision when created。
- corroboration/evidence link when applicable。
- logical-key head update when applicable。

A failed transaction MUST NOT leave a partially accepted revision sequence。

---

## 18. Runtime Scope

Authorized NEW runtime files：

- `domain/market_observation_acceptance.py`
- `persistence/market_observation.py`
- `persistence/postgres/market_observation.py`
- `persistence/postgres/migrations/0003_market_observation_evidence.sql`

Authorized NEW tests：

- `tests/unit/test_market_observation_acceptance.py`
- `tests/unit/test_market_observation_postgres.py`

Existing runtime modules are NOT_AUTHORIZED_FOR_MODIFICATION。

In particular：

- `domain/market_observation.py`
- `domain/bars.py`
- `backtest/market_data.py`
- `backtest/paper_market_data.py`
- `persistence/postgres/uow.py`
- `persistence/strategy_state.py`
- `persistence/postgres/strategy_state.py`
- `trading/*`
- all broker adapters。

If C24 requires an existing runtime-module semantic change：

STOP。

Do not widen scope。

---

## 19. C25 Boundary

C25 remains NOT_AUTHORIZED。

C24 MUST NOT modify：

- `StrategyStateSnapshot.last_market_observation_id`
- `StrategyStateSnapshot` recovery authority。
- `ExecutionTriggerRef`
- strategy delivery orchestration。
- paper/live strategy-consumption path。

C24 proves durable accepted observation evidence exists。

C25 later enforces：

    durable accepted revision
        -> strategy delivery
        -> exact revision-specific recovery/audit references

No C24 test may claim C25 completion。

---

## 20. R14 / K520 Boundary

C24 does NOT prove market-data completeness。

No-candidate interval semantics remain R14 / GAP-DATA-001。

C24 MUST NOT infer：

    no candidate == legitimate no-trade interval

K520 incremental feature/state provenance remains GAP-09-owned。

C24 MUST NOT absorb either dependency。

---

## 21. Manual Resolution Boundary

Production manual candidate acceptance/source selection/quarantine release：

NOT_AUTHORIZED。

R-13 production authorization/approval runtime is not implemented by C24。

C24 may model durable decision evidence required for future manual resolution。

It MUST NOT expose a production bypass such as：

- force_accept=True。
- actor string == authorization。
- reason string == authorization。
- ignore_quarantine=True。

Production manual resolution remains DEFAULT DENY。

---

## 22. Positive Acceptance Tests

Pure acceptance-policy tests must prove at least：

1. first eligible seed candidate -> accepted revision seq 1。
2. routing PRIMARY alone does not grant truth authority。
3. same-source same-content -> corroboration / no new revision。
4. different-source same-content -> corroboration / no new revision。
5. re-ingestion same content is idempotent。
6. provenance-only change does not advance revision_seq。
7. different content without formal proof -> quarantine。
8. different content with explicit authorized formal-correction proof -> next contiguous revision。
9. accepted correction supersedes exact previous revision。
10. source tier/routing role does not become truth precedence。
11. policy version change does not rewrite prior accepted evidence。
12. quarantine preserves prior accepted revision evidence。

---

## 23. PostgreSQL Acceptance Tests

Repository/migration tests must prove at least：

1. new migration version is 0003。
2. 0001/0002 unchanged。
3. required evidence/head tables exist。
4. important tables/columns have Traditional Chinese COMMENT statements。
5. candidate/revision/decision/evidence history is not updated/deleted in normal repository code。
6. revision ID uniqueness is database-enforced。
7. logical-key + fingerprint uniqueness is database-enforced。
8. logical-key + revision_seq uniqueness is database-enforced。
9. nullable contract_id cannot bypass logical-key uniqueness。
10. head uniqueness is database-enforced。
11. revision sequencing uses exact head lock / `FOR UPDATE`。
12. no SELECT-if-missing -> unconditional INSERT uniqueness pattern。
13. repository never commits/rolls back。
14. exact duplicate is distinguished from identity conflict。
15. same-content corroboration does not create a new accepted revision。
16. conflict/quarantine does not overwrite current accepted revision。

---

## 24. Compatibility Tests

Read-only compatibility:

- `tests/unit/test_market_observation_identity.py`
- `tests/unit/test_postgres_foundation.py`
- `tests/unit/test_operational_postgres.py`
- `tests/unit/test_strategy_state_recovery.py`

These files are NOT authorized for modification in C24。

External PostgreSQL integration tests remain disabled unless DSNs are explicitly authorized later。

---

## 25. Environment / Side Effects

Migration file creation：

AUTHORIZED_FOR_0003_ONLY。

Migration execution：

NOT_AUTHORIZED。

Actual PostgreSQL 17：

NOT_AUTHORIZED。

Actual PostgreSQL 18：

NOT_AUTHORIZED。

V07：

NOT_AUTHORIZED。

Broker network I/O：

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

- C24 requires changing C23 canonical identity semantics。
- existing MarketBar must be modified。
- StrategyStateSnapshot must be modified。
- ExecutionTriggerRef must be modified。
- strategy delivery orchestration becomes necessary。
- actual PostgreSQL execution is required。
- migration 0001/0002 would need rewriting。
- acceptance requires unresolved source-specific market semantics。
- automatic correction cannot be proven from explicit policy + evidence。
- production manual resolution becomes necessary。
- R14 completeness semantics become necessary。
- K520 semantics become necessary。
- more than two scope-internal correction cycles are required。
- unrelated full-regression failure exposes architecture contradiction。

---

## 27. Execution Sequence

    exact Authorization Baseline precheck
    -> inspect C23 primitives + persistence foundation
    -> create acceptance-policy domain
    -> create storage-neutral evidence/repository contract
    -> create PostgreSQL evidence adapter
    -> create NEW 0003 migration
    -> targeted pure acceptance tests
    -> targeted PostgreSQL contract tests
    -> C23/persistence/strategy compatibility
    -> full regression
    -> exact diff validation
    -> commit
    -> push
    -> final report
    -> STOP

Suggested runtime commit：

`feat(persistence): add market observation acceptance evidence`

No amend。

No rebase。

No force push。

After C24：

STOP。

Do not automatically start C25、C02、V05 or V07。

A docs-only C24 closure is required before the next runtime authorization。
