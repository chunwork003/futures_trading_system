# GAP-08 Bounded Runtime Authorization — C23

## 1. Authorization Status

BOUNDED_RUNTIME_AUTHORIZED。

Authorized leaf：

C23 — Canonical MarketObservation Identity + Revision。

No other correction / implementation / verification leaf is authorized。

---

## 2. Baselines

Architecture Decision Baseline：

`22ceaa729ab6e9da9c00ae52e09ae7116be5a743`

Correction-Freeze Baseline：

`93fb846a9c9cd61eea44427a86a542fc95f9ac28`

Previous completed bounded execution：

`docs/work/GAP08_C11_CLOSURE.md`

C11 Closure Baseline：

`a0d071d2aad7f157aebb8fce46f11c2c6b65acd2`

Authorization Baseline：

the docs-only commit containing this authorization envelope。

---

## 3. Frozen C23 Architecture Contract

Canonical ownership：

D Domain。

C23 MUST implement distinct canonical concepts：

- `MarketObservationLogicalKey`
- `MarketObservationContentFingerprint`
- `MarketObservationRevisionId`

Canonical revision-specific identity：

    mor1_<64 lowercase SHA-256 hex>

Canonical logical key fields：

- instrument_id。
- contract_id where listed-contract dimension is required。
- normalized timeframe。
- timezone-aware UTC interval_start_at。

Logical key MUST NOT contain：

- OHLCV / amount / counts。
- trade_date。
- session/session_ref。
- source/provenance。
- symbol/exchange display aliases。
- ingestion time。
- revision metadata。

---

## 4. C23 Canonical Content Contract

C23 owns one shared pure canonical entry point。

Recommended name：

`canonicalize_market_observation_content(...)`

Canonical strategy-visible content includes：

Market data：

- open。
- high。
- low。
- close。
- volume。
- amount when present。
- trade_count when present。
- tick_count when present。

Classification：

- trade_date。
- session_ref when present。

Source/provenance MUST NOT enter the content fingerprint。

Arbitrary feature payload MUST NOT enter the content fingerprint。

---

## 5. Numeric Contract

Identity/fingerprint numeric semantics MUST NOT depend on Python binary float representation。

Canonical market numeric input：

- Decimal。
- integer where semantically valid。
- exact decimal string。

Raw Python `float`：

REJECT。

NaN：

REJECT。

Infinity：

REJECT。

Decimal canonical lexical form：

- fixed-point decimal。
- no exponent form。
- insignificant trailing zeros removed。
- trailing decimal point removed。
- negative zero normalized to `0`。
- no silent rounding to force equality。

Examples：

    1
    1.0
    1.000

must canonicalize to the same decimal semantic value。

    -0
    -0.0

must canonicalize to：

    0

Volume / trade_count / tick_count：

- exact integer semantics。
- non-negative。
- bool is not accepted as integer evidence。

---

## 6. Time Contract

interval_start_at：

- timezone-aware required。
- normalize to UTC。
- deterministic lexical representation。
- UTC `Z` suffix。
- fixed six-digit microsecond precision。

Example：

    2026-09-25T01:00:00.000000Z

Naive datetime：

REJECT。

Timestamp is identity evidence。

It is NOT causal/revision authority。

---

## 7. Timeframe Contract

Canonical timeframe normalization is owned by the C23 domain primitive。

Minimum required behavior：

    "1m"
    " 1M "
    "60s"

must resolve to one canonical logical timeframe：

    1m

Other supported syntactic durations may normalize case/whitespace and integer representation。

C23 MUST NOT silently equate calendar/session semantics that are not proven equivalent。

In particular：

`24h` MUST NOT automatically become `1d` merely by arithmetic。

Invalid / zero / negative timeframe：

REJECT。

---

## 8. Contract Identity Rule

Listed-contract observations require a resolved canonical contract_id。

C23 MUST NOT infer contract identity from：

- symbol。
- broker code。
- continuous-series alias。
- front-series alias。

Missing contract_id when contract identity is required：

REJECT。

contract_id=None is permitted only when the caller explicitly supplies a canonical context where no listed-contract dimension exists。

No synthetic/front/continuous alias receives canonical listed-future identity in C23。

---

## 9. Canonical Byte Encoding

C23 MUST use explicit versioned byte framing。

Generic JSON serialization MUST NOT define identity。

All frame field values：

UTF-8 bytes。

Each ordered field frame：

    <ascii-field-name>:<ascii-byte-length>:<value-bytes>\n

Content fingerprint header：

    market-observation-content-v1\n

Revision-ID preimage header：

    market-observation-revision-id-v1\n

Canonical null lexical value：

    null

Content frame ordered fields：

1. content_schema_version
2. open
3. high
4. low
5. close
6. volume
7. amount
8. trade_count
9. tick_count
10. trade_date
11. session_ref

Content fingerprint：

    lowercase SHA-256 hex of exact content frame bytes

Revision-ID frame ordered fields：

1. identity_schema_version
2. instrument_id
3. contract_id
4. timeframe
5. interval_start_at
6. content_schema_version
7. content_fingerprint

Revision ID：

    mor1_
    + lowercase SHA-256 hex of exact revision-ID frame bytes

identity_schema_version：

1。

content_schema_version：

1。

---

## 10. revision_seq Boundary

revision_seq is authority-local ordering。

revision_seq MUST NOT enter：

- MarketObservationLogicalKey。
- MarketObservationContentFingerprint。
- MarketObservationRevisionId preimage。

C23 MUST NOT allocate revision_seq。

C23 MUST NOT persist revision_seq。

C23 MUST NOT implement per-key locking / acceptance sequencing。

Those responsibilities belong to C24。

---

## 11. C23 vs C24 Boundary

C23 implements：

- pure canonical logical identity。
- pure canonical content normalization。
- content fingerprint。
- deterministic revision ID。
- canonical validation。
- golden vectors。

C23 does NOT implement：

- candidate persistence。
- accepted revision persistence。
- revision_seq allocation。
- acceptance policy。
- provenance persistence。
- source-role authority。
- conflict/quarantine workflow。
- PostgreSQL uniqueness。
- last-write/acceptance behavior。
- operational repository。

Those belong to C24。

---

## 12. C23 vs C25 Boundary

C23 MUST NOT modify：

- `StrategyStateSnapshot.last_market_observation_id`
- strategy recovery references。
- execution trigger references。
- strategy delivery path。

Canonical target migration：

`last_market_observation_revision_id`

belongs to C25。

C23 MUST NOT introduce dual recovery authority。

---

## 13. Runtime Scope

Authorized runtime files：

NEW：

- `domain/market_observation.py`

NEW test：

- `tests/unit/test_market_observation_identity.py`

NEW cross-language fixture：

- `tests/fixtures/market_observation_golden_vectors_v1.json`

No existing runtime module is authorized for modification。

In particular，NOT_AUTHORIZED_FOR_MODIFICATION：

- `domain/bars.py`
- `domain/instruments.py`
- `domain/contracts.py`
- `backtest/market_data_models.py`
- `backtest/market_data.py`
- `backtest/paper_market_data.py`
- `persistence/strategy_state.py`
- `persistence/postgres/strategy_state.py`
- all migrations。

If C23 requires modification of an existing runtime consumer：

STOP。

Do not widen C23。

---

## 14. Golden Vector Acceptance

Golden vectors are mandatory。

The JSON fixture must be language-neutral and reusable by future C# implementation。

At least the following vectors are required：

1. listed contract / UTC input。
2. equivalent non-UTC timezone input producing the same UTC instant。
3. decimal trailing-zero normalization。
4. negative-zero normalization。
5. legitimate contract_id=null case。
6. `1m` / `60s` timeframe equivalence。
7. market-data content change producing different fingerprint and revision ID。
8. classification-only content change producing different fingerprint and revision ID。
9. same canonical content replay producing identical fingerprint and revision ID。

Expected content fingerprint and expected `mor1_...` value MUST be fixed literals in the fixture。

Tests MUST consume those literals。

Tests MUST NOT calculate an expected value using the same implementation and then call that a golden vector。

---

## 15. Required Positive Tests

Tests must prove：

1. logical-key equality after timezone normalization。
2. `1m` and `60s` normalize identically。
3. listed-contract contract_id is required。
4. legitimate non-contract context accepts canonical null。
5. same exact semantic decimals produce the same fingerprint。
6. negative zero equals zero canonically。
7. UTC lexical form has fixed six-digit microseconds + Z。
8. same content replay produces identical fingerprint。
9. same canonical identity/content produces identical mor1 ID。
10. market-data change changes fingerprint/mor1。
11. classification-only change changes fingerprint/mor1。
12. `mor1_` format is exactly prefix + 64 lowercase hex。
13. golden-vector literals match runtime result。

---

## 16. Required Negative Tests

Tests must prove rejection of：

- naive datetime。
- raw float identity/fingerprint input。
- Decimal NaN。
- Decimal Infinity。
- invalid instrument_id。
- invalid contract_id。
- missing required listed-future contract_id。
- blank/invalid timeframe。
- zero/negative timeframe。
- bool numeric/count evidence。
- negative volume/count。
- blank session_ref when supplied。

Static acceptance must prove：

- no `json.dumps` identity construction。
- no hash of raw float representation。
- no source/provenance fields in fingerprint contract。
- no symbol/exchange alias in logical key。
- no revision_seq in revision-ID preimage。

---

## 17. Compatibility Boundary

Read-only compatibility tests：

- `tests/unit/test_market_data.py`
- `tests/unit/test_paper_market_data.py`
- `tests/unit/test_strategy_state_recovery.py`

They must remain unchanged。

C23 creates a new canonical primitive only。

Existing MarketBar / strategy-state behavior remains unchanged until later authorized leaves。

---

## 18. Environment / Side Effects

Actual PostgreSQL：

NOT_AUTHORIZED。

Migration modification：

NOT_AUTHORIZED。

Migration execution：

NOT_AUTHORIZED。

Broker I/O：

NOT_AUTHORIZED。

Market-data network I/O：

NOT_AUTHORIZED。

External file/data mutation：

NOT_AUTHORIZED。

`data/`：

MUST NOT be modified/staged。

---

## 19. Stop Conditions

STOP without widening scope if：

- exact canonical identity requires changing existing MarketBar。
- exact canonical identity requires changing StrategyStateSnapshot。
- persistence/schema work becomes necessary。
- acceptance/revision_seq allocation becomes necessary。
- D340/session-calendar architecture must be changed。
- listed/synthetic identity cannot be represented without a new unresolved public semantic。
- golden vectors cannot be expressed deterministically under the frozen contract。
- generic JSON becomes necessary for identity。
- more than two scope-internal correction cycles are required。
- unrelated regression appears。

---

## 20. Execution Sequence

    exact Authorization Baseline precheck
    -> inspect existing domain/runtime references
    -> create pure C23 domain primitive
    -> create fixed golden vectors
    -> targeted C23 tests
    -> market-data / strategy-state compatibility
    -> full regression
    -> exact diff validation
    -> commit
    -> push
    -> final report
    -> STOP

Suggested runtime commit：

`feat(domain): add canonical market observation identity`

No amend。

No rebase。

No force push。

After C23：

STOP。

Do not automatically start C24、C25、C02 or V05。

A docs-only C23 closure is required before the next runtime authorization。
