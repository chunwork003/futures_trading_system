# AI Handoff

## Repository

- Repository：`futures_trading_system`
- Branch：`master`
- HEAD：`1ae1aa8`
- Source of truth：`CURRENT_STATE.md`、`CURRENT_WORK.md`、`GAP_REGISTER.md`、本文件。

## Current Architecture Summary

Python = Quant / Data / Research / ML / AI engine。未來 C# / ASP.NET Core = Application / Server / Workflow / API / Realtime；React + TypeScript = main investment workspace。PostgreSQL + PostGIS = operational system of record / GIS；Parquet = 大型歷史與分析資料；DuckDB + Polars = 本機研究層。

Broker 必須保持 neutral。第一個 broker 是 Sinopac Shioaji；目前 futures-first，但不得阻塞 equity、ETF、其他資產或 property。

概念流程：`Market Data → Feature → Strategy → Strategy Intent → Multi-Strategy Decision Layer → Target Account Position → Risk → Order / OMS → Broker`。

## Completed Capabilities

Backtest core、LONG/SHORT、SL/TP、execution lifecycle、partial fill/exit、paper trading、multi-strategy decision、target account position、global risk、position sizing、capital position management、Shioaji adapter foundation。

## Current Milestone and Test Baseline

- GAP-07-A — Canonical Instrument Specification：COMPLETE。
- GAP-07-B — Canonical Contract Specification：implemented / review pending。
- Recorded regression baseline：660 passed（632 existing + 28 GAP-07-B tests）。
- Codex full pytest 曾因 TEMP directory permission setup errors；不是已確認 assertion regression。

## Confirmed Decisions

- `Strategy Position != Target Account Position != Account Position != Broker Actual Position`。
- Strategy 是邏輯意圖；Broker Position Controller 是實體帳戶控制，不可混同。
- 方向變更：`EXIT → confirm FLAT → re-evaluate → ENTER opposite side`；不得 silent direct reversal。
- 所有 material action 可追溯：`Signal → Decision → Risk → Order → Fill → Position → Trade → Review`。Expected 與 Actual 必須分離。
- DecisionContext 應支援 strategy/config/feature versions、market state、indicators、expected/actual price、fees、risk decision、strategy influence、correlation/causation IDs。
- `StrategyDefinition != StrategyInstance`；config 必須版本化，持倉期間不得 silent parameter mutation，預設在安全 boundary 生效。
- `LogicalAccount != BrokerAccount`；一個 broker account 可服務多個 logical account / capital bucket。V1 使用 manual capital；cross-strategy capital borrowing 預設 OFF。
- Modes：BACKTEST、SIMULATED、BROKER_PAPER、LIVE_CONFIRM、LIVE_AUTO。LIVE_AUTO 真實金流另需 authorization gate。
- ADR-001 已接受：canonical ownership、adapter dependency direction、compatibility strategy 與 migration sequence 已定義。
- Canonical TAIFEX instrument symbol 為 TX / MTX / TMF；broker 與 dataset alias 使用獨立 mapping namespace，不屬於 canonical instrument identity。
- `ContractSpec` 支援 monthly / quarterly / weekly / other listed series；continuous contract 維持獨立，broker contract code 仍由 adapter 負責。

## Persistence and Reconciliation Direction

Trading State 必須持久化 order、fill、position、strategy state、account/equity、event history，並支援 restart recovery 與 broker reconciliation。broker actual state 與 internal state 不一致時必須明確呈現；不得猜測。

## Known Risks / Open GAPs

優先參照 `GAP_REGISTER.md`：GAP-07、GAP-ARCH-001/002/003、GAP-BROKER-001、GAP-ACCOUNT-001、GAP-08、GAP-PERSIST-001、GAP-09、GAP-LIVE-001。另有 data governance、documentation drift、default branch 與 pytest TEMP environment 問題。

## Blocking Issues

Live / money risk、broker ambiguity、reconciliation、recovery、core regression、secrets/security 與 business logic 猜測均為 LEVEL 3 blocker：停止該 Work Package；互不依賴工作可繼續。

## Next Recommended Work

GAP-07-B 已實作並等待 review。後續 runtime 修改只能依 approved Work Package 與 ADR-001 migration sequence 執行；下一建議工作為 GAP-07-C Trading Session / Calendar Reference。

## Do Not Change

- 不得未經 Work Package 授權修改 runtime、tests、database 或 `data/`。
- 不得 silent unrelated fix、改寫 Git history、force push 或假設 trading / broker semantics。
- Day-7 是 Dynamic Sprint；不可為趕期限跳過測試、保留已知重大缺陷、以 fake data 冒充驗證或降低驗收標準。
- 超過 7 天需建立 Delay Review：原因、V1 影響、Post-V1 可否延後、scope creep、過度優化、拆分與模型選擇。

每個 major milestone 必須更新本文件一次。
