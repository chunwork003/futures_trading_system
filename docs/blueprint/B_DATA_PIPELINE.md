# B — Data Pipeline

## Status

BUILDING / PROVISIONAL until Blueprint baseline acceptance。

---

## Domain Purpose

將外部歷史市場資料轉為可驗證、可清理、可聚合、可重現的 canonical historical dataset。

主要 current packages：

- `ingestion/`
- `cleaning/`
- `aggregation/`
- `storage/`

Historical authority：Parquet。

Analytical query：DuckDB / Polars。

此 Domain 不負責 live operational SOR。

---

## Capability Groups

| Group | Name | Responsibility |
|---|---|---|
| B100 | Source Acquisition | 外部資料來源與 raw acquisition |
| B200 | Raw Validation | schema、timestamp、structure、values |
| B300 | Cleaning | tick / bar 資料清理 |
| B400 | Aggregation | tick → bar、多 timeframe、session-aware |
| B500 | Historical Storage | Parquet、DuckDB、Arrow boundary |
| B600 | Provenance / Reproducibility | source / version / local data governance |
| B700 | Data QA / Monitoring | coverage、anomaly、source health |

---

## Engineering Leaves

| ID | Name | Purpose | Lifecycle | Weight | Maps |
|---|---|---|---|---:|---|
| B110 | Multi-Source Acquisition | 支援多個 historical source adapter | ACCEPTED | 3 | B01 |
| B120 | Source Request Boundary | source-specific request / retrieval 與 core data flow 分離 | ACCEPTED | 2 | B01 |
| B130 | Source Metadata | 保存來源、時間、symbol、source identity | IMPLEMENTED | 2 | B01,B06 |
| B140 | Raw-to-Validation Handoff | raw input 必須先通過 structural validation | ACCEPTED | 2 | B01,B02 |
| B210 | Schema Validation | required columns / type / structure 驗證 | ACCEPTED | 2 | B02 |
| B220 | Timestamp Validation | timestamp 可排序、可解析且不 silent coercion | ACCEPTED | 2 | B02 |
| B230 | Market Value Validation | OHLCV / tick value 基本市場資料合法性 | ACCEPTED | 2 | B02 |
| B240 | Duplicate / Ordering Validation | duplicate、ordering、structural anomaly 可偵測 | ACCEPTED | 2 | B02 |
| B250 | Missing / Coverage Validation | 缺段與資料 coverage 可識別 | IMPLEMENTED | 2 | B02 |
| B310 | Tick Cleaning | raw tick cleaning | ACCEPTED | 2 | B02 |
| B320 | Bar Cleaning | bar structural / value cleaning | ACCEPTED | 2 | B02 |
| B330 | Cleaning Auditability | cleaning 不應 silent 隱藏 source defect | IMPLEMENTED | 2 | B02,B06 |
| B410 | Tick-to-1m Aggregation | deterministic tick → 1 minute bar | ACCEPTED | 3 | B03 |
| B420 | Session-Aware Aggregation | aggregation 尊重 trading session boundary | ACCEPTED | 3 | B03 |
| B430 | Multi-Timeframe Aggregation | 5m / 15m / 30m / 60m 等 resample | ACCEPTED | 2 | B03 |
| B440 | Aggregation Determinism | 相同 input / rule 得相同 output | ACCEPTED | 2 | B03 |
| B510 | Canonical Parquet Storage | historical canonical dataset 以 Parquet 保存 | IMPLEMENTED | 3 | B04 |
| B520 | Parquet Schema / Partitioning | schema 與 partition 規則可持續演進 | IMPLEMENTED | 3 | B04 |
| B530 | DuckDB Analytical Query | local historical analytical query | IMPLEMENTED | 2 | B05 |
| B540 | Arrow / DataFrame Interop | DuckDB / Arrow / Polars boundary 可控 | IMPLEMENTED | 2 | B04,B05 |
| B610 | Dataset Provenance | dataset 可追到 source / transformation | DESIGNED | 3 | B06 |
| B620 | Reproducible Local Dataset | 研究資料版本與重建流程可重現 | DESIGNED | 3 | B06 |
| B630 | Local Data Governance | data/ 大型本機資料與 Git repo 分離 | DESIGN_FROZEN | 3 | B06 |
| B710 | Data QA Report | source / validation / cleaning QA 可彙總 | DESIGNED | 2 | B02,B06 |
| B720 | Source Coverage / Failure Monitoring | production data source failure / coverage 可觀測 | NOT_DESIGNED | 3 | B01,B06 |

---

## Operational Completeness Follow-Up — R-14 / GAP-DATA-001

R-03 defines canonical identity/revision/acceptance for observations that exist。

It does not define whether a missing candidate for an interval means legitimate no-trade activity or data-pipeline failure。

Historical B250 missing/coverage validation does not by itself prove production live completeness。

Until session/calendar-aware operational completeness semantics exist：

- no candidate received must not be silently treated as a valid empty/no-trade interval。
- continuous-interval feature/strategy consumers must not claim completeness when the missing interval cannot be proven irrelevant。
- source outage / transport failure / ingestion loss / legitimate market inactivity remain distinct future classifications。

Production source-health/coverage semantics map primarily to B720，with dependencies on D340 and K520。

This follow-up does not reopen R-03 identity decisions。

## Connections

| From | To | Contract |
|---|---|---|
| B100 | B200 | raw source data |
| B200 | B300 | validated raw data |
| B300 | B400 | cleaned tick / bar |
| B400 | B500 | canonical aggregated dataset |
| B500 | D300 | historical MarketBar / market observation input |
| B600 | F Research | reproducibility / provenance |

---

## State Authority

- Raw external data：source-owned。
- Clean canonical historical data：Parquet dataset。
- Analytical query state：DuckDB / Polars。
- Live operational state：不屬於 B Domain。

---

## External / Technical Sources

- SRC-POLARS-001。
- SRC-DUCKDB-001。
- SRC-PYARROW-001。

實際 historical vendor / source semantics 在對應 ingestion Work Package 中補受控 Source ID。

---

## Invariants

- Cleaning 不得修改交易 business semantics。
- Aggregation 必須 deterministic。
- DuckDB 不得成為 live operational SOR。
- `data/` 預設不得進 Git。
- richer canonical MarketBar ownership 由 D Domain 定義。

---

## Domain Acceptance

- B01～B06 全部有 leaf mapping。
- Parquet / DuckDB authority 清楚。
- raw → validation → cleaning → aggregation → storage flow 無 ambiguity。
- local data governance 與 provenance gap 可追蹤。
