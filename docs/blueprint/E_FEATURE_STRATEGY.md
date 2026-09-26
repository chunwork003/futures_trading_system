# E — Feature / Strategy

## Status

BUILDING / PROVISIONAL until Blueprint baseline acceptance。

---

## Domain Purpose

將 canonical market observations 轉成 deterministic feature state，再由 versioned strategy definition / instance 產生 logical strategy intent。

此 Domain 不直接決定 physical broker position。

主要 current packages：

- `features/`
- `strategy/`
- `strategies/`

---

## Capability Groups

| Group | Name | Responsibility |
|---|---|---|
| E100 | Feature Contracts | feature calculator / pipeline contract |
| E200 | Batch Features | historical batch feature calculation |
| E300 | Incremental Market / Feature State | paper/live incremental update |
| E400 | StrategyDefinition | algorithm identity / version / factory contract |
| E500 | StrategyInstance | versioned config + market scope |
| E600 | Strategy Registry / Runner | resolve / instantiate / run strategies |
| E700 | Strategy Configuration / Ownership | config lifecycle / package migration |

---

## Engineering Leaves

| ID | Name | Purpose | Lifecycle | Weight | Maps |
|---|---|---|---|---:|---|
| E110 | Feature Base Contract | reusable feature calculator contract | ACCEPTED | 2 | E01 |
| E120 | Feature Function Contract | DataFrame → DataFrame reusable pipeline function | ACCEPTED | 2 | E01,E02 |
| E130 | Feature Naming / Registration | stable feature/pipeline lookup identity | ACCEPTED | 2 | E02 |
| E140 | Deterministic Feature Contract | identical bars/config → identical feature result | DESIGN_FROZEN | 3 | E01,E02 |
| E210 | Price Features | price-derived batch features | ACCEPTED | 2 | E01 |
| E220 | Trend Features | moving average / trend-derived features | ACCEPTED | 2 | E01 |
| E230 | Momentum Features | momentum-derived batch features | ACCEPTED | 2 | E01 |
| E240 | Volatility Features | volatility-derived batch features | ACCEPTED | 2 | E01 |
| E250 | Volume Features | volume-derived features | ACCEPTED | 2 | E01 |
| E260 | FeatureBuilder Pipeline | backward-compatible standard feature pipeline | ACCEPTED | 2 | E02 |
| E270 | FeatureRegistry | named reusable pipeline registration / lookup | ACCEPTED | 2 | E02 |
| E310 | Incremental Feature State Contract | per-bar stateful update，不掃完整歷史 | NOT_DESIGNED | 4 | E03 |
| E320 | Incremental Warmup | historical warmup → live state transition | NOT_DESIGNED | 4 | E03 |
| E330 | Incremental Reconstruction | restart 後可 deterministic reconstruct state | NOT_DESIGNED | 4 | E03 |
| E340 | Feature Version Identity | persisted/live state 可知道 feature algorithm/version | DESIGNED | 3 | E03,E05 |
| E350 | Incremental / Batch Equivalence | incremental result 與 batch reference 在定義範圍內一致 | NOT_DESIGNED | 4 | E03 |
| E410 | Strategy Definition Identity | strategy_id / algorithm identity | ACCEPTED | 3 | E04,E05 |
| E420 | Strategy Version | strategy algorithm version 可追蹤 | ACCEPTED | 3 | E05 |
| E430 | Strategy Base Contract | concrete strategy 遵循共同 input/output contract | ACCEPTED | 3 | E04 |
| E440 | Concrete Strategy Implementations | EMA / trend state 等 concrete algorithm | ACCEPTED | 2 | E04 |
| E510 | Strategy Instance Identity | definition + versioned configuration 的 runtime instance | DESIGN_FROZEN | 4 | E05 |
| E520 | Instrument / Timeframe Scope | StrategyInstance 綁定 instrument / timeframe scope | DESIGN_FROZEN | 3 | E05 |
| E530 | Config Versioning | parameter configuration 可追蹤且不能持倉中 silent mutate | DESIGN_FROZEN | 4 | E05 |
| E540 | Safe Configuration Boundary | config change 在安全 boundary 生效 | DESIGN_FROZEN | 3 | E05 |
| E610 | Strategy Registry | strategy definition lookup / factory resolution | ACCEPTED | 2 | E05,E06 |
| E620 | Multi-Strategy Runner | 多策略獨立執行並產生 independent outputs | ACCEPTED | 4 | E06 |
| E630 | Strategy Output Isolation | strategy 不直接 mutate account physical position | DESIGN_FROZEN | 4 | E06 |
| E640 | Strategy Error Isolation | strategy failure 不得 silent corrupt 其他 strategy state | DESIGNED | 3 | E06 |
| E710 | `strategy/` Ownership | framework / registry / runner target ownership | IMPLEMENTED | 2 | E07 |
| E720 | `strategies/` Ownership | concrete implementation target ownership | IMPLEMENTED | 2 | E07 |
| E730 | Duplicate Ownership Migration | duplicated registry/base/config 逐 slice 整理 | DESIGNED | 3 | E07 |

---

## CURRENT / TARGET / MIGRATION

CURRENT：

- batch features 已成熟。
- FeatureBuilder / FeatureRegistry 已存在。
- `strategy/` 與 `strategies/` 並存。
- multi-strategy runner 已存在。
- incremental feature / market state 尚未完成。

TARGET：

- batch 與 incremental 共用明確 feature semantics。
- StrategyDefinition != StrategyInstance。
- strategy 只產生 logical intent / virtual state。
- physical position decision 交給 G Domain。

MIGRATION：

- 不在一般 feature/strategy Work Package mass rename `strategy/` / `strategies/`。
- duplication cleanup 只有 bounded consumer slice 才做。
- incremental state 由 GAP-09 獨立實作。

---

## Connections

| From | To | Contract |
|---|---|---|
| D300 | E100/E300 | canonical market observation |
| E100/E200 | E400/E500 | feature state |
| E400/E500 | G100 | strategy intent |
| E600 | G200 | independent strategy virtual state/input |
| K500 | E300/E500 | future recovered feature / strategy state |

---

## Authority

- feature calculation semantics：E Domain。
- strategy algorithm identity：StrategyDefinition。
- parameterized runtime strategy：StrategyInstance。
- strategy physical account exposure：不是 E Domain authority。

---

## Technical Sources

- SRC-POLARS-001。
- SRC-PYDANTIC-001。
- SRC-ADR-001。

---

## Key Invariants

- feature calculation 必須 deterministic。
- paper/live 不得每根 bar 重算完整 historical dataset。
- StrategyDefinition != StrategyInstance。
- StrategyInstance 持倉期間不得 silent mutate config。
- strategy 不直接決定 broker physical position。
- multi-strategy conflict 由 G Domain 處理。

---

## Current GAP Mapping

- E310-E350 → GAP-09。
- E730 → GAP-ARCH-003。
- strategy config / instance deeper operational integration → future bounded Work Package。

---

## GAP-08EFGHI Strategy Identity Dependency Freeze

Status：DESIGN_FROZEN。

Implements in this Work Package：

- E510 Strategy Instance Identity。
- E520 Instrument / Timeframe Scope。

E530 / E540 remain existing DESIGN_FROZEN constraints；this Work Package does not claim full runtime config-change lifecycle acceptance。

Canonical owner：

    strategy/instance.py

### StrategyInstance

Immutable public model：

    strategy_instance_id: str
    strategy_id: str
    strategy_version: str
    config_version: str
    config_fingerprint: str
    instrument_id: int > 0
    timeframe: str
    config_json: JSON object

Rules：

- strings trim / nonblank。
- config_json deterministic canonical JSON object。
- config_fingerprint = SHA-256 of canonical config_json。
- config fingerprint mismatch rejected。
- Normal recovery/activation requires durable strategy state to resolve to the exact governing StrategyDefinition / implementation revision。
- A different implementation revision may consume prior durable state only inside an explicitly authorized compatibility/migration transition；it may not silently activate from deployment presence alone。
- `TRANSITION_IN_PROGRESS` is not StrategyTradingReady；completed POST_TRANSITION must establish durable state/provenance compatible with the new governing implementation revision。
- config change does not silently mutate an existing persisted instance。
- a material configuration change requires a new immutable config version plus an explicit lifecycle compatibility decision。
- an authorized compatible transition may preserve strategy_instance_id；an incompatible/identity-breaking transition requires a new StrategyInstance。
- restart/config loading never decides same-instance continuity implicitly。
- symbol/display text is not canonical instrument identity。

StrategyDefinition != StrategyInstance。

K520 incremental feature state remains excluded。

---

## Domain Acceptance

- E01～E07 全部有 leaf mapping。
- batch / incremental responsibility 清楚。
- StrategyDefinition / StrategyInstance distinction 明確。
- strategy / strategies migration 不造成 big-bang cleanup。

## Decision Checkpoint 5C — Strategy Identity / Lifecycle Authority

R-08 / R-09 are authoritative for deeper operational StrategyInstance identity/config recovery semantics。

Key authority distinctions：

- `strategy_instance_id` = stable opaque StrategyInstance lifecycle identity。
- `instrument_id` = canonical StrategyInstance instrument binding。
- canonical instrument binding is not executable ContractSpec identity unless the D Domain explicitly defines equivalence。
- legacy/display `symbol` is non-authoritative compatibility input。
- StrategyConfigVersion is not StrategyInstance identity。
- StrategyConfigVersion is not sufficient to identify strategy behavior。
- exact governing StrategyDefinition / implementation revision is separately required。
- DecisionPolicyVersion remains distinct from StrategyConfigVersion。

V1 may constrain one StrategyInstance to one canonical instrument binding；this is a V1 cardinality constraint，not an identity equivalence。

Material strategy state/output must retain exact applicable config + implementation provenance。

Current runtime fields such as `strategy_version` / `config_version` remain implementation candidates only；this checkpoint does not claim runtime conformance to the final operational authority model。

## Recovery Decision Checkpoint 5E — Market Completeness Readiness Dependency

R-14 market-data completeness is a StrategyTradingReady / DecisionCohortTradingReady dependency where required by the StrategyInstance/cohort contract。

StrategyRestoreValid does not imply completeness and does not imply StrategyTradingReady。

If required canonical completeness cannot be positively proven by an approved authority，the dependent StrategyInstance/cohort remains NOT_READY。

Market-data completeness failure does not by itself corrupt BrokerAccountExecutionReady。

Independent account-protection/risk/recovery actions remain subject to their own market-data/pricing/currentness prerequisites。

Historical COMPLETE does not automatically remain applicable for current activation。

A readiness-relevant completeness proof requires deterministic currentness validation against relevant observation/candidate/session/calendar/policy changes。

K520 remains GAP-09-owned；R-14 COMPLETE does not prove derived feature/state irrelevance to historical observation corrections。
