# Current State

## Repository Baseline

Repository：

`futures_trading_system`

Branch：

`master`

Architecture baseline：

`771f10f`

GAP-ACCOUNT-001 execution authorization baseline：

`5e24960`

Actual runtime execution HEAD：

由每次 Work Package precheck 取得。

本文件不保存「精確 current HEAD」，避免 documentation commit 造成自我參照與立即 stale。

Recorded full regression：

934 passed / 4 skipped

Known warning：

1 PytestCacheWarning / GAP-ENV-001。

Known local untracked：

`data/`

`data/` 不得自動 stage。

---

## Blueprint Baseline

Status：

AUTHORITATIVE。

Baseline commit：

`432c48fb63c3d8d2760c0f2f5338e205ded63d30`

Engineering inventory：

- A～O V1 Domains。
- 603 engineering leaves。
- total weight 2137。
- Blueprint IDs / source / authority / traceability / metrics 已啟用。

GAP-ACCOUNT-001：

COMPLETED / ACCEPTED。

Accepted runtime commit：

`50813b679f818f3837a9f50fdcda9921495ab507`

Blueprint launch gate 已完成使命，不再阻塞 runtime。

## Current Phase

Current milestone：M6 — Persistence / Recovery / Provenance。

GAP-08ABCD：COMPLETED / ACCEPTED。

Current Work Package：

GAP-08EFGHI — Operational Persistence + Recovery。

Blueprint：35 leaves / weight 151。

Runtime implementation：COMPLETED_CANDIDATE。

Runtime commit：`6b62239bca1d11543944f9f078e577e16010bcbf`。

Runtime verification：934 passed / 4 skipped / 1 warning。

User-observed 5HR usage：28%。

Architecture acceptance：HOLD。

Reason：post-runtime review identified recovery/execution correctness gaps and underspecified semantics。

Decision checkpoint：

- R-01 DECIDED / CORRECTION_REQUIRED。
- R-02 DECIDED / CORRECTION_REQUIRED。
- R-03A DECIDED / CORRECTION_REQUIRED。
- R-03B DECIDED / CORRECTION_REQUIRED。
- R-03C OPEN。
- R-03D OPEN。
- R-04 OPEN / mandatory dependency。

Authoritative detailed record：

`docs/adr/ADR-002-RECOVERY-CONSISTENCY-MARKET-OBSERVATION.md`

Runtime authorization：NOT_AUTHORIZED_FOR_FURTHER_EXECUTION。

Launch Gate：HOLD_FOR_POST_RUNTIME_ARCHITECTURE_DECISIONS。

35 / 151 must not be counted as ACCEPTED yet。

K520：DEFERRED_TO_GAP_09。

PG17 / PG18：PENDING_INTEGRATION_VERIFICATION。

Official lifecycle metric remains the 47.92% architecture-freeze baseline until correction/acceptance rebase。

Level 3B：NOT_ENABLED。

## Existing Major Foundation

已完成或高度成熟：

- historical ingestion。
- validation / cleaning。
- bar aggregation。
- Parquet / DuckDB analytical layer。
- trading calendar foundation。
- batch features。
- strategy framework。
- deterministic backtest。
- LONG / SHORT。
- SL / TP。
- commission / slippage。
- analysis / optimization。
- OOS / WFO。
- Monte Carlo。
- paper trading。
- async order lifecycle。
- partial entry / exit。
- strategy virtual positions。
- conflict resolution。
- TargetAccountPosition。
- attribution / netting。
- direction-change wait-for-flat。
- portfolio risk。
- position sizing。
- capital management。
- Shioaji adapter foundation。
- InstrumentSpec。
- ContractSpec。
- TradingSessionRef。
- MarginSchedule。
- BrokerInstrumentReference。
- actual canonical multiplier consumer。
- actual canonical margin consumer。
- BrokerAccount。
- canonical internal AccountPosition foundation。
- BrokerPositionSnapshot。
- read-only broker account / position query ports。
- Sinopac pure account / position mapping。
- broker contract reverse resolution。
- pure expected / actual pairwise reconciliation foundation。
- ReconciliationResult / policy / case lifecycle。
- deterministic multi-position collection reconciliation。
- startup reconciliation readiness gate。
- broker-neutral OrderIntent。
- PositionEffect OPEN / REDUCE / CLOSE。
- pure PositionEffect validation。
- explicit Shioaji Buy / Sell + New / Cover mapping。
- order-ID New/Cover inference removed。

---

## Critical Missing V1

主要剩餘：

- AccountPosition fill/event projection。

- operational PostgreSQL。
- trading persistence。
- restart recovery。
- decision/risk provenance。
- incremental feature state。
- SimulationBroker。
- LIVE authorization / safety。
- Python service API。
- ASP.NET Core Application。
- React Workspace。
- operational review / audit。

## Progress

Total V1 capability blocks：

92。

Engineering leaves：

603。

+

44.17%。

Architecture Design Coverage：87.60%。
Design Freeze Coverage：52.22%。
Runtime Implementation：39.59%。
Unit Verification：36.36%。
Integration Verification：36.27%。
Accepted Capability：36.27%。

Capability status：

COMPLETE 12 / PARTIAL 49 / NOT_STARTED 31。

Readiness：

- Operational：NOT_READY。
- Production Live：BLOCKED。
- LIVE_AUTO：NOT_AUTHORIZED。

Latest accepted runtime：

`98dc38ce39bdab191ce0bc6d71e37ef69059ec9c`

## Automation Status

### Level 1

Manual Work Package relay。

Validated。

### Level 2

Bounded autonomous bundle。

Validated by GAP-07-CLOSE。

### Level 3A

Repository queue + ACTIVE full Work Package。

Formal runtime calibration samples：7。

Completed runtime samples：

- GAP-ACCOUNT-001：12%。
- GAP-BROKER-001：14%。
- GAP-RECON-001A：11%。
- GAP-RECON-001B：16%。
- GAP-BROKER-002：10%。
- GAP-08ABCD：12%。
- GAP-08EFGHI：28%。

Observed average 5HR usage：14.71%。

Total implementation correction cycles：4。

GAP-08EFGHI runtime test result is PASS but architecture acceptance is HOLD；this sample is retained for sizing calibration。

### Level 3B

Continuous autonomous queue execution。

ELIGIBLE_FOR_EVALUATION。

NOT_ENABLED。

Persistence/recovery mainline 不因 Level 3A 樣本數自動升級 Level 3B。

---

## Automation Efficiency Observation

Formal Level 3A runtime samples：

| Sample | Work Package | 5HR | Files Read | Files Changed | Tool Ops | Corrections | Regression |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | GAP-ACCOUNT-001 | 12% | 8 | 12 | 18 | 0 | 776 |
| 2 | GAP-BROKER-001 | 14% | ~22 | 20 | 24 | 0 | 800 |
| 3 | GAP-RECON-001A | 11% | 8 | 2 | 19 | 0 | 821 |
| 4 | GAP-RECON-001B | 16% | 8 | 2 | 22 | 1 | 847 |
| 5 | GAP-BROKER-002 | 10% | 12 | 3 | 17 | 0 | 869 |
| 6 | GAP-08ABCD | 12% | 8 | 15 | 23 | 1 | 897 |

Six-sample average：

12.50%。

Total implementation correction cycles：

2。

Sample 6：

- expanded bundle：19 leaves / weight 77。
- wall time：約 12m09s。
- retries：1。
- PG17 / PG18 integration：PENDING。
- token/context：UNAVAILABLE。

Observation：

larger coherent scope did not increase observed 5HR usage；however wall time / tool operations / correction behavior remain part of sizing evaluation。

Policy：

- do not target a fixed quota percentage。
- merge same-context work when semantics permit。
- split only at genuine public-semantics / authority / safety / external-verification seams。

## Live State

Real-money LIVE_AUTO：

NOT AUTHORIZED。

原因：

Persistence、Recovery、Live Safety 尚未完成。

---

## Current Active Work

Work Package：

GAP-08EFGHI Operational Persistence + Recovery。

Status：READY_FOR_EXECUTION。

Blueprint：35 leaves / weight 151。

Runtime Gate：RELEASED_ARCHITECTURE_FREEZE。

Runtime authorization：AUTHORIZED_FOR_LEVEL_3A_RUNTIME。

Execution Mode：LEVEL_3A_BOUNDED。

Recommended model：GPT-5.6 Sol / 中度。

Reason for 中度：

single bundle now crosses execution state machine、multi-table transaction、account reconciliation、strategy state reconstruction and recovery safety。

No runtime until freeze commit/push is verified。
