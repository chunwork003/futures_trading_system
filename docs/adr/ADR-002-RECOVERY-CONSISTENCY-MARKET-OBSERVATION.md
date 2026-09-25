# ADR-002：Recovery Consistency / Market Observation Identity

## 1. Status

**DECISION CHECKPOINT 1 ACCEPTED — ADR REMAINS OPEN**

- Decision date：2026-09-25。
- Runtime implementation baseline：`6b62239bca1d11543944f9f078e577e16010bcbf`。
- Runtime verification：934 passed / 4 skipped / 1 warning。
- User-observed 5HR usage：28%。
- Runtime result：TEST_PASS。
- Architecture acceptance：HOLD。
- 35 leaves / weight 151：IMPLEMENTED CANDIDATE，NOT ACCEPTED。
- Accepted decisions in this checkpoint：R-01、R-02、R-03A、R-03B。
- Still open：R-03C、R-03D、R-04；R-12/R-13/K520 remain linked dependencies。
- No further runtime execution is authorized by this ADR。

## 2. Why Acceptance Is On Hold

GAP-08EFGHI runtime completed and regression passed，but post-runtime architecture review found safety/recovery semantics that were either underspecified or not fully implemented。

Known correction categories include：

- missing expected snapshot was treated as FLAT。
- account recovery exception isolation was not explicit。
- no durable account recovery checkpoint / contiguous account revision head。
- broker submission is not yet orchestrated behind durable sequence-0 PENDING evidence。
- StrategyStateSnapshot and execution persistence are not yet wired into one causal runtime boundary。
- market observation identity is only placeholder text in recovery tests。
- canonical Order / Fill / OrderEvent runtime fields and transition/invariant details drift from frozen architecture。
- R-04 non-terminal broker discovery/reconciliation remains required for production-safe recovery。

Therefore runtime commit is retained as the implementation baseline，not reverted，but GAP-08EFGHI is not accepted yet。

## 3. R-01 — Expected State Initialization / Read Semantics

Status：DECIDED / IMPLEMENTATION_CORRECTION_REQUIRED。

### 3.1 Expected-state taxonomy

Persisted expected state must distinguish：

- NOT_INITIALIZED：query succeeded and no expected-state authority exists。
- EXPLICIT_FLAT：an actual persisted complete snapshot exists with positions=()。
- EXPECTED_POSITIONS：an actual persisted complete non-empty snapshot exists。

READ_FAILURE is not a domain state。

Persistence read failure must raise typed ExpectedStateReadError and must never become NOT_INITIALIZED or FLAT。

Checkpoint-reference corruption must raise ExpectedSnapshotIntegrityError and is strictly more severe than NOT_INITIALIZED。

### 3.2 Recovery boundary / blast radius

Minimum recovery isolation scope is BrokerAccount：(broker, account_ref)。

- NOT_INITIALIZED -> BrokerAccount HALT。
- ExpectedStateReadError -> BrokerAccount HALT。
- ExpectedSnapshotIntegrityError -> BrokerAccount HALT + integrity incident。
- one account failure must not automatically terminate recovery of independent accounts。
- shared dependency failure may naturally halt multiple accounts。

Account recovery boundary itself must catch typed account-state read failures and return a scoped RecoveryResult；caller must not be relied upon to provide safety isolation。

### 3.3 Expected-state authority

- missing snapshot != FLAT。
- recovery must never synthesize FLAT from missing persistence。
- every material expected-state change appends a complete AccountPositionSnapshot。
- transition to FLAT must append positions=()。
- no expected-state change does not require a duplicate snapshot。
- reconciliation compares/audits state and never mutates expected state。

### 3.4 Explicit initialization

Initialization is an explicit high-risk action from NOT_INITIALIZED only。

Single canonical TradingEvent：EXPECTED_STATE_INITIALIZED。

mode：

- FLAT。
- BROKER_SEED。

Payload/evidence includes at least：

- mode。
- broker_observation_id。
- seeded_positions。
- confirmed_by。
- confirmed_at。
- reason。

Validation：

- mode=FLAT iff seeded_positions=()。
- mode=BROKER_SEED requires non-empty seeded_positions。
- BROKER_SEED seeded_positions must exactly match a fresh persisted broker observation。
- BROKER_SEED reason is mandatory and nonblank。
- FLAT reason may be optional。
- confirmed_by is mandatory/nonblank and must not be silently supplied by trading core/system default。

Fresh BrokerPositionObservation + EXPECTED_STATE_INITIALIZED TradingEvent + first expected snapshot must commit atomically。

Initialization must atomically enforce NOT_INITIALIZED as a precondition；no check-then-unconditional-insert TOCTOU path。

Idempotency is account-scoped using stable Event Ledger identity；one BrokerAccount may have only one successful canonical initialization transition。

Same retry may deduplicate；different concurrent initialization content must conflict。

READ_FAILURE and integrity failure can never enter initialization fallback。

Broker actual query failure must be a typed failure and must not be converted to empty positions。

### 3.5 Production gate

Both FLAT and BROKER_SEED production initialization depend on R-04 proving unresolved/non-terminal broker execution has been checked。

BROKER_SEED additionally depends on R-13 operator authorization/approval runtime contract。

Until R-13 exists，BROKER_SEED production/live use is default-deny；paper/sandbox verification only。

R-13 maps to existing L610/L710/L750 and N310/N410/N430/N440/N450/N460 architecture；it is not a parallel authorization domain。

## 4. R-02 — Recovery Checkpoint / Causal Frontier

Status：DECIDED / IMPLEMENTATION_CORRECTION_REQUIRED / DEPENDS_ON_R-03 + R-04。

### 4.1 Two-layer recovery vector

Do not create a global synchronized checkpoint across account/execution/strategy state。

Use：

1. BrokerAccount-scoped execution/account recovery checkpoint。
2. per-StrategyInstance market-observation/state frontier。

Strategy logical state remains independent from AccountPosition authority。

### 4.2 Account revision head

Each BrokerAccount owns a transactional contiguous authority revision head。

Successful canonical OrderEvent acceptance advances the account revision exactly once。

All currently canonical lifecycle events advance revision，including no-fill terminal transitions：

- PENDING。
- SUBMITTED。
- PARTIALLY_FILLED。
- FILLED。
- CANCELLED。
- REJECTED。

No new EXPIRED or SUBMISSION_OUTCOME_UNKNOWN OrderStatus is introduced by this decision。

Only revision-advancing authority transactions may lock AccountStateHead。

Observation/audit-only writes such as BrokerPositionObservation、AccountSnapshot、ReconciliationRun must not lock/advance AccountStateHead merely because they share an account。

Lock scope is one BrokerAccount and must be held only for the short database transaction；broker network I/O must never occur while holding the lock。

### 4.3 Recovery checkpoint exact reference

Every AccountRecoveryCheckpoint exact-references the expected_snapshot_id that represents expected state at that revision。

If an event does not change expected position，the checkpoint carries forward the prior expected_snapshot_id。

Recovery must not replace an exact checkpoint reference with SELECT latest fallback。

Checkpoint exists but referenced snapshot is missing/corrupt -> ExpectedSnapshotIntegrityError -> HALT + integrity incident；bootstrap/reconstruction-from-broker is forbidden。

### 4.4 Durable PENDING before broker side effect

Execution external-side-effect boundary begins at durable canonical sequence-0 PENDING。

Required order：

1. validate intent/risk/account prerequisites。
2. commit initial canonical PENDING evidence / initial order projection / account revision checkpoint。
3. release database transaction/lock。
4. only then call broker API。
5. persist later broker status/fills as new canonical events/revisions。

Crash before durable PENDING means no broker call may have happened by contract。

Crash after durable PENDING but before known broker outcome is an unresolved/non-terminal execution and must not be blindly retried。

Unresolved/non-terminal execution is a recovery-time derived classification，not a new OrderStatus。

At minimum it includes persisted status in PENDING / SUBMITTED / PARTIALLY_FILLED without later canonical terminal evidence；exact broker discovery/remediation rules belong to R-04。

Transport failure classification and whether a request definitely never reached broker also belong to R-04。

### 4.5 Strategy / execution causal UoW

Pure strategy-state persistence does not lock or advance AccountStateHead。

For an observation cycle that emits material strategy outputs feeding a broker-bound OrderIntent，the material-emitting strategy snapshots and sequence-0 PENDING causal boundary must commit atomically。

Material-emitting set means StrategyInstances that emitted non-HOLD/material outputs during the cycle and whose outputs were accepted as inputs to the material Decision Layer result。

HOLD-only strategies are not pulled into the execution atomic boundary solely because they were evaluated。

The purpose is crash consistency，not merging StrategyPosition and AccountPosition authority。

Any failure/conflict inside that causal UoW rolls back the whole unit。

Partial component retry is forbidden。

After rollback，the system may restart from the previous durable boundary and rerun the complete observation -> strategy -> decision -> initial PENDING flow；it must not patch only the missing persistence component。

### 4.6 ExecutionTriggerRef

Initial durable execution evidence must retain a queryable tuple/list of minimal crash/audit backlinks：

ExecutionTriggerRef：

- strategy_instance_id。
- strategy_snapshot_id。
- market_observation_id。

This records which durable material-emitting strategy state transitions crossed the same execution side-effect boundary。

It does not replace K810-K840 full Signal/Decision/Risk attribution provenance。

### 4.7 Cross-layer recovery consistency

Wall-clock ordering between StrategyStateSnapshot and AccountRecoveryCheckpoint is not itself a safety rule。

A strategy snapshot may be newer or older in wall-clock time than account checkpoint without being inconsistent。

READY requires：

- account/event/projection frontier internally consistent。
- exact expected snapshot reference valid。
- broker actual reconciled。
- no unresolved execution requiring R-04 action。
- required StrategyStateSnapshot valid at its own market observation boundary。

Pre-PENDING decision provenance is not claimed by GAP-08；full provenance remains K810-K840。

## 5. R-03A — Market Observation Logical Key

Status：DECIDED / IMPLEMENTATION_CORRECTION_REQUIRED / DEPENDS_ON_D340。

Canonical logical observation identity represents market time locus，not payload revision。

MarketObservationLogicalKey fields：

- instrument_id。
- contract_id where a listed-contract dimension exists。
- normalized canonical timeframe。
- interval_start_at as timezone-aware UTC inclusive interval start。

Logical key explicitly excludes：

- OHLCV / amount / counts。
- trade_date。
- session/session_ref。
- source/provenance。
- symbol/exchange display values。
- ingestion time。
- content revision。

Same logical key remains the same observation locus even if payload/classification is later corrected。

### 5.1 Time semantics

Legacy ambiguous timestamp must map through one canonical interval_start_at rule。

For current intraday aggregation this corresponds to left/bucket-start semantics。

Input must be timezone-aware and normalized before identity construction。

Daily-or-coarser intervals are not magically immune to calendar changes；their interval_start_at derivation depends on D340 session/calendar semantics and inherits that rule stability。

### 5.2 Timeframe semantics

Identity construction accepts only canonical normalized timeframe values；source aliases such as semantically equivalent 1m/60s forms must not create distinct keys。

### 5.3 Listed futures / synthetic series

Listed future observation requires a resolved canonical contract_id。

Missing/unresolvable listed-future contract_id must reject or quarantine the observation；it must never silently fall back to contract_id=None。

contract_id=None is reserved for instruments where no listed-contract dimension legitimately exists。

Synthetic/continuous/front-series aliases such as TXFR1 do not receive operational canonical observation identity until a canonical series identity contract exists。

Backtests using synthetic/continuous series therefore do not provide R-02/R-03 production recovery/audit safety evidence and must not be represented as such。

## 6. R-03B — Observation Revision / Content Identity

Status：DECIDED / IMPLEMENTATION_CORRECTION_REQUIRED。

### 6.1 Hybrid revision representation

Each accepted immutable observation revision contains：

- logical key。
- authority-local monotonic revision_seq。
- deterministic content_fingerprint。
- supersedes revision reference where applicable。

revision_seq orders accepted revisions inside one canonical authority/store only；it is not a cross-environment identity。

Cross-environment exact-content comparison uses logical key + deterministic content fingerprint。

### 6.2 Fingerprinted payload

Fingerprint covers canonical strategy-visible market semantics，not storage/source provenance。

market_data_fields include at least：

- open/high/low/close。
- volume。
- amount when canonical/present。
- trade_count/tick_count when canonical/present。

classification_fields include：

- trade_date。
- session/session_ref。

Exclude source URL/file/batch、ingested_at、database row ID、Parquet filename、broker-native object and arbitrary feature payload。

### 6.3 Change class

Accepted revision differences are classified：

- MARKET_DATA_REVISION：one or more market_data_fields changed。
- CLASSIFICATION_REVISION：only classification_fields changed。

MARKET_DATA_REVISION affecting the required recovery state horizon prevents automatic READY and produces REVIEW。

CLASSIFICATION_REVISION does not automatically block READY only when an explicit/verified strategy dependency contract proves the changed classification fields are non-material to that StrategyInstance decision/state semantics。

Unknown dependency、missing declaration、or an actually consumed classification field -> REVIEW。

No global assumption that all future strategies ignore classification fields is allowed。

### 6.4 Canonical numeric serialization

Raw Python/JSON float representation must not define content fingerprint identity。

Price/market numeric values require one exact canonical numeric normalization / serialization rule before hashing。

No silent rounding may be used merely to force fingerprints to match。

### 6.5 Revision authority and concurrency

Source adapters submit candidates and provenance；they do not assign accepted canonical revision_seq。

Canonicalization authority decides whether a candidate becomes an accepted canonical revision。

Revision serialization/locking granularity is one logical observation key；a global canonical-store lock is forbidden。

Concurrent unrelated instruments/timeframes must not serialize behind one store-wide revision lock。

### 6.6 Replay / conflict

Same logical key + same content_fingerprint is an idempotent duplicate and does not allocate another revision_seq。

Same logical key + different fingerprint is a revision candidate，not automatically accepted last-write-wins。

If authority policy cannot select/accept a candidate，the logical observation becomes CONFLICT/QUARANTINE。

Direct quarantine blast radius is the logical observation key：(instrument_id, contract_id, timeframe, interval_start_at)。

All StrategyInstances consuming that observation may not treat it as material market evidence while quarantined，regardless of BrokerAccount。

Market-observation quarantine scope and BrokerAccount recovery scope are orthogonal isolation axes。

Propagation into derived bars/features requires later provenance/dependency rules and must not be silently assumed safe。

### 6.7 Strategy / execution evidence reference

StrategyStateSnapshot.last_market_observation_id and R-02 ExecutionTriggerRef.market_observation_id must resolve to an immutable revision-specific accepted observation evidence record，not merely the logical key。

Exact final ID encoding remains R-03C。

### 6.8 Superseded consumed evidence

Historical evidence is immutable。

If revision 2 supersedes revision 1，existing StrategyStateSnapshot / Order trigger references to revision 1 are never rewritten to revision 2。

Accepted MARKET_DATA_REVISION within the required reconstructed state horizon -> automatic READY forbidden -> REVIEW。

CLASSIFICATION_REVISION uses the dependency rule in 6.3。

Missing/corrupt referenced revision is an integrity failure/HALT，not REVIEW。

Until K520 feature-state provenance can prove an older corrected observation is irrelevant，unknown impact inside the required feature/state horizon is handled conservatively as REVIEW。

### 6.9 REVIEW release

Production REVIEW release/approval belongs to R-13 operator authorization/approval runtime contract。

Until R-13 is implemented，production release from these REVIEW states is default-deny；paper/sandbox workflow testing only。

## 7. Open Decisions After Checkpoint 1

R-03C — revision-specific MarketObservation ID encoding / canonical value object。

R-03D — cross-environment canonicalization / source authority / correction acceptance policy。

R-04 — non-terminal broker order discovery / submission outcome reconciliation / safe remediation。

R-12 — ReconciliationRun audit contract。

R-13 — Operator Authorization / Approval Runtime Contract mapped to existing L/N Blueprint。

K520 — incremental feature/state provenance required for exact historical correction impact horizon。

## 8. Runtime Correction Items Already Identified

These are not new design choices unless a later decision explicitly changes them：

- canonical Order/Fill/OrderEvent runtime fields must be reconciled to frozen contracts。
- PENDING direct PARTIALLY_FILLED/FILLED legal transitions must match architecture。
- status/filled_quantity invariants must be fully enforced。
- occurred_at and received_at must remain distinct evidence semantics。
- missing expected snapshot must not become FLAT。
- recovery must use exact account checkpoint/snapshot references。
- production broker submission orchestration must commit initial PENDING before broker I/O。
- StrategyStateSnapshot persistence must be integrated with material execution causal boundary。

## 9. Consequence

Runtime commit remains a useful implementation baseline and is not reverted。

However GAP-08EFGHI cannot move to ACCEPTED until open recovery/identity dependencies are decided and the bounded correction runtime passes targeted/compatibility/full-regression verification。

No LIVE authorization is implied。