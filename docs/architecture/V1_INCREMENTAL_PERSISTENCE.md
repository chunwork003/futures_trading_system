# First incremental codec and persistence mapping — P00 candidate

## EMA_CLOSE_V1 qualification slice

First feature is close-price EMA, matching `features/trend.py::add_trend_features` and `features/rolling.py::ema` with adjust=False and min_samples=span. This qualifies one feature, not all of GAP-09 or a complete strategy. Preserve existing batch functions. P05 implements the adapter only after this candidate is accepted.

Input: one accepted completed canonical bar at a time, fixed StrategyInstance/instrument/listed contract/timeframe/config. Close must be finite, positive and <=1e9 for this qualification profile. Decimal close converts to IEEE754 binary64 only inside approximate feature calculation; never use the resulting float as operational money. Span is an integer 1..1000, fixed for the instance. Null/missing/gap bars are not imputed: qualification becomes invalid and affected cohort cannot increase risk until pinned replay restores continuity.

Recurrence: alpha=2/(span+1); first accepted close initializes EMA; each subsequent step computes `(1-alpha)*previous + alpha*close`, in that order without fused multiply-add. Count increments only for a new accepted observation. Output is null/WARMING before count>=span, otherwise EMA/READY. Warmup readiness is local only, not account or trading readiness. No full history scan per update; O(1) state/time.

Codec `ema_close.v1`: span, processed_count, ema_hex, last_observation_revision_id, governing_config_fingerprint. ema_hex is Python-compatible finite binary64 hexadecimal lexical representation (`float.hex` / `float.fromhex`), not decimal money. It preserves exact binary64 checkpoint state across restore. Fresh state has count=0 and both ema/last observation null; after any bar both are present. Span/config/codec mismatch rejects restore. P05 must verify canonical hex roundtrip and finite positive value, count/frontier correspondence and external snapshot bindings; schema shape alone is insufficient.

Repeated exact last observation is a no-op after canonical content verification; same identity/different material rejects at accepted observation boundary. An older/revised frontier is not another step: invalidate qualification and rebuild from pinned accepted history. Snapshot capture occurs only after a complete observation update and its associated output is durably accounted for. Replay cannot re-emit a second economic intent.

Golden fixture `contracts/ema_close.fixture.v1.json` freezes closes [10,12,11,15,14], span=3, states [10,11,11,13,13.5], outputs [null,null,11,13,13.5]. Test every restart boundary and compare against current Polars batch EMA; tolerance abs=1e-12 + rel=1e-12 for approximate feature values, never for monetary fields. Larger equivalence suite before P05 acceptance must cover constant/ramp/alternating/extreme qualified prices, spans 1/20/60/1000, partitions, missing/revised bars, all checkpoint boundaries and dependency-lock drift.

## Durable envelope versus domain DTO

New DTOs are payload contracts. `TradingEvidenceEnvelope` wraps each immutable new Signal/Decision/RiskDecision/CapitalState/IncrementalState qualification record with schema_version, evidence_id, owner, actor_ref, recorded_at, correlation_id, causation_id and payload_hash. Existing accepted Order/Fill/StrategyStateSnapshot/account/reconciliation records remain in their existing stores and are referenced, never rewritten into a competing generic event store.

Envelope owner is E for Signal/IncrementalState, G for Decision/RiskDecision/CapitalState. Payload identity and envelope evidence_id must agree with the owning record key; IncrementalState qualification gets a separate immutable evidence ID referring to its existing snapshot. Canonical payload hash is SHA256 of UTF-8 sorted-key compact JSON with finite scalars and wire lexical normalization; the payload hash excludes envelope fields. No arbitrary blob deserialization or pickle. recorded_at is first durable acceptance time, retained on exact duplicate replay. Correlation follows command/observation chain; missing causation uses explicit null, not fabricated identity.

K owns storage adapters/UoW, not payload semantics. Proposed new stores are owner-specific append-only tables in trading: strategy_signals, decisions, risk_decisions, capital_projections, incremental_qualifications. Each stores typed query keys, envelope metadata, immutable JSON payload/hash and explicit references. Same key/same material returns original record; same key/different material conflicts. No wildcard generic SQL writer exposed to API. Important table/column comments are Traditional Chinese. These table names are candidate physical ownership, not executed migrations.

| Record | Atomic boundary / key / recovery |
|---|---|
| Signal + strategy progress | Snapshot at completed observation + output receipt + Signal in one UoW; unique instance/config/strategy version/observation; replay checks receipt before emission |
| Incremental qualification | Links accepted StrategyStateSnapshot plus feature codec/version/config/frontier; state bytes stay in snapshot.state_json under an explicit codec member; qualifier cannot replace missing snapshot |
| Decision | Immutable complete cohort evaluation; unique account/contract/policy/cohort/frontier/expected account revision; transaction verifies reference closure and records all selected/excluded members |
| RiskDecision | Immutable decision/account/capital/policy/margin input closure; execution separately revalidates current cut, so stored ALLOW never means indefinitely authorized |
| CapitalState | Immutable projection key includes account checkpoint + mark + calculation/margin policy; no writable balance head competing with account ledger |
| OrderIntent | Existing canonical intent store/UoW; adapter requires accepted Decision/Risk/trigger references; no second OrderIntent schema/store |

Do not hold a DB transaction during feature/backtest computation. Compute against pinned inputs, then verify all required revisions and commit under accepted fence; if invalidated, discard candidate and re-evaluate. One account writer persists canonical trading effects. Cross-owner references do not require a distributed transaction because Python-owned trading state uses the same PG UoW; BFF never writes these tables.

Missing referenced payload/hash/frontier/codec fails restore; exact duplicate is safe, contradictory duplicate is not. A new persistence migration must add explicit FKs/uniqueness/indexes and forward compatibility tests without editing existing migrations. Row existence, valid local restore and resolved reconciliation are not trading permission.

## Remaining acceptance gates

This closes the first-codec and envelope ownership design at candidate level. It does not implement persistence adapters or certify all existing DTO mappings. Semantic review must check complete RecoveryCut participation of new readiness-relevant records, transaction sizing and revision/fence integration against accepted K contracts. P05/P06/P08 packages must enumerate these integration assertions, not infer them from this fixture passing.
