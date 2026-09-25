# D — Canonical Domain

## Status

BUILDING / PROVISIONAL until Blueprint baseline acceptance。

---

## Domain Purpose

提供 broker-neutral、research/backtest/simulation/live 共用的 canonical market identity、contract specification、market observation、session reference、margin reference 與 broker identity mapping。

Canonical Domain 不負責：

- strategy decision。
- account expected state。
- broker API call。
- persistence ORM。
- backtest execution semantics。

主要 current package：

- `domain/`

---

## Capability Groups

| Group | Name | Responsibility |
|---|---|---|
| D100 | Instrument | product identity / static specification |
| D200 | Contract | listed contract identity / lifecycle specification |
| D300 | Market Observation | canonical OHLCV / market observation |
| D400 | Trading Session Reference | versioned calendar/session reference |
| D500 | Margin Reference | effective-dated canonical margin |
| D600 | Broker Instrument Identity | canonical ↔ broker-neutral external identity |
| D700 | Domain Validation / Repository Boundary | validation、resolution、consumer seam |

---

## Engineering Leaves

| ID | Name | Purpose | Lifecycle | Weight | Maps |
|---|---|---|---|---:|---|
| D110 | InstrumentSpec Identity | canonical instrument_id / symbol / exchange / asset type | ACCEPTED | 3 | D01 |
| D120 | Instrument Static Economics | multiplier / tick size / currency | ACCEPTED | 3 | D01 |
| D130 | Instrument Status | ACTIVE / INACTIVE 等生命周期狀態 | ACCEPTED | 2 | D01 |
| D140 | Instrument Validation | symbol / exchange / currency / positive economic fields | ACCEPTED | 2 | D01 |
| D150 | Legacy Instrument Compatibility | existing Instrument → InstrumentSpec bounded conversion | ACCEPTED | 2 | D01 |
| D210 | ContractSpec Identity | contract_id / instrument_id / canonical_code | ACCEPTED | 3 | D02 |
| D220 | Contract Series Type | MONTHLY / QUARTERLY / WEEKLY / OTHER | ACCEPTED | 2 | D02 |
| D230 | Contract Lifecycle Dates | listing / expiration / last trade / settlement | ACCEPTED | 3 | D02 |
| D240 | Contract Session Override Reference | listed contract 可參照特殊 session rule | ACCEPTED | 2 | D02,D03 |
| D250 | Contract Validation | lifecycle ordering / month / status validation | ACCEPTED | 2 | D02 |
| D260 | Legacy Contract Compatibility | existing Contract → ContractSpec bounded conversion | ACCEPTED | 2 | D02 |
| D310 | Canonical Market Observation Identity | timestamp / trade date / instrument / contract / timeframe | DESIGNED | 3 | D06 |
| D320 | OHLCV Observation | open / high / low / close / volume | IMPLEMENTED | 3 | D06 |
| D330 | Optional Market Metadata | amount / trade count / session / source / provenance | DESIGNED | 3 | D06 |
| D340 | Market Observation Time Semantics | timestamp timezone / session interpretation 明確 | DESIGNED | 4 | D03,D06 |
| D350 | Market Observation Validation | OHLC relationship / volume / identity / timestamp validation | DESIGNED | 3 | D06 |
| D360 | Existing Bar Migration Boundary | current `domain.bars.Bar` 保留，future richer canonical owner bounded migration | DESIGN_FROZEN | 3 | D06 |
| D410 | TradingSessionRef Identity | stable session_ref / exchange / timezone / rule_version | ACCEPTED | 3 | D03 |
| D420 | IANA Timezone Validation | session timezone 必須為有效 IANA zone | ACCEPTED | 2 | D03 |
| D430 | Calendar Rule Version Reference | domain 不內嵌整套 calendar rule，只持 stable reference | ACCEPTED | 2 | D03 |
| D440 | Contract Session Override | ContractSpec 可安全參照特殊 session | ACCEPTED | 2 | D03 |
| D510 | MarginScheduleEntry | effective-dated canonical margin reference | ACCEPTED | 4 | D04 |
| D520 | Margin Natural Key | instrument / contract / effective_date 唯一語意 | ACCEPTED | 3 | D04 |
| D530 | Margin Decimal Semantics | operational margin 使用 Decimal，不以 float 作 canonical money truth | ACCEPTED | 3 | D04 |
| D540 | Margin Effective-Date Resolution | as_of_date 明確解析 latest valid entry | ACCEPTED | 3 | D04 |
| D550 | Margin Source / Publication Metadata | source / published_at 可追溯 | ACCEPTED | 2 | D04 |
| D560 | Margin Authority Separation | canonical margin != RiskConfig override != broker actual margin | DESIGN_FROZEN | 4 | D04 |
| D610 | BrokerInstrumentReference | broker-neutral canonical ↔ broker code reference | ACCEPTED | 4 | D05 |
| D620 | Canonical-to-Broker Resolution | broker + canonical IDs + effective date → exact mapping | ACCEPTED | 3 | D05 |
| D630 | Broker-to-Canonical Reverse Resolution | broker contract code → exact canonical listed contract | ACCEPTED | 3 | D05 |
| D640 | Mapping Effective Range | effective_from / effective_to inclusive semantics | ACCEPTED | 2 | D05 |
| D650 | Mapping Ambiguity / Missing Errors | missing / duplicate mapping 明確 error，不猜測 | ACCEPTED | 3 | D05 |
| D660 | Native Object Exclusion | canonical mapping 不保存 broker SDK object | ACCEPTED | 3 | D05 |
| D710 | Canonical Resolution Seam | consumer 透過 explicit resolver / repository 取得 specification | ACCEPTED | 3 | D01-D05 |
| D720 | Domain Extra-Field Safety | canonical core model 不接受未授權 external/native 欄位 | IMPLEMENTED | 2 | D01-D05 |
| D730 | Canonical Identity Consistency | Instrument / Contract / Broker reference ID chain 不可混淆 | DESIGN_FROZEN | 4 | D01,D02,D05 |

---

## Current Runtime Paths

- `domain/instruments.py`
- `domain/contracts.py`
- `domain/bars.py`
- `domain/trading_session.py`
- `domain/margins.py`
- `domain/broker_instruments.py`

---

## Target Ownership

Canonical owner：

    domain/

Broker native object owner：

    adapters/<broker>/

Historical replay consumer：

    backtest/

Trading consumer：

    trading/

---

## Post-Runtime Recovery Identity Decision Checkpoint

ADR-002 R-03A / R-03B are authoritative for the current Market Observation correction review。

Key decisions：

- logical observation identity = instrument_id + listed contract_id when applicable + normalized timeframe + timezone-aware UTC interval_start_at。
- trade_date/session/source/OHLCV are not logical-key fields。
- listed futures without resolved contract_id reject/quarantine；no silent None fallback。
- synthetic/continuous series do not yet have operational recovery identity。
- observation revisions use deterministic content fingerprint + authority-local revision_seq。
- candidate != accepted revision；no canonical last-write-wins。
- StrategyStateSnapshot must ultimately reference immutable revision-specific observation evidence。
- accepted market-data correction in required recovery horizon -> REVIEW。
- classification-only correction may bypass REVIEW only when explicit verified strategy dependency proves it non-material。

R-03C / R-03D remain open；D310-D350 lifecycle values are not promoted by this checkpoint。


## CURRENT / TARGET / MIGRATION

### Instrument / Contract / Session / Margin / Broker Reference

CURRENT：

已存在 canonical foundation。

TARGET：

維持 `domain/` canonical ownership。

MIGRATION：

逐 consumer migration，不做 big-bang import rewrite。

### Market Observation

CURRENT：

`domain.bars.Bar` 已具有 timestamp、trade_date、symbol、contract、timeframe、OHLCV、trade_count、session、source。

TARGET：

完整 canonical Market Observation / MarketBar，能承載 identity、session、amount/provenance 等通用市場資訊。

MIGRATION：

保留 existing Bar compatibility；只有 consumer 需求出現時 bounded migration。

---

## Connections

| From | To | Contract |
|---|---|---|
| B500 | D300 | historical market observation |
| C200 | D400 | session reference |
| C400 | D200 | listed contract lifecycle |
| D100/D200 | E/F/G/H/I/J | canonical instrument / contract identity |
| D300 | E/F | market observation |
| D500 | G/F | margin reference |
| D600 | I/J | broker identity mapping |

---

## Authority

- InstrumentSpec：canonical product specification。
- ContractSpec：canonical listed contract specification。
- TradingSessionRef：calendar/session stable reference。
- MarginScheduleEntry：canonical effective-dated reference margin。
- BrokerInstrumentReference：broker-neutral mapping reference。
- Broker SDK objects：不是 D Domain authority。

---

## External Sources

- SRC-TAIFEX-TX-001。
- SRC-TAIFEX-MTX-001。
- SRC-TAIFEX-MARGIN-INDEX-001。
- SRC-TAIFEX-MARGIN-RULE-001。
- SRC-TAIFEX-CALENDAR-001。
- SRC-PYDANTIC-001。
- SRC-ADR-001。

---

## Key Invariants

- canonical symbol != dataset alias != broker product code != broker contract code。
- domain 不依賴 backtest / trading / adapter / ORM。
- MarginSchedule 不等同 scenario RiskConfig。
- broker actual margin 不等同 canonical reference margin。
- operational timestamp 必須最終 timezone-aware。
- native `sj.*` object 不得進 canonical model。
- reverse broker mapping ambiguous 時不得猜。

---

## Domain Acceptance

- D01～D06 全部有 leaf mapping。
- canonical ownership 唯一。
- CURRENT / TARGET / MIGRATION 清楚。
- MarketBar remaining work 有 bounded target。
- GAP-ACCOUNT-001 使用的 D630 已有 Blueprint identity。
