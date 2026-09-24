# Blueprint Traceability

## Status

AUTHORITATIVE
---

## 1. Required Chain

每個正式 engineering leaf 最終必須可追蹤：

    V1 Capability
    → Blueprint Leaf
    → GAP
    → Work Package
    → Runtime File
    → Test
    → External Source
    → Commit
    → Acceptance

---

## 2. Traceability Fields

| Field | Meaning |
|---|---|
| Capability ID | V1_CAPABILITY_MAP ID |
| Blueprint ID | engineering leaf |
| GAP | problem / required development |
| Work Package | bounded execution contract |
| Runtime Path | implementation |
| Test Path | verification |
| Source ID | official/internal semantics source |
| Commit | accepted implementation commit |
| Lifecycle | blueprint lifecycle |
| Acceptance | PASS/FAIL |

---

## 3. GAP-ACCOUNT-001 Initial Mapping

此 mapping 在 Domain Blueprint baseline 時進一步驗證。

### Canonical / Broker Identity

    D630
        Reverse broker contract resolution

### Broker Adapter

    I510
        Broker account identity mapping

    I520
        Account type normalization

    I530
        Native / PII filtering

    I610
        Futures position mapping

    I620
        Direction mapping

    I630
        Quantity / price mapping

    I640
        Contract reverse-resolution integration

    I650
        Observation-time injection

### Account

    J210
        BrokerAccount model

    J220
        Broker stable account reference

    J230
        Broker account metadata validation

    J240
        BrokerAccountProvider

    J310
        Canonical AccountPosition

    J320
        Expected position identity

    J330
        Quantity / direction semantics

    J410
        BrokerPositionProvider

    J420
        BrokerPositionSnapshot

    J430
        Actual position identity

    J440
        Observation / Decimal semantics

### Pure Comparison

    J510
        Pairwise comparator

    J520
        ReconciliationStatus

    J530
        MATCH

    J540
        INTERNAL_ONLY

    J550
        BROKER_ONLY

    J560
        CONTRACT_MISMATCH

    J570
        DIRECTION_MISMATCH

    J580
        QUANTITY_MISMATCH

    J590
        Non-comparable identity error

### Explicitly Not Implemented

    J600
        Reconciliation policies

    J700
        Startup readiness

    H200
        OrderIntent / PositionEffect

---

## 4. Current Known Runtime Paths

Existing compatibility：

    domain/broker_instruments.py
    backtest/account_position.py
    backtest/broker.py
    backtest/shioaji_*

Target GAP-ACCOUNT-001：

    trading/account.py
    trading/reconciliation.py
    adapters/sinopac/account_mapping.py

Tests：

    tests/unit/

Final exact path：

以 accepted runtime commit 為準。
