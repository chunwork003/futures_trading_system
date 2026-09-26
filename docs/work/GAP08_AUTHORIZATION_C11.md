# GAP-08 Bounded Runtime Authorization — C11

## 1. Authorization Status

BOUNDED_RUNTIME_AUTHORIZED。

Authorized leaf：

C11 — Shioaji Status Mapping Correction。

No other correction or verification leaf is authorized。

---

## 2. Baselines

Architecture Decision Baseline：

`22ceaa729ab6e9da9c00ae52e09ae7116be5a743`

Correction-Freeze Baseline：

`93fb846a9c9cd61eea44427a86a542fc95f9ac28`

Previous completed bounded execution：

`docs/work/GAP08_C22_CLOSURE.md`

C22 Closure Baseline：

`22ac4cb4c60dbe5fbb3b00d3758a2c7ad50e76d1`

Authorization Baseline：

the docs-only commit containing this authorization envelope。

---

## 3. Frozen C11 Contract

C11 is a SMALL_FIX correction leaf。

Frozen PASS：

- unverified broker statuses remain capability-unverified / non-authoritative。

Frozen MUST NOT：

- unconditional `Inactive -> REJECTED`。
- unconditional `Failed -> REJECTED` without verified zero-effect semantics。
- `PreSubmitted -> SUBMITTED` without verified semantics。

V05 remains the separate broker-capability verification leaf。

C11 MUST NOT manufacture V05 evidence。

---

## 4. Required Fail-Closed Mapping

Current verified bounded mapping retained：

    Filled
        -> FILLED

    PartFilled
        -> PARTIALLY_FILLED

    Cancelled
        -> CANCELLED

    PendingSubmit
        -> SUBMITTED

    Submitted
        -> SUBMITTED

Current unverified semantics：

    PreSubmitted
    Inactive
    Failed

must NOT produce a canonical OrderStatus。

Required behavior：

    -> explicit typed capability-unverified failure

Preferred bounded type：

    UnverifiedBrokerOrderStatusError

or an equivalently precise typed exception。

The type must preserve the offending broker status in the error context/message。

---

## 5. Unknown Status Rule

An otherwise-unmapped Shioaji status MUST NOT silently fall back to：

    OrderStatus.PENDING

Unknown/unmapped status is non-authoritative。

Required：

    explicit typed capability-unverified failure

This prevents absence of a known mapping from becoming a canonical broker-state claim。

---

## 6. Runtime Scope

Primary runtime file：

- `backtest/shioaji_mapping.py`

Authorized direct test files：

- `tests/unit/test_shioaji_mapping.py`
- `tests/unit/test_shioaji_submitted_status.py`

Optional new bounded test：

- `tests/unit/test_c11_shioaji_status_mapping.py`

Compatibility tests may be executed read-only。

No other runtime file is authorized for modification。

In particular：

- `backtest/shioaji_broker.py` — NOT_AUTHORIZED_FOR_MODIFICATION。
- `adapters/sinopac/capabilities.py` — NOT_AUTHORIZED_FOR_MODIFICATION。
- `adapters/capabilities.py` — NOT_AUTHORIZED_FOR_MODIFICATION。

If a non-test runtime caller requires semantic redesign rather than natural propagation of the typed fail-closed error：

STOP。

Do not widen C11。

---

## 7. Positive Acceptance

Direct tests must prove：

1. Filled -> FILLED。
2. PartFilled -> PARTIALLY_FILLED。
3. Cancelled -> CANCELLED。
4. PendingSubmit -> SUBMITTED。
5. Submitted -> SUBMITTED。
6. PreSubmitted produces explicit capability-unverified failure。
7. Inactive produces explicit capability-unverified failure。
8. Failed produces explicit capability-unverified failure。
9. failure identifies the offending broker status。

---

## 8. Negative Acceptance

Direct/static tests must prove：

1. Inactive does not return REJECTED。
2. Failed does not return REJECTED。
3. PreSubmitted does not return SUBMITTED。
4. unknown/unmapped broker status does not silently return PENDING。
5. no V05 verification claim is added。
6. no capability matrix is upgraded。
7. no broker I/O occurs。
8. no retry/recovery semantics are added。
9. no canonical OrderStatus enum expansion is performed。
10. no C10 recovery reconstruction responsibility is absorbed。

---

## 9. V05 Boundary

V05：

PreSubmitted / Inactive / Failed Semantics Verification。

Status：

NOT_AUTHORIZED。

C11 is enforcement under currently unverified semantics。

C11 != V05。

C11 completion MUST NOT claim：

- PAPER_VERIFIED。
- PRODUCTION_VERIFIED。
- verified zero-effect Failed semantics。
- verified terminal Inactive semantics。
- verified canonical PreSubmitted semantics。

Future V05 evidence may justify a later mapping change through a separate authorized checkpoint。

---

## 10. Environment / Side Effects

Actual PostgreSQL：

NOT_AUTHORIZED。

Migration modification：

NOT_AUTHORIZED。

Migration execution：

NOT_AUTHORIZED。

Broker network I/O：

NOT_AUTHORIZED。

Broker paper I/O：

NOT_AUTHORIZED。

Broker production I/O：

NOT_AUTHORIZED。

Tests must use local enum/model behavior only。

---

## 11. Test Boundary

Direct targeted tests：

    .\.venv\Scripts\python.exe -m pytest tests\unit\test_shioaji_mapping.py tests\unit\test_shioaji_submitted_status.py -q

If the optional bounded C11 test is added，include it。

Shioaji compatibility tests：

    .\.venv\Scripts\python.exe -m pytest tests\unit\test_shioaji*.py -q

These tests MUST NOT access a real broker/network。

External PostgreSQL DSNs must remain disabled：

    POSTGRES17_TEST_DSN
    POSTGRES18_TEST_DSN

Full regression：

    .\.venv\Scripts\python.exe -m pytest -q

---

## 12. Stop Conditions

STOP without widening scope if：

- correcting mapping requires `backtest/shioaji_broker.py` semantic modification。
- correcting mapping requires capability-matrix modification。
- a test requires real broker access。
- V05 evidence is required to decide an additional status。
- Shioaji enum behavior differs materially from the currently installed package。
- correction requires canonical OrderStatus enum redesign。
- correction requires recovery/C10 implementation。
- unrelated regression appears。
- more than two scope-internal correction cycles are required。

---

## 13. Completion Boundary

Execution sequence：

    exact Authorization Baseline precheck
    -> inspect installed Shioaji enum/status surface
    -> C11 implementation
    -> targeted tests
    -> Shioaji compatibility
    -> full regression
    -> exact diff validation
    -> commit
    -> push
    -> final report
    -> STOP

Suggested runtime commit：

`fix(shioaji): fail closed on unverified order statuses`

No amend。

No rebase。

No force push。

After C11：

STOP。

Do not automatically start C23、C02 or V05。

A docs-only C11 closure is required before the next runtime authorization。
