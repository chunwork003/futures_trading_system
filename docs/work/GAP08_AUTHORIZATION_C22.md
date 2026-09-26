# GAP-08 Bounded Runtime Authorization — C22

## 1. Authorization Status

BOUNDED_RUNTIME_AUTHORIZED。

Authorized leaf：

C22 — Canonical Time Evidence Correction。

No other correction or verification leaf is authorized。

---

## 2. Baselines

Architecture Decision Baseline：

`22ceaa729ab6e9da9c00ae52e09ae7116be5a743`

Correction-Freeze Baseline：

`93fb846a9c9cd61eea44427a86a542fc95f9ac28`

Previous completed bounded execution：

`docs/work/GAP08_C01_CLOSURE.md`

C01 Closure Baseline：

`45381207d1ff4f2e8f02b42a3764e354c2074ac9`

Authorization Baseline：

the docs-only commit containing this authorization envelope。

---

## 3. Authorized Runtime Scope

Primary runtime files：

- `trading/execution.py`
- `persistence/execution.py`

Tests：

- `tests/unit/test_operational_execution.py`
- one new bounded C22 test file if useful

Conditional test-only inspection：

- `tests/unit/test_event_ledger.py`

No change to `persistence/events.py` is expected。

If `persistence/events.py` requires semantic modification：

STOP and review scope before continuing。

---

## 4. Frozen Contract

C22 must preserve distinct semantic time evidence。

Required：

    occurred_at
    received_at

are independent evidence values。

For canonical OrderEvent：

- `occurred_at` is required。
- `received_at` is required。
- both are timezone-aware。
- both normalize to UTC。
- neither defaults to the other。
- neither defaults to local/system now。

For OrderEvent -> TradingEvent mapping：

    TradingEvent.occurred_at
        = exact OrderEvent.occurred_at

    TradingEvent.received_at
        = exact OrderEvent.received_at

Forbidden：

    received_at = event.occurred_at

as convenience fallback。

---

## 5. Clock / Ordering Semantics

C22 does NOT introduce a universal timestamp ordering invariant。

The following is NOT required：

    occurred_at <= received_at

because source clock skew / transport clock differences may exist。

Causal ordering remains：

    sequence
    revision
    frontier
    explicit authority references

Timestamp values MUST NOT become causal authority。

---

## 6. Unknown / Unverified Source Time Boundary

C22 does not fabricate unknown source occurrence time。

Current bounded OMS OrderEvent contract requires explicit known `occurred_at`。

If an upstream source cannot provide a semantically valid occurrence time：

- it must not substitute `received_at`。
- it must not substitute `datetime.now()`。
- it must not substitute `datetime.utcnow()`。
- it must not create false KNOWN evidence。

Full UNKNOWN / UNVERIFIED external broker occurrence-time representation is not implemented by this leaf when it requires schema or recovery-domain expansion。

If such representation becomes necessary to complete C22：

STOP。

Do not widen C22 into C07/C09/C10 or a migration change。

---

## 7. Explicitly Out of Scope

NOT AUTHORIZED：

- AccountStateHead / checkpoint work。
- C02～C21。
- C23～C25。
- V01～V07。
- broker discovery。
- broker callback reconstruction。
- Shioaji mapping。
- backtest models。
- strategy state。
- MarketObservation models。
- DB migration modification。
- DB migration execution。
- actual PostgreSQL access。
- broker network/paper/production I/O。
- global timestamp rewrite。

No universal `recorded_at` field is added to TradingEvent by C22。

Record-specific timestamp fields remain record-specific。

---

## 8. Bounded Rewrite Policy

C22 work type：

CORRECTION / EXTEND。

Small internal rewrite is allowed if needed to remove duplicated or false timestamp authority。

Do not perform a broad rewrite of execution models。

Preferred implementation：

1. Add explicit required `received_at` to canonical `OrderEvent`。
2. normalize `occurred_at` and `received_at` independently。
3. map both exactly into `TradingEvent`。
4. update only direct C22 tests/callers required by this canonical contract。

Do not preserve an invalid compatibility fallback merely to reduce diff size。

---

## 9. Positive Acceptance

Direct tests must prove：

1. `OrderEvent.occurred_at` is required。
2. `OrderEvent.received_at` is required。
3. both reject naive datetime。
4. both normalize timezone-aware values to UTC independently。
5. mapping preserves exact occurred_at。
6. mapping preserves exact received_at。
7. distinct timestamps remain distinct after mapping。
8. received_at may precede occurred_at without causal validation failure。
9. event sequence remains lifecycle ordering authority。

---

## 10. Negative Acceptance

Direct tests must prove：

1. missing received_at is rejected。
2. no implicit received_at = occurred_at fallback。
3. no `datetime.now()` fallback。
4. no `datetime.utcnow()` fallback。
5. received_at does not overwrite occurred_at。
6. occurred_at does not overwrite received_at。
7. timestamp comparison is not used to validate event sequence。
8. no schema/migration changes。
9. no broker/backtest changes。
10. no C23 MarketObservation responsibility absorbed into C22。

---

## 11. Test Boundary

Actual PostgreSQL integration DSNs must be disabled：

    POSTGRES17_TEST_DSN
    POSTGRES18_TEST_DSN

Targeted：

    .\.venv\Scripts\python.exe -m pytest tests\unit\test_operational_execution.py -q

If a new C22 test file is created，include it。

Event-ledger semantic compatibility：

    .\.venv\Scripts\python.exe -m pytest tests\unit\test_event_ledger.py -q

Full regression：

    .\.venv\Scripts\python.exe -m pytest -q

No actual PostgreSQL integration test is authorized。

No broker test is authorized。

---

## 12. Stop Conditions

STOP without widening scope if：

- adding required `received_at` requires schema migration。
- non-test runtime callers outside the authorized files require semantic redesign。
- `persistence/events.py` needs structural change。
- unknown/unverified occurrence-time persistence requires DB/schema work。
- C22 requires broker-specific time mapping。
- C22 requires recovery coordinator changes。
- full regression exposes an unrelated architecture contradiction。
- more than two bounded correction cycles are required。

---

## 13. Git Policy

Execution sequence：

    exact Authorization Baseline precheck
    -> C22 implementation
    -> targeted tests
    -> event-ledger compatibility
    -> full regression
    -> exact diff validation
    -> commit
    -> push
    -> final report
    -> STOP

Suggested runtime commit：

`fix(execution): preserve canonical event time evidence`

No amend。

No rebase。

No force push。

Do not automatically start C11 or C02。

---

## 14. Stop Boundary

After C22 runtime commit / push / final report：

STOP。

Runtime Authorization is consumed。

A separate docs closure must record C22 completion before another leaf can be authorized。
