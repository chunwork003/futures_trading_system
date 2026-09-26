# ADR-002：Recovery Consistency / Market Observation Identity

## 1. Status

**DECISION CHECKPOINT 4 ACCEPTED — ADR REMAINS OPEN**

- Decision date：2026-09-25。
- Runtime implementation baseline：`6b62239bca1d11543944f9f078e577e16010bcbf`。
- Runtime verification：934 passed / 4 skipped / 1 warning。
- User-observed 5HR usage：28%。
- Runtime result：TEST_PASS。
- Architecture acceptance：HOLD。
- 35 leaves / weight 151：IMPLEMENTED CANDIDATE，NOT ACCEPTED。
- Accepted decisions through this checkpoint：R-01、R-02、R-03A/B/C/D、R-04A/B/C/D/E/F/G/H；R-03 and R-04 are fully DECIDED。
- R-04 architecture is closed；R-12/R-13/R-14/K520 remain linked dependencies，and frozen broker capability gates remain implementation/production authorization requirements。
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

Exact revision-specific ID encoding is defined by R-03C。

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

## 7. R-03C — Revision-Specific Observation ID / Canonical Value Objects

Status：DECIDED / IMPLEMENTATION_CORRECTION_REQUIRED。

### 7.1 Revision ID

Canonical revision-specific reference uses a deterministic versioned opaque ID：

    mor1_<64 lowercase SHA-256 hex>

The digest is derived from a versioned canonical identity envelope containing：

- identity_schema_version。
- instrument_id。
- contract_id or canonical null where legitimately absent。
- normalized timeframe。
- timezone-aware UTC interval_start_at。
- content_schema_version。
- deterministic content_fingerprint。

revision_seq、supersedes、accepted_at、source/provenance、change_class and acceptance policy metadata must not enter the revision-ID preimage。

revision_seq is authority-local ordering only and is never cross-environment identity。

### 7.2 Distinct canonical value objects

D Domain owns distinct concepts：

- MarketObservationLogicalKey。
- MarketObservationContentFingerprint。
- MarketObservationRevisionId。

Persistence/wire layers may serialize them，but canonical code must not treat them as interchangeable arbitrary strings。

MarketObservationRevisionId is opaque to consumers。

Consumers must not parse instrument、contract、timeframe or business semantics from the ID。

### 7.3 Canonical encoding

Identity encoding is an explicit versioned byte-level contract，not generic object/JSON serialization。

V1 UTC timestamp lexical form is deterministic and uses UTC Z form with fixed microsecond precision。

Naive datetime is rejected。

Canonical numeric fingerprint input uses exact numeric semantics：

- no raw binary float hashing。
- no silent rounding to force equality。
- insignificant trailing decimal zeros normalize to the same semantic value。
- negative zero normalizes to zero。
- NaN / Infinity are rejected。

### 7.4 Persistence representation

Operational persistence stores the opaque revision ID together with explicit structured logical-key/content/revision columns。

Conceptual uniqueness includes：

- unique observation_revision_id。
- unique logical key + content schema version + content fingerprint。
- unique logical key + revision_seq。

A single opaque ID must not replace structured query fields。

### 7.5 Atomic identity conflict detection

Atomic uniqueness must be enforced by the operational storage adapter at write time。

For V1 PostgreSQL，UNIQUE(observation_revision_id) or an equivalent database uniqueness constraint is mandatory。

Application-level SELECT -> if missing -> INSERT is forbidden because it creates a TOCTOU race。

When atomic insert reports an existing revision ID，the adapter/repository classifies the collision by comparing persisted canonical identity/content evidence：

- exact same canonical evidence -> idempotent duplicate。
- same revision ID but different canonical identity/content -> MarketObservationIdentityConflictError。

A uniqueness violation itself must never be silently retried or treated as duplicate without canonical comparison。

If PostgreSQL transaction state is aborted by the uniqueness violation，comparison may occur after rollback in a new read transaction；the architecture does not require querying through an aborted transaction。

Identity/fingerprint conflict is an integrity incident，quarantines the affected logical key and forbids automatic READY。

No salt/regenerated ID workaround is allowed。

### 7.6 Canonicalization / validation ownership

Canonical ownership belongs to D Domain，not domain.Bar、backtest.MarketBar、DataFrame rows or source adapters。

Shared canonical entry point conceptually owns both eligibility validation and deterministic construction：

    canonicalize_market_observation_content(...)

It validates at least：

- resolved canonical instrument/contract identity。
- listed-future contract requirement。
- normalized supported timeframe。
- timezone-aware interval semantics。
- canonical market values / numeric validity。
- required observation fields。

Source adapters may parse source-native data but may not independently decide fallback eligibility。

Missing contract identity、naive time、invalid numeric value、unsupported timeframe or otherwise invalid canonical envelope must be rejected through shared typed errors / quarantine semantics。

Adapters must not each implement separate permissive eligibility rules。

### 7.7 Strategy/recovery reference migration

Canonical target names are explicit：

- StrategyStateSnapshot.last_market_observation_revision_id。
- ExecutionTriggerRef.market_observation_revision_id。

Legacy last_market_observation_id may remain only as a compatibility read surface during bounded migration。

Once a writer can produce a valid MarketObservationRevisionId，the new revision-specific field becomes the sole recovery/audit authority。

Long-lived dual-write/dual-authority state where legacy free-form ID and canonical revision ID may disagree is forbidden。

### 7.8 Golden-vector contract

Cross-language golden vectors are acceptance requirements，not optional unit-test conveniences。

The same canonical input must produce the same content fingerprint and mor1 ID in Python and future C# implementations。

Vectors must cover contract present/null legitimate cases、UTC normalization、decimal normalization、classification-only change、market-data change and same-content replay。

## 8. R-03D — Cross-Environment Canonicalization / Source Authority

Status：DECIDED / IMPLEMENTATION_CORRECTION_REQUIRED。

### 8.1 Shared canonicalizer / environment adapters

Historical、paper and live producers use environment-specific source parsing/acquisition but one shared pure D Domain canonical identity/validation contract。

Shared semantics include：

- logical-key construction。
- timeframe normalization。
- time normalization。
- exact numeric normalization。
- content fingerprint。
- mor1 revision ID。
- canonical eligibility validation。

Producer paths may not independently redefine those semantics。

### 8.2 Versioned acceptance policy

Candidate acquisition is separate from canonical truth acceptance。

Canonical acceptance uses an explicit versioned MarketObservationAcceptancePolicy containing sufficient scope/source/correction/conflict semantics。

Policy metadata does not enter mor1 identity。

A change in policy never retroactively rewrites historical accepted evidence。

### 8.3 Source roles

Routing role and truth authority are separate concepts。

PRIMARY means normal acquisition preference only。

AUTHORITATIVE_FOR_SCOPE means a versioned verified policy may use that source as truth authority for the stated scope。

Source Registry S0/S1/S2 documentation authority tier is not automatically market-price-feed truth precedence。

No source becomes canonical truth merely because it is the normal PRIMARY feed。

### 8.4 Candidate evidence vs accepted revision

MarketObservationCandidateEvidence and accepted MarketObservationRevision are separate evidence concepts。

Candidate evidence retains source/provenance information without forcing a new canonical content revision。

Multiple sources providing identical logical key + content fingerprint corroborate one accepted revision rather than creating artificial revisions。

Provenance changes alone do not create a new content revision。

### 8.5 Same-content handling

- same source + same content -> duplicate/corroborating evidence；no new revision。
- different source + same content -> corroborating evidence；no new revision。
- re-ingestion + same content -> idempotent；no new revision。
- newer provenance metadata with same canonical content -> append provenance evidence only。

### 8.6 Different-content correction acceptance

Different content is never accepted merely because it arrived later。

Automatic correction acceptance requires policy-provable evidence：

- candidate source eligible for the policy scope。
- policy explicitly authorizes its correction semantics。
- source evidence proves a newer/formal correction according to verified semantics。
- canonical validation passes。
- per-logical-key revision-head precondition succeeds。

Same-source different content without such proof is not automatically a correction。

If evidence/policy cannot prove acceptance，the logical observation enters CONFLICT/QUARANTINE。

### 8.7 Cross-source conflict

Where policy explicitly establishes a verified AUTHORITATIVE_FOR_SCOPE source，its accepted evidence may remain canonical while conflicting validation-source evidence is retained as discrepancy evidence。

Without explicit truth authority：

    CONFLICT / QUARANTINE

Forbidden conflict-selection shortcuts include：

- keep first。
- keep last。
- majority vote。
- Source Registry tier automatically wins。

### 8.8 Quarantine/runtime blast radius

Direct market-data quarantine scope is the logical observation key and is orthogonal to BrokerAccount recovery isolation。

Before strategy consumption，a quarantined observation is unavailable as material market evidence。

If an already-consumed accepted revision later becomes disputed by a material candidate/conflict，affected strategy state becomes DATA_REVIEW_REQUIRED。

DATA_REVIEW_REQUIRED blocks new material/speculative strategy actions that depend on the disputed evidence。

It must not disable existing account/execution safety machinery、position protection、broker reconciliation or other actions required to reduce/control existing exposure。

### 8.9 Historical / paper / live producer modes

Historical mode：

raw source -> parse -> shared canonicalizer -> versioned acceptance policy -> accepted revision -> historical dataset。

Historical dataset reproducibility metadata records canonicalizer/policy/source versions。

Paper recovery-capable mode consumes accepted canonical revisions rather than arbitrary dict/MarketBar values。

Legacy simple PaperMarketDataProvider may remain for deterministic compatibility tests but does not constitute R-02/R-03 recovery-safety evidence。

Live mode：

source candidate -> parse -> shared canonicalizer -> acceptance policy -> durable accepted revision -> strategy delivery。

### 8.10 Operational market-observation evidence

R-03 exposes a correction-scope expansion that did not exist in the original GAP-08EFGHI 35 leaves / weight 151 runtime bundle。

Recovery/audit-safe operational references require storage-neutral market-observation evidence persistence，including at minimum immutable accepted revision resolution and candidate/provenance evidence sufficient for conflict/quarantine audit。

V1 operational implementation family remains PostgreSQL。

Required correction direction includes：

- MarketObservationRevisionRepository or equivalent storage-neutral port。
- PostgreSQL operational accepted-revision evidence adapter。
- bounded candidate/provenance evidence persistence required by acceptance/conflict rules。
- accepted-observation-before-strategy orchestration。

This does not replace Parquet as historical dataset authority。

The additional correction scope has not yet been assigned new Blueprint lifecycle weight and must not be hidden inside the original 35 / 151 acceptance claim。

Retention/partitioning/archive policy is intentionally not decided by R-03D and remains a later implementation/K930 concern。

No implementation may delete evidence still required by recovery/audit references merely because retention policy is unresolved。

### 8.11 Durable before strategy delivery

All recovery-capable paper/live strategy processing consumes only durable accepted MarketObservationRevision evidence。

Strategy delivery before operational evidence commit is forbidden。

This introduces a synchronous durability/write-latency cost in live bar processing。

That latency is an explicit safety trade-off，not an implementation bug。

Any future ultra-low-latency exception requires a separate architecture decision and may not silently bypass durable-before-delivery ordering。

### 8.12 Derived observations

Derived 5m/15m/30m/60m observations are first-class canonical observation revisions。

Derivation evidence records sufficient aggregation policy/version and input MarketObservationRevision references。

If input provenance changes but derived canonical content is identical，append derivation provenance without inventing a new content revision。

If input correction changes derived canonical content，a new derived revision candidate is produced。

A superseded derived observation already consumed by strategy applies the same R-03B8 consumed-evidence REVIEW rules as a direct/raw observation；aggregation does not reduce severity。

### 8.13 Policy/failover history

Acceptance-policy change never retroactively updates prior accepted revisions。

Accepted evidence retains the acceptance policy/version/context needed for audit，but those fields do not enter mor1 identity。

Source failover must be explicitly permitted by policy and recorded。

Silent exception-driven fallback is forbidden。

Failover candidates still pass the same canonical validation/correction/conflict policy；failover does not weaken truth-selection rules。

### 8.14 Cross-environment equality

Same mor1 ID means the same logical key + content schema + canonical content semantics。

It does not imply same source、same revision_seq、same provenance、same acceptance policy、same accepted_at or same latest frontier。

Different environments may temporarily have different latest accepted revisions without invalidating deterministic identity。

### 8.15 Manual resolution

Manual candidate acceptance、source selection or release from data REVIEW are high-risk authority actions。

Production manual resolution depends on R-13 authorization/approval semantics and is default-deny until R-13 is implemented。

Paper/sandbox may exercise the workflow。

Manual resolution must append auditable actor/time/reason/evidence/policy context；it may not mutate historical evidence in place。

## 9. R-14 — Market Data Completeness / Gap Detection

Status：OPEN FOLLOW-UP / NOT PART OF R-03 IDENTITY DECISION。

Missing observation and quarantined observation are different conditions。

R-03A-D define identity/revision/acceptance for candidate observations that exist；they do not prove whether an interval with no candidate represents：

- a legitimate no-trade interval。
- an exchange/session/calendar condition。
- source outage。
- transport failure。
- ingestion/data loss。

Until a formal session/calendar-aware completeness/gap-detection contract exists，a strategy or feature pipeline that depends on continuous intervals must not assume：

    no candidate received == legitimate no-trade interval

If irrelevance cannot be proven，the system must conservatively avoid claiming complete market-data recovery safety。

R-14 maps to GAP-DATA-001 and relates to B250/B720、D340 and K520。

R-14 does not reopen R-03 identity decisions and does not block Decision Checkpoint 2；it is a future production market-data/recovery safety dependency。

## 10. R-04A — Broker Order Discovery Authority

Status：DECIDED / IMPLEMENTATION_CORRECTION_REQUIRED。

Production restart recovery requires an account-scoped broker-neutral read-only BrokerOrderStateProvider or equivalent capability。

It is separate from the legacy execution Broker submit/cancel interface and must not depend on restart-preexisting native Trade objects or process-memory caches。

Recovery discovery for Shioaji requires authoritative account refresh before evaluating broker execution state。

trade_cache_health is diagnostic evidence and does not replace authoritative refresh。

Exact BrokerAccount filtering is mandatory because list_trades may expose trades from more than one account context。

Wrong-account contamination is an adapter contract failure。

Broker execution query failure becomes typed unknown external execution state for the affected BrokerAccount。

BrokerAccount recovery HALT blocks material execution/readiness actions but does not prohibit read-only audit/history access to already durable internal evidence。

## 11. R-04B — Durable Broker Correlation Identity

Status：DECIDED / IMPLEMENTATION_CORRECTION_REQUIRED / BROKER_CAPABILITY_GATE。

Every production submission requires an immutable broker_client_order_ref durable before broker I/O。

broker_client_order_ref must be generated and persisted inside the same sequence-0 PENDING causal transaction。

Therefore every durable PENDING order is defined to already contain a valid broker_client_order_ref。

broker_client_order_ref is distinct from broker-assigned broker_order_id。

All SUBMIT attempts for the same canonical order reuse the same broker_client_order_ref。

Retry must not create a new correlation identity；reusing the same ref intentionally preserves duplicate-submission detection。

Recovery matching authority is exact deterministic identity only。

Attribute/time-window heuristic matching is forbidden as money-risk authority。

For Shioaji，custom_field is the leading broker-native carrier candidate，but production order submission is default-deny until exact place-order -> refresh -> restart-like list_trades round-trip stability is verified for the pinned SDK capability。

If the candidate field cannot preserve exact deterministic identity，production-safe Shioaji submission remains BLOCKED until another broker-supported deterministic correlation mechanism is verified。

## 12. R-04C — Discovery Classification / Broker Action Attempt

Status：DECIDED / IMPLEMENTATION_CORRECTION_REQUIRED。

Discovery completeness and exact-match cardinality are separate axes。

Discovery result distinguishes：

- COMPLETE_FOR_REQUIRED_SCOPE。
- INCOMPLETE。
- typed query/external-state failure。

Exact match cardinality distinguishes：

- zero。
- exactly one。
- more than one。

Positive broker evidence may be retained even when discovery is incomplete；absence has no authority unless required scope/horizon is complete。

Material external side effects use append-only BrokerActionAttempt evidence。

V1 action types include SUBMIT and CANCEL；future AMEND/REPLACE must use the same durable-before-broker-call pattern。

BrokerActionAttempt is not OrderStatus。

Attempt evidence commits and advances BrokerAccount authority revision before broker API invocation。

SUBMIT attempt absent after durable PENDING proves broker submission could not yet have been invoked by contract。

SUBMIT attempt present with no authoritative exact broker match is SUBMISSION_OUTCOME_UNRESOLVED and must not be blindly retried。

CANCEL attempt present while broker order remains active is CANCEL_OUTCOME_UNRESOLVED；active external state does not prove cancel failed。

More than one exact external order for one immutable client correlation identity is AMBIGUOUS_DUPLICATE_EXTERNAL_ORDER -> integrity incident。

BrokerActionAttempt / BrokerActionResolution are immutable evidence。

BrokerActionHead or equivalent mutable concurrency projection prevents concurrent unresolved attempts for the same order/action。

The constraint must be database-enforced；check-then-write TOCTOU is forbidden。

Manual release/retry of unresolved submit/cancel outcomes is high-risk authority and depends on R-13；production default-deny until R-13。

Automated recovery guarantee is bounded by the broker verified discovery horizon。

For Shioaji current official semantics，cross-day unresolved actions outside verified order-discovery horizon require out-of-band evidence and are not claimed as fully automated V1 recovery。

## 13. R-04D — Discovery Health / Execution Continuity

Status：DECIDED / IMPLEMENTATION_CORRECTION_REQUIRED。

R-04D uses two orthogonal broker-neutral gates：

- RecoveryDiscoveryGate：PASS / INCOMPLETE。
- ExecutionContinuityGate：READY / DEGRADED_RECOVERABLE / NOT_READY。

Final BrokerAccount READY / REVIEW / HALT belongs to R-04H，not R-04D。

trade_cache_health is broker-specific diagnostic evidence and never the sole recovery authority。

Healthy is neither necessary nor sufficient for COMPLETE_FOR_REQUIRED_SCOPE。

Health meaning depends on event_type + reason + required recovery scope + unresolved execution context。

A coherent BrokerDiscoveryObservation / discovery_run_id fences one recovery evidence collection。

Required ordering：authoritative refresh completes -> broker state read/filter/canonicalize -> post-refresh health observed -> same-run completeness evaluated。

Stale/pre-refresh health evidence cannot be combined with later broker records。

NoBaseline is informational by itself。

NotSubscribed may leave current discovery complete while continuity is NOT_READY；automatic subscribe -> refresh -> re-evaluate is allowed because subscription repair is not an economic mutation。

SequenceGap before authoritative reconciliation prevents discovery/continuity trust。

After successful authoritative current-state reconciliation，a new ExecutionContinuityEpoch may be established while historical_stream_integrity remains DEGRADED。

Re-anchor never rewrites history to pretend the gap did not occur。

PendingReport surviving authoritative reconciliation is unresolved material broker evidence；Discovery remains INCOMPLETE and Continuity NOT_READY。

Historical UntrackableEventId may be re-anchored for current-state discovery，but persistent inability to track required future material event identity prevents Continuity READY。

No ad-hoc synthetic broker event identity is allowed。

ProjectionFailed invalidates affected Trade/list_trades projection as sufficient discovery authority unless successful reconciliation repairs it or a separately frozen authoritative reconstruction path exists。

ExecutionContinuityEpoch is a local operational fence，not a claim of broker-side linearizable snapshot/high-water semantics。

Pinned/verified Shioaji event-tracking capability remains a production gate。

## 14. R-04E — Broker Snapshot to Canonical Execution Reconstruction

Status：DECIDED / IMPLEMENTATION_CORRECTION_REQUIRED / BROKER_CAPABILITY_GATES_REMAIN。

### 14.1 Reconstruction authority

Observed current state reconstruction is not historical broker-event reconstruction。

Recovery must never fabricate unsupported SUBMITTED / PARTIALLY_FILLED intermediate events、broker callback event IDs or guessed historical timestamps merely to make history contiguous。

OrderEvent is canonical immutable material order-lifecycle evidence，not a literal broker callback DTO。

OrderEvent provenance may therefore originate from LOCAL_OMS、BROKER_CALLBACK or BROKER_DISCOVERY。

Authoritative discovery may re-anchor canonical Order state only when all economically material evidence required by that transition can be reconstructed and atomically committed。

Broker target state may be known while canonical reconstruction remains incomplete。

### 14.2 Fill evidence / identity

Canonical Fill may be reconstructed only from deal-level broker evidence。

Cumulative deal_quantity or average values alone do not authorize synthetic Fill creation。

Fill identity must derive from verified broker-native restart-stable BrokerDealIdentity evidence。

Callback-only identity is insufficient as the sole recovery key。

No timestamp/price/quantity heuristic hash fallback is allowed。

Shioaji Deal.seq is the leading V1 candidate but remains production capability verification required。

Same DealIdentity + same canonical content is duplicate/corroborating evidence。

Same DealIdentity + different material content is an integrity conflict。

### 14.3 Lifecycle reconstruction

Deal-before-order-report is a valid normal path。

PENDING -> PARTIALLY_FILLED and PENDING -> FILLED are legal recovery/live transitions when supported by material evidence。

PARTIALLY_FILLED -> PARTIALLY_FILLED with newly accepted Fill evidence is a material same-status change and requires a new canonical OrderEvent/account revision。

Late lower-information callback evidence must not regress canonical projection。

A contradictory coherent authoritative discovery is not merely ignored；it requires integrity/incompleteness evaluation。

PendingSubmit is a supported broker non-terminal observation but does not automatically promote canonical state to SUBMITTED。

PreSubmitted / Inactive / relevant Failed transition semantics remain broker capability verification required。

Unverified quantity-modification recovery is V1 default-deny。

Canonical Order.quantity remains the known original execution request；broker effective/reduced quantity semantics may not silently rewrite it。

### 14.4 Terminal economic immutability

Terminal acceptance means lifecycle terminal + economic result sealed。

FILLED / CANCELLED / REJECTED may be canonically accepted only when all economically required evidence for that terminal result is reconstructable and atomically committable。

After terminal canonical acceptance：

- no additional Fill may be attached to that Order。
- filled_quantity may not change。
- average_fill_price may not change。
- expected-position effect may not change。
- terminal status may not regress or receive same-terminal economic enrichment。

Complete authoritative broker evidence contradicting sealed terminal economics is INTEGRITY_CONFLICT。

Incomplete broker evidence yields RECONSTRUCTION_INCOMPLETE instead of false corruption claims。

Future broker/exchange trade correction or bust semantics require a separate explicit correction-domain contract；they are not implemented by weakening terminal immutability。

### 14.5 Fill-set economic authority

Verified broker deal evidence -> canonical Fill set -> Order filled economics -> expected AccountPositionSnapshot is the internal authority chain。

Canonical Fill set is the internal filled-economic authority。

Order.filled_quantity is derived from the canonical Fill set。

Order.average_fill_price is derived from the quantity-weighted canonical Fill set when fills exist。

Broker aggregate deal_quantity / average values are external validation/reconciliation evidence and may not directly overwrite canonical economics。

A broker identifiable DealSet proper superset may reconstruct verified missing Fill(s)。

A complete broker DealSet proper subset of durable LocalFillSet is an integrity conflict。

Aggregate mismatch without sufficient individual deal identity is RECONSTRUCTION_INCOMPLETE。

### 14.6 Account recovery mutation fence

Recovery must compare broker evidence against a durable local recovery cut。

recovery_cut_revision is AccountStateHead.current_revision，not a parallel high-water system。

New material strategy execution is blocked while the recovery fence is active。

Broker evidence ingress is not blocked。

Post-cut callback evidence must not directly bypass the recovery fence and must not be dropped。

Production broker callback ingress uses durable BrokerReportInbox evidence before deferred canonical application。

Account-serialized coordination controls ordering/application；durable inbox provides crash-safe evidence capture。

BrokerReportInboxEntry itself does not advance AccountStateHead。

BrokerReportApplication records APPLIED / DUPLICATE / CORROBORATED / DEFERRED / CONFLICT semantics without mutating historical inbox evidence。

AccountRecoveryControl or equivalent durable control row owns short recovery-session/final-handoff concurrency control and is distinct from economic AccountStateHead authority。

Final handoff from RECOVERING to normal must be race-free with callback ingress。

### 14.7 Atomic account-authority commit

One atomic material authority commit equals one BrokerAccount revision。

One revision contains at most one canonical OrderEvent but may include multiple Fill records、one new complete expected-position snapshot、multiple BrokerActionResolution records/head mutations and exactly one AccountRecoveryCheckpoint。

Every accepted OrderEvent belongs to exactly one revision-advancing authority commit，but not every authority commit requires an OrderEvent。

A single discovery run affecting multiple orders may therefore generate multiple sequential account revisions；revision order is canonical acceptance order，not claimed broker callback history。

Before recovery mutation commit，AccountStateHead must be locked and equal recovery_cut_revision。

Mismatch is STALE_RECOVERY_CUT and causes abort/re-evaluation，not silent application of stale broker evidence。

Broker network I/O never occurs while AccountStateHead is locked。

When one broker evidence set both changes lifecycle and resolves an open BrokerActionAttempt，Order/Fill/expected-position effects and BrokerActionResolution/head clear belong to the same authority transaction/revision。

Position-changing Fill requires a complete new AccountPositionSnapshot in the same transaction。

Status-only transition carries forward the prior exact expected_snapshot_id。

Incomplete/conflicting/unverified reconstruction never creates a partial authority revision。

### 14.8 Bundle idempotency / ambiguous commit

Every material authority mutation has a stable AccountAuthorityCommit identity that is reproducible across retry/reconnect/process recovery。

committed_revision is a result，not the idempotency identity。

authority_commit_id and mutation_fingerprint are separate responsibilities。

same commit identity + same fingerprint -> return/deduplicate prior committed result。

same commit identity + different fingerprint -> IDEMPOTENCY_INTEGRITY_CONFLICT。

Retry first checks committed receipt identity；only if absent may it validate expected_head_revision and attempt the mutation。

Ambiguous COMMIT outcome is resolved by querying the authoritative PostgreSQL SOR for the same committed receipt before retry。

Commit receipt and all economic/account authority mutations must be in the same database transaction。

Domain retains a typed AccountAuthorityCommitReceipt contract。

V1 physical persistence may map that receipt into the existing append-only Trading Event Ledger rather than create a parallel receipt authority table。

InboxEntry identity、BrokerDeal/Fill identity and AccountAuthorityCommit identity are distinct。

The system does not claim exactly-once broker callback delivery；it requires durable evidence capture + idempotent canonical application + deterministic exactly-once economic effect。

### 14.9 Shared persistence primitive

Live execution、recovery re-anchor and broker-action resolution must share one BrokerAccount authority-commit primitive。

Do not create an independent recovery persistence authority that reimplements Fill / snapshot / order / revision invariants。

Existing ExecutionPersistenceService may become/delegate to a higher AccountAuthorityCommitService compatibility facade rather than grow into an opaque giant procedure。

### 14.10 Remaining broker capability gates

- Shioaji exact restart-stable FillKey：VERIFICATION_REQUIRED。
- broker_client_order_ref/custom_field round-trip：VERIFICATION_REQUIRED / production default-deny。
- PreSubmitted / Inactive / relevant Failed mapping：CAPABILITY_VERIFICATION_REQUIRED。
- quantity modification recovery：DEFAULT_DENY / DEFERRED。
- pinned Shioaji event tracking capability：VERIFICATION_REQUIRED。

These gates do not reopen R-04E architecture；they remain implementation/production authorization gates。

## 15. R-04F/G/H — Final Broker Recovery Safety Decisions

R-04 overall status：DECIDED / IMPLEMENTATION_CORRECTION_REQUIRED / BROKER_CAPABILITY_GATES_REMAIN。

R-04A through R-04H are architecture-decided。

Remaining Shioaji capability verification does not reopen R-04 architecture；it remains an implementation/production authorization gate。

### 15.1 R-04F — Terminal vs Non-Terminal Recovery Rules

Status：DECIDED / IMPLEMENTATION_CORRECTION_REQUIRED / BROKER_CAPABILITY_GATES_REMAIN。

Canonical non-terminal OrderStatus remains：PENDING / SUBMITTED / PARTIALLY_FILLED。

Canonical terminal OrderStatus remains：FILLED / CANCELLED / REJECTED。

Recovery classifications such as SUBMISSION_OUTCOME_UNRESOLVED、RECONSTRUCTION_INCOMPLETE and CAPABILITY_UNVERIFIED are not OrderStatus。

Broker-observed terminal state is not sufficient for canonical terminal acceptance。

Canonical terminal acceptance requires all economically material evidence for the transition to be reconstructable and atomically committable。

FILLED requires complete identifiable canonical Fill evidence；aggregate broker deal_quantity / average values alone are insufficient。

CANCELLED may contain prior or newly reconstructed fills and therefore permits 0 <= filled_quantity < quantity。

Recovery never fabricates unsupported intermediate lifecycle history。

PENDING -> PARTIALLY_FILLED and PENDING -> FILLED are legal evidence-backed recovery transitions。

PARTIALLY_FILLED -> PARTIALLY_FILLED with newly accepted Fill evidence is a material same-status OrderEvent and advances BrokerAccount revision。

Failed -> REJECTED is permitted only when verified broker semantics prove original-order failure with zero economic effect。

PreSubmitted / Inactive / unsupported Failed semantics remain CAPABILITY_UNVERIFIED until pinned adapter verification。

Once FILLED / CANCELLED / REJECTED is canonically accepted，terminal economics are sealed。

Complete authoritative contradiction after terminal sealing is INTEGRITY_CONFLICT。

Incomplete evidence is RECONSTRUCTION_INCOMPLETE；it must not produce fabricated canonical recovery。

R-04F does not authorize broker-action retry or re-invocation。

### 15.2 R-04G — Safe Retry / No-Resubmit

Status：DECIDED / IMPLEMENTATION_CORRECTION_REQUIRED / BROKER_IDEMPOTENCY_CAPABILITY_NOT_AVAILABLE。

No blind broker-action retry is allowed。

Absence of broker evidence is not proof that an external side effect did not occur。

No BrokerActionAttempt means broker invocation is impossible by frozen ordering and is classified RESUMABLE_FIRST_INVOCATION。

An unresolved existing BrokerActionAttempt means the broker side effect may have occurred and automatic re-invocation is forbidden。

Complete discovery + zero exact broker match does not override the unresolved-attempt rule。

A durable NOT_DISPATCHED BrokerActionResolution may restore SideEffectSafetyGate eligibility only when a verified pre-transport boundary proves broker network invocation never began。

Timeout、process crash、disconnect、connection reset after dispatch started、lost response、missing callback and zero list_trades match are OUTCOME_UNKNOWN，never NOT_DISPATCHED。

An exact broker match forbids resubmission；the existing broker order is recovered instead。

Incomplete or out-of-discovery-horizon evidence forbids automatic retry。

broker_client_order_ref / custom_field correlation identity is not broker idempotency authority。

Current Shioaji architecture has no verified server-side idempotent resubmission guarantee。

Terminal canonical Order is never revived；a later desired submission requires a new OrderIntent and new canonical Order。

SUBMIT and CANCEL use the same durable-attempt / no-blind-retry rule。

Human or out-of-band evidence cannot directly open retry；production authority belongs to R-13 and must create auditable durable resolution evidence。

SideEffectSafetyGate SAFE_TO_INVOKE is necessary but not sufficient；current intent/session/instrument/account/risk/business validity must also pass before broker invocation。

R-04G does not decide final BrokerAccount READY / REVIEW / HALT。

### 15.3 R-04H — BrokerAccount READY / REVIEW / HALT Integration

Status：DECIDED / IMPLEMENTATION_CORRECTION_REQUIRED。

READY means every mandatory recovery/evidence/capability predicate required for safe normal automated execution is positively proven。

REVIEW means no proven integrity corruption exists，but additional authorized human/out-of-band evidence or authority is required before release。

HALT means an integrity、technical、capability or authority prerequisite prevents safe normal automated material broker action。

UNKNOWN、DEGRADED and NO_ERROR_OBSERVED never imply READY。

READY requires valid expected/account authority、valid exact checkpoint references、coherent recovery cut、complete required broker discovery/horizon、unambiguous exact correlation、complete canonical reconstruction、valid Fill/economic invariants、no integrity conflict、no unresolved BrokerActionAttempt requiring disposition、ExecutionContinuityGate READY、no unapplied material broker evidence and race-free final handoff。

A correctly reconciled active non-terminal broker order does not by itself prevent READY。

Out-of-horizon unresolved action requiring formal external evidence is REVIEW，subject to R-13 for production release。

Integrity conflict、multiple exact broker matches、invalid expected-state authority or unavailable mandatory broker capabilities are HALT conditions。

Precedence is HALT > REVIEW > READY。

If no explicit READY proof exists and no recognized REVIEW disposition applies，the system fails closed。

Minimum recovery isolation scope remains BrokerAccount。

REVIEW/HALT blocks new normal material broker side effects but permits durable callback capture、read-only discovery、authoritative refresh、subscription repair、evidence persistence and deterministic reconciliation required to repair recovery。

READY handoff must be race-free with callback ingress；changed AccountStateHead or new unapplied material evidence yields STALE_RECOVERY_EVALUATION and forces reevaluation。

READY / REVIEW / HALT is operational readiness authority and does not by itself advance economic AccountStateHead revision。

No R-04H state may bypass R-04G no-resubmit rules or R-13 production authorization requirements。

### 15.4 R-04 Overall Closure

R-04A：DECIDED。
R-04B：DECIDED。
R-04C：DECIDED。
R-04D：DECIDED。
R-04E：DECIDED。
R-04F：DECIDED。
R-04G：DECIDED。
R-04H：DECIDED。

R-04 overall：DECIDED / IMPLEMENTATION_CORRECTION_REQUIRED。

No runtime correction is authorized by Decision Checkpoint 4。

Next architecture action is to map、bound and reweight the complete correction Work Package before runtime authorization。

Linked R-12 / R-13 / R-14 / K520 dependencies and broker capability gates must be explicitly classified as implementation blocker、production authorization gate or later GAP dependency during correction freeze。

## 16. Runtime Correction Items Already Identified

These are not new design choices unless a later decision explicitly changes them：

- canonical Order/Fill/OrderEvent runtime fields must be reconciled to frozen contracts。
- PENDING direct PARTIALLY_FILLED/FILLED legal transitions must match architecture。
- status/filled_quantity invariants must be fully enforced。
- occurred_at and received_at must remain distinct evidence semantics。
- missing expected snapshot must not become FLAT。
- recovery must use exact account checkpoint/snapshot references。
- production broker submission orchestration must commit initial PENDING before broker I/O。
- StrategyStateSnapshot persistence must be integrated with material execution causal boundary。

## 17. Consequence

Runtime commit remains a useful implementation baseline and is not reverted。

However GAP-08EFGHI cannot move to ACCEPTED until the post-R-03/R-04 expanded correction scope is explicitly mapped/frozen/reweighted，required linked dependencies and capability gates are classified，and bounded correction runtime passes targeted/compatibility/full-regression verification。

No LIVE authorization is implied。

## Decision Checkpoint 5A — R-01 through R-05 Closed

**DECISION CHECKPOINT 5A ACCEPTED — ARCHITECTURE DECISIONS ONLY**

- Baseline decision commit：`462a3d541cb6b0bccc9bb5e3e1a118cd1c2cf351`。
- Runtime implementation candidate remains：`6b62239bca1d11543944f9f078e577e16010bcbf`。
- Architecture acceptance remains：HOLD。
- Runtime authorization remains：NOT_AUTHORIZED。
- R-01：DECIDED / AMENDED。
- R-02：DECIDED / AMENDED。
- R-03：DECIDED / UNCHANGED。
- R-04：DECIDED / AMENDED。
- R-05：DECIDED / IMPLEMENTATION_CORRECTION_REQUIRED。
- Next architecture cluster：R-06 + R-07 Recovery Boundary Cluster。

This checkpoint records architecture decisions only。

It does NOT assert：

- runtime conformance。
- broker capability verification completion。
- production readiness。
- authorization to begin runtime correction。

### R-01 Amendments

#### A1 — Production initialization authorization

All production `EXPECTED_STATE_INITIALIZED` transitions require R-13-authorized initialization authority。

`FLAT` and `BROKER_SEED` are both production default-deny until that authority exists。

`BROKER_SEED` may require a stronger authorization policy；R-01 does not freeze a particular UI、approval count or workflow implementation。

#### A2 / A2b — Initialization authority revision and READY separation

Successful `EXPECTED_STATE_INITIALIZED` establishes the first committed BrokerAccount material authority revision：

    account_revision = 1

The physical persistence model may either create the head at revision 1 or advance a pre-existing reserved/control revision-0 row to revision 1。

Architecture does not require physical `AccountStateHead` row absence before initialization。

Fresh broker I/O occurs before the authority transaction and never while holding the AccountStateHead authority lock。

The revision-1 initialization authority commit atomically establishes：

- initialization authority event。
- first complete `AccountPositionSnapshot`。
- logical AccountStateHead revision 1。
- exact `AccountRecoveryCheckpoint(1)`。
- exact expected snapshot reference。
- stable authority-commit/idempotency receipt。
- persisted immutable broker observation evidence required by initialization。

Broker observation persistence by itself does not advance AccountStateHead；the initialization authority transition does。

Initialization revision 1 establishes the local durable authority baseline but does NOT itself grant BrokerAccount `READY`。

The fresh broker observation is evidence，not a broker-side linearizable fence。

Final activation still requires the existing R-04H race-safe recovery/currentness handoff。

#### A3 / A3b — BROKER_SEED as account-position genesis

`BROKER_SEED` is an explicit one-time account-position genesis authority。

It does not fabricate historical Order、OrderEvent or Fill evidence and does not claim historical execution attribution。

Conceptually：

    ExpectedPosition at revision N
    = InitializationBaseline
      + canonical economic effects accepted after initialization

This is a semantic authority relationship，not a requirement to implement position reconstruction as naive arithmetic over all history。

All economically authoritative facts required to establish the seeded position must come from approved authoritative sources at the initialization boundary。

Fresh broker evidence supplies broker-state/economic facts for which the broker is authoritative。

Canonical instrument/reference authority may supply separately frozen reference facts such as canonical instrument interpretation where appropriate。

Economically material reference authority/version used by initialization must remain auditable。

No economically material value may be guessed、heuristically inferred or synthetically fabricated。

If a complete canonical initialization `AccountPositionSnapshot` cannot be formed from verified authorities，production initialization remains blocked。

#### A4 — UNMANAGED_EXTERNAL_EXECUTION

`UNMANAGED_EXTERNAL_EXECUTION` is a recovery classification，not an OrderStatus。

It covers material broker execution evidence within required recovery scope that has no deterministic canonical local counterpart。

Active/non-terminal unmatched broker execution always blocks automatic initialization / automatic READY。

Terminal unmatched broker execution also blocks automatic READY when it is inside required recovery scope、has unresolved current economic impact or affects current broker/account reconciliation。

Historical terminal evidence outside required recovery scope with no current economic/recovery impact does not automatically block READY。

Recovery must not：

- auto-import unmatched broker execution into fabricated canonical history。
- silently cancel unmatched broker execution。
- fabricate Order / Fill provenance。

Final REVIEW versus HALT integration remains R-04H authority。

### R-02 Amendments

#### A5 — account_revision semantics

`account_revision` means BrokerAccount material authority commit sequence。

It does NOT mean OrderEvent sequence。

Every accepted canonical OrderEvent belongs to exactly one revision-advancing material authority commit。

One authority revision contains at most one canonical OrderEvent。

Some material authority revisions may contain no OrderEvent，including initialization、BrokerActionAttempt or valid standalone material BrokerActionResolution transitions。

Every successful authority revision produces exactly one exact AccountRecoveryCheckpoint。

#### A6 — causal atomic crash invariant

Material StrategyStateSnapshot + initial PENDING persistence must preserve the frozen atomic crash invariant。

It must be impossible for a successful durable strategy frontier to claim that the material observation was consumed while the corresponding durable execution boundary required by the frozen causal contract is absent，and vice versa where that contract requires atomicity。

V1 targets one verified PostgreSQL transactional consistency domain。

A future cross-store design may claim equivalent semantics only if it preserves the same crash invariant。

Best-effort、eventual or ordinary dual-write is not equivalent。

### R-03 Confirmation

R-03A/B/C/D remain DECIDED / UNCHANGED。

D340、R-14/GAP-DATA-001 and K520 remain explicit dependencies/gates and do not reopen R-03。

### R-04 Amendments

`UNMANAGED_EXTERNAL_EXECUTION` is integrated into account-scoped broker recovery evaluation。

R-04H final activation must validate complete RecoveryCut currentness，not AccountStateHead equality alone。

Final activation requires：

1. AccountStateHead still satisfies the evaluated authority-frontier precondition。
2. no new relevant non-revision-advancing recovery evidence appeared outside the evaluated RecoveryCut。
3. no unapplied material broker evidence exists outside the evaluated/application frontier。
4. AccountRecoveryControl / recovery-session generation or equivalent recovery fence still identifies the same valid handoff generation。

Failure of final-currentness validation produces `STALE_RECOVERY_EVALUATION` and requires reevaluation；it does not silently activate the account。

This clarification does not reopen R-04A-H。

### R-05 — ExecutionStateLoader Contract

Status：DECIDED / IMPLEMENTATION_CORRECTION_REQUIRED。

#### R-05A — Read + Validate + Explicit Result

`ExecutionStateLoader` is the local durable execution restore + validation boundary。

It returns explicit immutable restore evidence/result。

It is not：

- broker discovery。
- broker network I/O。
- reconciliation authority。
- repair/re-anchor authority。
- economic mutation authority。
- AccountStateHead advancement authority。
- final READY / REVIEW / HALT authority。

#### R-05B — Coherent Complete RecoveryCut

Loader restores exactly one coherent BrokerAccount-local durable RecoveryCut from a verified persistence consistency domain。

Independent repository `latest` reads are forbidden as recovery authority。

AccountStateHead revision N identifies the BrokerAccount material/economic authority frontier only。

`account_revision = N` alone is not a complete RecoveryCut identity when recovery-critical dependencies may change without advancing AccountStateHead。

RecoveryCut therefore consists conceptually of：

- exact BrokerAccount authority frontier；and
- sufficient deterministic cut/currentness evidence covering recovery-critical dependencies that may change independently of `account_revision`。

At minimum，where applicable，the cut/currentness proof must cover：

- durable broker-report/callback inbox arrival/application state。
- AccountRecoveryControl / recovery-session generation or equivalent recovery fence。
- future recovery-critical dependencies explicitly permitted to change without advancing account_revision。

AccountAuthorityCommitReceipt remains part of authority validation closure，but does not require a separate independent frontier when atomically committed with the corresponding authority revision。

Architecture does not prescribe physical fields such as：

- `broker_inbox_high_water`。
- `recovery_control_version`。
- database snapshot/XID token。
- one high-water/version column per dependency。

The requirement is semantic：implementation must be able to prove whether relevant recovery evidence appeared outside/after the evaluated RecoveryCut。

All records claimed to belong to one RecoveryCut must be observed under a verified consistency boundary capable of proving that coherent view。

If required authority/recovery data cannot be observed under a provable consistency boundary，loader must not synthesize a coherent cut。

A captured RecoveryCut remains historically valid as the coherent world that was observed；final-currentness at activation remains R-04H responsibility。

#### R-05C — VALID guarantee / required transitive closure

`ExecutionRestoreResult = VALID` guarantees：

1. one coherent local RecoveryCut was captured。
2. its BrokerAccount authority frontier is exactly account_revision N。
3. the required transitive recovery dependency closure visible at that cut is complete and internally consistent。
4. every validated materialized projection has a deterministic canonical validation anchor at the captured RecoveryCut。
5. every recovery-critical dependency capable of changing without account_revision advancement is covered by deterministic cut/currentness evidence。
6. required AccountAuthorityCommit receipts and canonical provenance resolve consistently with the authority frontier。
7. no detected local integrity defect prevents subsequent recovery evaluation。

Required recovery roots include at least，where applicable：

- AccountStateHead(N)。
- AccountRecoveryCheckpoint(N)。
- exact expected_snapshot_id。
- current non-terminal canonical Orders。
- unresolved/open BrokerActionAttempt / BrokerActionHead state。
- pending durable broker-report/callback evidence that can still affect canonical execution。
- active AccountRecoveryControl / recovery-session state。

The transitive closure then resolves required canonical evidence such as OrderEvent、Fill、BrokerActionResolution、authority-commit receipt and canonical provenance/reference evidence。

`VALID` does NOT mean：

- broker-current。
- final-current。
- BrokerAccount READY。
- Strategy READY。
- trading authorized。
- entire historical archive proven corruption-free。

Completed terminal history that is no longer a required current recovery dependency does not need eager full replay during every startup。

#### R-05D — Restore outcomes / initialization boundary

Architecture-level outcomes：

    VALID

    BASELINE_NOT_ESTABLISHED

    RESTORE_FAILURE
        READ_FAILURE
        MISSING_REQUIRED_AUTHORITY
        INTEGRITY_FAILURE
        UNSUPPORTED_SCHEMA_OR_CAPABILITY

`BASELINE_NOT_ESTABLISHED` may be returned only when durable account lifecycle/initialization authority positively proves that no successful BrokerAccount initialization authority commit has ever existed。

Absence of head/checkpoint/snapshot rows alone is insufficient to prove never-initialized。

If prior successful initialization cannot be excluded，restore fails closed as `MISSING_REQUIRED_AUTHORITY` or `INTEGRITY_FAILURE` according to evidence。

Required versus optional evidence is defined by the frozen contract，not inferred ad hoc from repository `None` values。

Authority restore is all-or-nothing for the required recovery dependency closure。

Partial diagnostic evidence may be retained，but cannot be exposed as `VALID`。

All-or-nothing recovery authority validation does not require eager loading or full replay of the entire historical archive。

A RecoveryCut becoming superseded after successful load is not an R-05 loader failure；R-04H final-currentness evaluation handles that condition。

#### R-05E — Projection + canonical evidence validation

V1 does not require full-history event replay。

Loader validates persisted materialized projections against bounded canonical evidence at the captured RecoveryCut。

Every validated materialized projection must deterministically resolve to its applicable canonical authority/validation anchor at that cut。

Projection-only trust is forbidden。

Wall-clock `latest` is not authority。

Architecture does not require a particular physical anchor field such as `last_event_id`。

Validation failure produces integrity failure；ExecutionStateLoader does not repair、rewrite、re-anchor or silently reconstruct durable authority state。

#### R-05F — RecoveryExecutionContext / activation boundary

A VALID restore may hydrate only a recovery-isolated `RecoveryExecutionContext`。

Before successful R-04H final handoff，that context may support recovery evaluation、broker discovery、diagnostics、reconciliation planning and deterministic evidence comparison。

It may not be treated as normal live execution authority。

Normal strategy submission、normal cancel workflow and normal live trading remain blocked until R-04H race-safe activation succeeds。

If recovery remediation itself requires a material broker side effect，it remains governed by R-04G side-effect safety plus R-13 authority where applicable。

`RecoveryExecutionContext` is not a second economic authority。

`Execution READY != Strategy READY`；strategy restoration/readiness remains R-06。

### Explanatory Notes — Non-Decisions

1. `deterministic cut/currentness witness` does not require every dependency to own an independent physical high-water/version column。

The requirement is only that implementation can prove whether relevant recovery evidence appeared after/outside the evaluated RecoveryCut。

2. R-05D all-or-nothing authority restore does not require eager loading/full replay of the complete historical archive。

It means only that the required recovery dependency closure may not partially succeed and still be labelled `VALID`。

### Decision Queue After Checkpoint 5A

Next：R-06 + R-07 Recovery Boundary Cluster。

Then continue in authoritative queue order：R-08 → R-09 → R-10 formal closure → R-11 → R-12 → R-13 boundary → R-14 boundary → K520 defer confirmation → broker capability gate classification → correction scope freeze/reweight → later runtime authorization。

No correction runtime is authorized by this checkpoint。

## Decision Checkpoint 5B — R-06 / R-07 Recovery Boundary Cluster

**DECISION CHECKPOINT 5B ACCEPTED — ARCHITECTURE DECISIONS ONLY**

- Baseline：`c131d6bd04212d302259b0571bfef91084196f76`。
- Runtime candidate remains：`6b62239bca1d11543944f9f078e577e16010bcbf`。
- Architecture Acceptance remains：HOLD。
- Runtime Authorization remains：NOT_AUTHORIZED。
- R-06：DECIDED。
- R-07：DECIDED。
- R-09 remains OPEN and owns StrategyInstance/config identity and lifecycle authority。
- Next architecture cluster：R-08 + R-09 identity/config authority。

This checkpoint records architecture decisions only。

It does NOT assert：

- runtime conformance。
- production readiness。
- broker capability completion。
- authorization to begin runtime correction。

## R-06 — Multi-Strategy Recovery Boundary

Status：DECIDED。

### R-06A — StrategyInstance Recovery Unit

Minimum logical strategy recovery unit = `StrategyInstance`。

It is NOT：

- strategy class。
- globally shared strategy_id。
- BrokerAccount-wide strategy state。
- one global strategy watermark。

StrategyInstance identity/config lifecycle authority is not defined by R-06；it remains R-09 responsibility。

### R-06B — Per-Instance Recovery Frontier

A StrategyRecoveryFrontier contains，as applicable：

- exact durable StrategyStateSnapshot or positively authorized no-state mode。
- one or more exact required MarketObservation frontier(s)。
- state-schema compatibility evidence。
- required causal/consumption/material-output backlinks。

A StrategyInstance may consume one or multiple recoverable observation streams。

A scalar observation frontier is valid only when that StrategyInstance contract has exactly one recoverable observation stream。

No global strategy watermark is permitted。

Algorithmic statelessness does NOT mean recovery statelessness。

An explicitly stateless StrategyInstance may omit internal durable strategy-state payload only when that mode is positively authorized。

Stateless mode does not waive durable observation、consumption、causal or material-output frontier evidence required for safe recovery。

For a material-output-capable StrategyInstance：

    no StrategyStateSnapshot payload

must never imply：

    no recovery frontier required

A legitimately never-consumed StrategyInstance may have a genesis/empty recovery frontier only when lifecycle authority positively proves that state。

R-06B proves which exact evidence formed restored strategy state；R-03 remains authority for whether corrected/superseded market evidence permits activation。

### R-06C — Fresh / Stateless / Genesis Eligibility

Absence of StrategyStateSnapshot alone never authorizes fresh start。

Fresh initialization、first activation、stateless mode or genesis/never-consumed state must be positively proven by StrategyInstance lifecycle/config authority。

Otherwise：

    StrategyInstance = NOT_READY

Silent fresh start is forbidden。

R-09 remains responsible for：

- strategy_instance_id authority。
- config_version authority。
- lifecycle/provisioning authority。
- allowed schema/config migration authority。

### R-06D — Required Decision Participation / Policy Continuity

A StrategyInstance recovery failure is initially StrategyInstance-scoped。

However，a decision cohort may produce new normal material account actions only when every StrategyInstance declared required by the applicable authoritative decision/config policy version is recovery/trading-ready。

Required participation may not be inferred from：

- currently loaded runtime instances。
- whichever instances restored successfully。
- latest config by default。
- current deployment presence alone。

A required unavailable StrategyInstance may never be silently：

- removed。
- substituted。
- downgraded to optional。

Recovery must deterministically resolve the exact authoritative decision/config policy version governing the restored cohort。

Restart must not silently replace the recovered governing version with the latest/currently deployed version。

Policy-version continuity does NOT prohibit explicit version transition。

An explicit Vn -> Vn+1 transition is allowed only through an authorized lifecycle/config transition with its own compatibility/migration semantics。

Restart、deployment presence or recovery failure alone is never sufficient authority for policy substitution。

Exact version identity、transition authority and config lifecycle remain R-09。

Independent decision cohorts may continue independently only when their membership and independence are themselves authoritatively defined and the required account-exposure / decision-routing / risk independence is proven。

Absent such proof，contributors sharing the same account final-position decision authority are treated as one coupled decision boundary。

If the Multi-Strategy Decision Layer owns durable decision-relevant state，that state must itself have a recoverable authority frontier before the corresponding cohort can become READY。

R-06 does not require the Decision Layer to own durable state；a pure/reconstructible Decision Layer needs no additional recovery authority。

### R-06E — Readiness Composition / Catch-Up Isolation

The following states are distinct：

- BrokerAccountExecutionReady。
- StrategyRestoreValid。
- StrategyTradingReady。
- DecisionCohortTradingReady。

A successful strategy snapshot restore does not by itself grant StrategyTradingReady。

A strategy may still require replay/catch-up、market-correction evaluation、schema compatibility or config compatibility evaluation。

Generic startup recovery replay/catch-up may evaluate historical observations and may internally derive signals when required for deterministic state reconstruction。

Before StrategyTradingReady and DecisionCohortTradingReady，such historical outputs：

- cannot create a new broker-bound OrderIntent。
- cannot create a normal PENDING execution boundary。
- cannot invoke normal broker side effects。
- cannot become a current tradable decision merely because historical evaluation emitted a signal。

After catch-up，new normal material action requires current evaluation under：

- current restored strategy state。
- authoritative governing decision policy。
- BrokerAccount execution readiness。
- current risk/business/session prerequisites。

The narrow R-02 causal replay contract remains separate：if R-02 positively proves that the exact observation -> strategy -> decision UoW never crossed its durable execution boundary and is eligible for replay，that replay follows R-02 semantics。

R-02 exact causal replay is not generic startup catch-up。

Normal strategy decision paths remain subject to decision-cohort readiness。

Account-protection、risk-controlled or operator-authorized recovery actions remain governed by their own frozen authority paths。

A strategy cannot bypass cohort readiness merely by labelling one of its own outputs as REDUCE or safety action。

## R-07 — ReconciliationCase BrokerAccount Scope

Status：DECIDED。

### R-07A — Primary Recovery Ownership

Each ReconciliationCase has exactly one primary BrokerAccount recovery scope。

A case may reference instrument、contract、order、position、strategy and evidence for diagnosis/audit，but those references do not change primary BrokerAccount ownership。

A shared incident may affect multiple BrokerAccounts，but recovery-case authority scope does not cross BrokerAccount boundaries。

Architecture does not require a SharedIncident persistence model at this checkpoint。

### R-07B — V1 Isolation Floor

V1 execution/recovery isolation floor = BrokerAccount。

V1 does not permit instrument-level normal execution isolation inside one BrokerAccount merely because one affected instrument can be identified。

Instrument-level isolation may only be introduced by a later explicit architecture decision with proven independence across account exposure、margin/risk、pending execution and routing authority。

### R-07C — Account-Scoped Readiness Evaluation

Repository/readiness evaluation of reconciliation impact must be BrokerAccount-scoped。

Global unresolved-case existence may never directly block unrelated BrokerAccounts。

The existence of an open/unresolved ReconciliationCase does NOT by itself determine READY / REVIEW / HALT。

R-04H readiness remains based on validated underlying reconciliation evidence、severity、unresolved economic/recovery impact and applicable policy。

`case.open == true` is not itself economic/readiness truth authority。

ReconciliationCase remains a durable discrepancy/control/audit representation。

Any reconciliation state/evidence that is a material prerequisite for R-04H readiness is recovery-critical non-revision-advancing evidence。

Such readiness-affecting state must be covered by the evaluated complete RecoveryCut/currentness witness。

Pure audit/history-only case changes that cannot affect current readiness do not need to invalidate activation evaluation。

### R-07D — Case Authority Boundary

ReconciliationCase is discrepancy/problem/control/audit lifecycle authority。

It is NOT：

- expected-position authority。
- Order authority。
- Fill authority。
- AccountStateHead economic authority。

Opening、updating、closing a case or attaching audit evidence does not by itself advance AccountStateHead or rewrite expected position。

If reconciliation resolution requires economic mutation，it must flow through the frozen AccountAuthorityCommit path。

Manual authority/override remains R-13 responsibility。

Formal run-level ReconciliationRun audit remains R-12 responsibility。

### Decision Queue After Checkpoint 5B

Next：R-08 + R-09 identity/config authority cluster。

Then：R-10 formal closure -> R-11 -> R-12 -> R-13 boundary classification -> R-14 boundary classification -> K520 defer confirmation -> broker capability gate classification -> correction-scope freeze/reweight -> explicit runtime authorization。

No runtime correction is authorized by this checkpoint。
