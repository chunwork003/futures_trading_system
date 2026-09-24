# Current State

- Repository：`futures_trading_system`
- Branch：`master`
- HEAD：`3c4ed81`
- Current phase：Post GAP-07 — Broker Account / Position Sync + Reconciliation
- M0-A：COMPLETE
- M0-B：COMPLETE；ADR-001 已 ACCEPTED 並完成 documentation commit。
- Latest completed：GAP-07 Contract / Futures Specification — CLOSED
- Recorded regression baseline：745 passed（737 existing + 8 GAP-07-E3 tests）
- V1 estimated progress：40–50%（以 Work Package acceptance criteria 評估，非 LOC 或檔案數）

## Existing Core

- Backtest Core、LONG / SHORT、SL / TP、Execution Lifecycle。
- Partial Fill / Partial Exit、Paper Trading。
- Multi-Strategy Decision、Target Account Position、Global Risk。
- Position Sizing、Capital Position Management、Shioaji Adapter foundation。

## Critical Missing

- Broker Account / Position Sync、Reconciliation。
- Trading Persistence、Restart Recovery、Incremental Feature / Market State。
- Simulation fault model、Operational PostgreSQL、Application API、Web Workspace。
- LIVE_AUTO control / recovery。

GAP-07 deferred follow-ups 不阻塞 closure：timezone-aware inbound boundary、session rule duplication、expiry-day consolidation、DuckDB margin refinement、broker actual margin snapshot、continuous roll、legacy `Order.contract` migration 與 broker capability matrix。細節以 `GAP_REGISTER.md` 為準。

## Known Non-blocking

- Codex pytest TEMP permission：`C:\Users\CHUNs\AppData\Local\Temp\pytest-of-CHUNs` 曾出現 `PermissionError`。
- `data/` governance、docs drift、GitHub default branch `main` 與 development branch `master` 不一致、repository public。

細節與順序以 `GAP_REGISTER.md`、`CURRENT_WORK.md` 為準。
