# H — Execution / OMS

## Status

BUILDING / PROVISIONAL until Blueprint baseline acceptance。

---

## Domain Purpose

將 risk-approved account action 轉成 explicit execution semantics，管理 Order lifecycle、OrderEvent、Fill、partial/terminal state、PaperBroker 與 future production OMS。

Execution Core 必須 broker-neutral。

Target ownership：

    trading/execution/

主要 current runtime：

- `backtest/models.py`
- `backtest/execution.py`
- `backtest/order_factory.py`
- `backtest/broker.py`
- `backtest/paper_broker.py`
- `backtest/paper_trading.py`
- `backtest/paper_runner.py`

---

## Capability Groups

| Group | Name | Responsibility |
|---|---|---|
| H100 | Execution Contracts | Order / Fill / status / broker-neutral port |
| H200 | OrderIntent / PositionEffect | explicit economic execution meaning |
| H300 | Order Lifecycle | pending / submitted / partial / terminal |
| H400 | Fill / OrderEvent | actual broker execution evidence |
| H500 | OMS State | idempotent state machine / order correlation |
| H600 | PaperBroker | deterministic simple broker baseline |
| H700 | Paper Orchestration | polling / pending sync / position application |
| H800 | Idempotency / Retry | duplicate protection / recovery-safe processing |
| H900 | Direction Transition Execution | wait-for-flat execution coordination |

---

## Engineering Leaves

| ID | Name | Purpose | Lifecycle | Weight | Maps |
|---|---|---|---|---:|---|
| H110 | Order Model | broker-neutral requested execution state | ACCEPTED | 3 | H01 |
| H120 | Fill Model | actual execution quantity / price result | ACCEPTED | 3 | H01 |
| H130 | OrderType | MARKET / LIMIT / STOP execution type | ACCEPTED | 2 | H01 |
| H140 | OrderStatus | PENDING / SUBMITTED / PARTIAL / FILLED / CANCELLED / REJECTED | ACCEPTED | 3 | H01,H03 |
| H150 | Broker Execution Port | submit / query / fills / cancel capability | ACCEPTED | 4 | H02 |
| H160 | Submission Result | submit 可回傳 current order + immediate fills | ACCEPTED | 2 | H02,H03 |
| H170 | Canonical Execution Ownership | Order / Fill long-term owner 為 trading.execution | DESIGN_FROZEN | 4 | H01 |
| H210 | OrderIntent | 描述為何要下單，而非只描述 order mechanics | ACCEPTED | 5 | H07 |
| H220 | PositionEffect | OPEN / CLOSE / REDUCE 等 explicit effect | ACCEPTED | 5 | H07 |
| H230 | OrderIntent Identity | correlation / causation / source target/risk decision | ACCEPTED | 4 | H07,H08 |
| H240 | PositionEffect Validation | effect 必須與 current expected position / target transition 相容 | ACCEPTED | 5 | H07 |
| H250 | Broker Open/Close Mapping Boundary | adapter 只能由 explicit PositionEffect 決定 New/Cover | ACCEPTED | 5 | H07 |
| H310 | Pending State | submitted 前/等待 broker acceptance | ACCEPTED | 2 | H03 |
| H320 | Submitted State | broker 已接受但未完全成交 | ACCEPTED | 2 | H03 |
| H330 | Partial Fill State | 多 fill / partial quantity 累積 | ACCEPTED | 4 | H03 |
| H340 | Terminal Filled State | full quantity complete | ACCEPTED | 3 | H03 |
| H350 | Terminal Cancelled State | cancelled 與已成交量共存語意可處理 | ACCEPTED | 4 | H03 |
| H360 | Terminal Rejected State | broker rejection 明確終止 | ACCEPTED | 3 | H03 |
| H370 | Async Status Synchronization | query broker 後更新 internal execution state | ACCEPTED | 4 | H03 |
| H410 | Fill Conversion Boundary | broker deal → canonical Fill | ACCEPTED | 4 | H01,H03 |
| H420 | Multi-Fill Accumulation | 同 order 多 fills 合併 quantity / weighted price | ACCEPTED | 4 | H03 |
| H430 | Fill Deduplication | broker duplicate deal 不重複套用 account state | ACCEPTED | 4 | H03,H08 |
| H440 | OrderEvent Contract | future append-only order status/change event | DESIGN_FROZEN | 4 | H08 |
| H450 | Execution Time Semantics | broker event / fill timestamp 必須 canonical timezone-aware | DESIGN_FROZEN | 4 | H03,H08 |
| H510 | OMS Order Identity | internal order_id / broker_order_id 分離 | DESIGN_FROZEN | 4 | H08 |
| H520 | OMS State Machine | legal transition / terminal immutability | DESIGN_FROZEN | 5 | H08 |
| H530 | Correlation / Causation | intent → order → event → fill 可追蹤 | DESIGN_FROZEN | 4 | H08 |
| H540 | OMS Persistence Seam | execution state 由 K Domain persistence port 保存 | DESIGN_FROZEN | 4 | H08 |
| H550 | OMS Recovery Seam | restart 可由 persisted events + broker query reconstruct | DESIGN_FROZEN | 5 | H08 |
| H610 | PaperBroker Submit | deterministic immediate fill baseline | ACCEPTED | 3 | H04 |
| H620 | PaperBroker Query | in-memory order / fill query | ACCEPTED | 2 | H04 |
| H630 | PaperBroker Cancel | pending order cancellation baseline | ACCEPTED | 2 | H04 |
| H640 | PaperBroker Scope Boundary | PaperBroker 不模擬完整 production latency/faults | DESIGN_FROZEN | 3 | H04 |
| H710 | PaperTradingEngine | broker + position + portfolio + risk orchestration | ACCEPTED | 4 | H05 |
| H720 | Pending Order Registry | async order 待後續 sync | ACCEPTED | 3 | H05,H06 |
| H730 | Entry Fill Application | entry fills 更新 historical/paper position projection | ACCEPTED | 4 | H05 |
| H740 | Exit Fill Application | partial/full exit fills 更新 position / realized PnL | ACCEPTED | 4 | H05 |
| H750 | Pending Order Synchronization | polling broker fills/status 並套用一次 | ACCEPTED | 4 | H06 |
| H760 | Paper Runner Polling | market data / strategy / engine deterministic polling loop | ACCEPTED | 3 | H06 |
| H770 | Paper Market Data Boundary | runner 消費 canonical-style MarketBar，不呼叫 broker行情 native object | ACCEPTED | 3 | H06 |
| H810 | Duplicate Submission Protection | same order identity 不可 silent duplicate submit | IMPLEMENTED | 3 | H08 |
| H820 | Fill Delivery Idempotency | repeated status polling 不重覆交付相同 fill | ACCEPTED | 4 | H08 |
| H830 | Event Idempotency Key | persisted/live OrderEvent future explicit idempotency identity | DESIGN_FROZEN | 4 | H08 |
| H840 | Safe Retry Policy | timeout / reconnect retry 不得造成 duplicate economic order | NOT_DESIGNED | 5 | H08 |
| H910 | EXIT Intent Generation | opposite direction transition 先要求 exit current exposure | DESIGN_FROZEN | 4 | H07 |
| H920 | Confirmed FLAT Gate | 未確認 account flat 不得 enter opposite side | DESIGN_FROZEN | 5 | H07,H08 |
| H930 | Re-Evaluation Gate | FLAT 後重新跑 strategy / decision / risk | DESIGN_FROZEN | 5 | H07 |
| H940 | Opposite ENTER | only after fresh accepted decision/risk | DESIGN_FROZEN | 4 | H07 |

---

## Post-Runtime Recovery Decision Checkpoint

ADR-002 R-02 and R-04A-E are authoritative for the current OMS/recovery correction。

Required correction direction：

- sequence-0 PENDING commits before broker side effect。
- durable PENDING already contains immutable broker_client_order_ref。
- all SUBMIT retries for one canonical order reuse the same broker_client_order_ref。
- broker_order_id remains a separate broker-assigned identity。
- BrokerActionAttempt is durable before SUBMIT/CANCEL broker side effect。
- BrokerActionAttempt / Resolution are not OrderStatus。
- one unresolved action attempt per order/action is enforced transactionally。
- no attribute/time heuristic may become recovery identity authority。
- OrderEvent means canonical material order-lifecycle evidence；it is not restricted to literal broker callback messages。
- BROKER_DISCOVERY may produce a canonical recovery-sourced OrderEvent。
- recovery must not fabricate unsupported intermediate lifecycle events。
- direct PENDING -> PARTIALLY_FILLED / FILLED transitions must be supported when evidence proves them。
- PARTIALLY_FILLED -> PARTIALLY_FILLED with new Fill evidence is a material same-status lifecycle change。
- Fill reconstruction requires verified deal-level restart-stable identity。
- callback-only identity does not satisfy restart recovery by itself。
- cumulative broker quantity cannot synthesize missing Fill evidence。
- late lower-information callback cannot regress projection。
- contradictory authoritative discovery requires explicit conflict/incomplete evaluation。
- terminal canonical acceptance seals lifecycle and economics。
- after terminal acceptance no extra Fill / filled quantity / average price / expected-position enrichment is permitted。
- canonical Fill set is the internal filled-economic authority。
- broker aggregates remain external reconciliation evidence。
- live/recovery/broker-action persistence must share one BrokerAccount authority-commit primitive。
- one account revision contains at most one canonical OrderEvent。
- no broker network I/O occurs while account authority lock is held。

Broker capability gates remain for Shioaji client-ref round-trip、exact FillKey、event tracking、PreSubmitted/Inactive/Failed semantics and quantity modification。

R-04F/G/H remain open。

This documentation checkpoint does not promote H lifecycle values and does not authorize runtime correction。

## CURRENT / TARGET / MIGRATION

CURRENT：

- Order / Fill / status foundation 位於 `backtest.models`。
- Broker ABC 有 submit / query / fills / cancel。
- partial fill / dedup / terminal lifecycle 已完成。
- PaperBroker / PaperTradingEngine / Runner 已存在。
- OrderFactory 使用 ENTRY / EXIT naming。
- GAP-BROKER-001 已建立 explicit OrderIntent / PositionEffect；Shioaji execution 不再由 order_id prefix 推定 New/Cover。

TARGET：

- canonical Order / Fill / OrderEvent / OrderIntent / PositionEffect 位於 `trading.execution`。
- execution semantics 與 broker-native mapping 分離。
- OMS 能 persistence / recovery / idempotency。

MIGRATION：

- GAP-BROKER-001 已完成 explicit OrderIntent / PositionEffect runtime foundation。
- New/Cover prefix inference 已移除。
- existing PaperBroker / Backtest consumers 保持 compatibility。
- 不為 ownership cleanup mass-move unrelated models。

---

## Connections

| From | To | Contract |
|---|---|---|
| G400/G900 | H200 | target / RiskDecision |
| H200 | H300/H500 | explicit execution intent |
| H150/H200 | I300 | broker-neutral order + effect |
| I400 | H300/H400 | broker status / deals → canonical state |
| H400 | J300 | Fill / OrderEvent 更新 expected AccountPosition |
| H500 | K300/K600 | execution persistence / event ledger |
| J600/L | H900 | reconciliation / live readiness gate |

---

## Authority

- OrderIntent：economic execution request semantics。
- Order：requested broker-neutral execution object。
- OrderEvent：execution lifecycle event。
- Fill：actual execution evidence。
- AccountPosition：不是 H authority，只由 execution result projection 更新。
- broker native Trade / Order：I Domain。

---

## Key Invariants

- Order ID 命名不得承擔 OPEN/CLOSE business semantics。
- PositionEffect 必須 explicit。
- Fill dedup 必須 deterministic。
- terminal order 不得 silent 回到 non-terminal state。
- retry 不得產生 duplicate economic order。
- direction reversal 必須 EXIT → confirmed FLAT → re-evaluate → ENTER。
- corrective reconciliation execution 在 GAP-BROKER-001 前禁止。

---

## Current GAP Mapping

- H210-H250 / H910-H940 → GAP-BROKER-001。
- H440/H510-H550/H830-H840 → GAP-08 / production OMS follow-up。
- production simulation fault model → L Domain / GAP-SIM-001。
- ownership migration → GAP-ARCH-001 bounded slices。

---

## GAP-BROKER-001 Architect Design Freeze

Status：

DESIGN_FROZEN。

Canonical owner：

    trading/execution.py

### PositionEffect

Canonical enum：

    OPEN
    REDUCE
    CLOSE

不得加入：

    REVERSE

Semantics：

- OPEN：增加指定 position direction 的 exposure；可為 FLAT → position，或同方向 ADD。
- REDUCE：減少 existing position，但 execution 後 quantity 必須仍大於 0。
- CLOSE：減少 existing position 至 exactly FLAT。
- opposite-side transition 不得用單一 intent 直接 reversal。
- reversal 固定 EXIT / CLOSE → confirmed FLAT → re-evaluate → OPEN opposite。

### OrderIntent

建立 immutable broker-neutral OrderIntent。

至少：

    intent_id: str
    correlation_id: str
    causation_id: str | None
    position_direction: PositionDirection
    position_effect: PositionEffect
    quantity: int > 0
    target_position_ref: str | None
    risk_decision_ref: str | None

Rules：

- extra fields forbid。
- intent_id / correlation_id trim 且不可 blank。
- optional refs 若存在不可 blank。
- PositionDirection 使用 trading.account.PositionDirection。
- trading.execution 不得 import backtest models。
- typed TargetAccountPosition / RiskDecision persistence identity 尚未完成，因此 refs 保持 optional opaque reference。
- provenance persistence 留 GAP-PERSIST-001。

### PositionEffect Validation

建立 pure validation seam。

Input：

    OrderIntent
    AccountPosition | None

Rules：

- expected=None：只允許 OPEN。
- expected!=None：intent position_direction 必須與 existing expected direction 一致。
- OPEN：允許同方向增加 exposure。
- REDUCE：0 < intent.quantity < expected.quantity。
- CLOSE：intent.quantity == expected.quantity。
- REDUCE / CLOSE quantity > expected.quantity：reject。
- opposite direction while non-FLAT：reject。
- validation 是 pure；不得 submit、mutate 或 repair broker state。

### Legacy Order Compatibility

Existing backtest.models.Order 保持 mechanical order contract。

Legacy Order.direction 在本 migration slice 明確解讀為：

    position direction

不是 broker-native Buy / Sell action。

因此：

- OPEN LONG 的 native action 是 Buy。
- OPEN SHORT 的 native action 是 Sell。
- CLOSE / REDUCE LONG 的 native action 是 Sell。
- CLOSE / REDUCE SHORT 的 native action 是 Buy。

不得再把 Order.direction 單獨直接等同 broker action。

### Broker Submission Compatibility

Existing execution Broker port 保持同一 capability。

本 GAP 允許 bounded signature extension：

    submit_order(
        order,
        *,
        intent: OrderIntent | None = None
    )

Rules：

- generic / PaperBroker caller 可暫時省略 intent，以保持 existing paper/backtest compatibility。
- ShioajiBroker submission 必須要求 explicit intent。
- ShioajiBroker 收到 intent=None 必須 fail fast。
- 不得從 order_id、signal_id、prefix 或 caller name 推定 PositionEffect。

### Order / Intent Consistency

Shioaji submission 前至少驗證：

- intent.quantity == order.quantity。
- intent.position_direction value == legacy order.direction value。
- mismatch 必須 explicit error。

### Out of Scope

- persistence。
- corrective reconciliation。
- account startup readiness。
- full Order ownership migration。
- full adapter relocation。
- direct reversal。
- DayTrade business semantics。
- broker Auto open/close inference。

## GAP-08EFGHI OMS Dependency Freeze

Status：DESIGN_FROZEN。

Implements：

H170 H440 H450 H510 H520 H530 H540 H550 H830。

Canonical owner：

    trading/execution.py

Legacy backtest Order / Fill remain compatibility models；no big-bang migration。

### Canonical OrderType

Exact values：

    MARKET
    LIMIT
    STOP

### Canonical OrderStatus

Exact values：

    PENDING
    SUBMITTED
    PARTIALLY_FILLED
    FILLED
    CANCELLED
    REJECTED

Terminal：FILLED / CANCELLED / REJECTED。

### Canonical Order

Immutable public projection model，minimum fields：

    order_id
    intent_id
    correlation_id
    causation_id optional
    broker
    account_ref
    instrument_id
    contract_id optional
    position_direction
    position_effect
    order_type
    quantity
    requested_price Decimal optional
    status
    filled_quantity
    average_fill_price Decimal optional
    created_at
    broker_order_id optional
    version

Rules：

- quantity > 0。
- 0 <= filled_quantity <= quantity。
- price uses finite Decimal；legacy float adapter converts via Decimal(str(value)) only。
- all timestamps timezone-aware UTC。
- broker_order_id once assigned cannot change to a different value。
- version equals last applied OrderEvent sequence。

Status invariants：

- PENDING / SUBMITTED：filled_quantity = 0。
- PARTIALLY_FILLED：0 < filled_quantity < quantity。
- FILLED：filled_quantity = quantity。
- CANCELLED：0 <= filled_quantity < quantity；partial-then-cancelled is valid。
- REJECTED：filled_quantity = 0。

### Canonical Fill

Immutable evidence model：

    fill_id
    order_id
    order_event_id
    correlation_id
    causation_id
    broker
    account_ref
    instrument_id
    contract_id optional
    broker_order_id optional
    broker_trade_id optional
    broker_deal_id optional
    occurred_at
    quantity
    price Decimal
    commission Decimal

Rules：

- fill_id is internal stable identity。
- causation_id == order_event_id。
- broker native IDs remain separate opaque identities。
- broker deal identity when present is persisted and deduplicated explicitly。

### OrderEvent

Immutable append-only event model：

    event_id
    order_id
    previous_status optional
    status
    occurred_at
    received_at
    sequence
    filled_quantity
    average_fill_price Decimal optional
    broker_order_id optional
    idempotency_key
    correlation_id
    causation_id
    reason optional

Sequence：

- starts at 0。
- sequence 0 = creation event：previous_status=None / status=PENDING。
- subsequent event sequence must be exactly previous version + 1。
- per-order sequence cannot gap or regress。

Correlation：

- Order copies intent_id / correlation_id / causation_id from OrderIntent。
- every OrderEvent keeps same correlation_id。
- first event causation_id = intent_id。
- later event causation_id = immediately preceding OrderEvent.event_id。
- Fill causation_id = producing OrderEvent.event_id。

Idempotency：

- EventLedger source = OMS。
- entity_type = ORDER。
- entity_id = order_id。
- idempotency scope = ORDER_EVENT:<order_id>。
- caller supplies stable nonblank idempotency_key。
- identical replay -> DUPLICATE。
- same identity/sequence/key with different canonical content -> explicit conflict。

Legal state transitions：

- creation None -> PENDING。
- PENDING -> SUBMITTED / PARTIALLY_FILLED / FILLED / CANCELLED / REJECTED。
- SUBMITTED -> PARTIALLY_FILLED / FILLED / CANCELLED / REJECTED。
- PARTIALLY_FILLED -> PARTIALLY_FILLED / FILLED / CANCELLED。
- terminal state accepts no new unique lifecycle event。
- duplicate terminal callback is handled by idempotency before transition application。

OMS authority：

- append-only OrderEvent + Fill = historical evidence。
- Order row = mutable derived projection。
- recovery reconstructs/validates projection against persisted evidence；projection never replaces evidence authority。

H840 Safe Retry remains outside scope。

---

## Domain Acceptance

- H01～H08 全部有 leaf mapping。
- explicit economic intent 與 mechanical order 分離。
- PaperBroker 與 SimulationBroker 責任不混淆。
- current unsafe prefix inference 有唯一 replacement path。

## Recovery Decision Checkpoint 4 — R-04F/G/H

R-04A-H are architecture-decided；ADR-002 is authoritative。

Execution/OMS correction direction：

- broker-observed terminal does not itself authorize canonical terminal。
- FILLED requires complete canonical Fill evidence。
- CANCELLED permits prior/reconstructed fills with filled_quantity < quantity。
- terminal economics are sealed after canonical terminal acceptance。
- recovery classifications are not OrderStatus。
- no blind SUBMIT/CANCEL retry。
- unresolved BrokerActionAttempt blocks automatic re-invocation。
- verified durable NOT_DISPATCHED is the only currently frozen automatic reinvocation exception after an attempt exists。
- terminal Order is never revived；later business submission uses a new OrderIntent / Order。
- BrokerAccount READY / REVIEW / HALT is operational readiness and does not itself advance economic AccountStateHead。

No runtime correction is authorized by this checkpoint。
