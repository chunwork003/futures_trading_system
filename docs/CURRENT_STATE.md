# Current State

- Repository：`futures_trading_system`
- Branch：`master`
- HEAD：`4205dad`
- Current phase：GAP-07 — Contract / Futures Specification
- M0-A：COMPLETE
- M0-B：COMPLETE；ADR-001 已 ACCEPTED 並完成 documentation commit。
- Latest completed：GAP-07-E3 Canonical Margin Actual Consumer Wiring
- Recorded regression baseline：745 passed（737 existing + 8 GAP-07-E3 tests）
- V1 estimated progress：40–50%（以 Work Package acceptance criteria 評估，非 LOC 或檔案數）

## Existing Core

- Backtest Core、LONG / SHORT、SL / TP、Execution Lifecycle。
- Partial Fill / Partial Exit、Paper Trading。
- Multi-Strategy Decision、Target Account Position、Global Risk。
- Position Sizing、Capital Position Management、Shioaji Adapter foundation。

## Critical Missing

- GAP-07 final acceptance / closure 尚待 Stage B；runtime implementation slices 已完成。
- Broker Account / Position Sync、Reconciliation。
- Trading Persistence、Restart Recovery、Incremental Feature / Market State。
- Simulation fault model、Operational PostgreSQL、Application API、Web Workspace。
- LIVE_AUTO control / recovery。

## Known Non-blocking

- Codex pytest TEMP permission：`C:\Users\CHUNs\AppData\Local\Temp\pytest-of-CHUNs` 曾出現 `PermissionError`。
- `data/` governance、docs drift、GitHub default branch `main` 與 development branch `master` 不一致、repository public。

細節與順序以 `GAP_REGISTER.md`、`CURRENT_WORK.md` 為準。
