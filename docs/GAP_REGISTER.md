# GAP Register

新增 GAP 必須先寫入 **Newly Inserted**，標記 Added Date、Reason、Priority、Dependency、Status，再同步更新 Master Ordered GAP。禁止只在聊天或 commit message 記錄問題。

## Newly Inserted

| ID | Added Date | Reason | Priority | Dependency | Status |
|---|---|---|---|---|---|
| GAP-07-E3 | 2026-09-24 | 將 canonical margin resolution 接入 actual risk consumer；需明確 deterministic as_of_date injection | P1 | GAP-07-E2, GAP-07-D | Complete |
| GAP-07-E2 | 2026-09-24 | 將 canonical multiplier resolution seam 接入 actual BacktestEngine / Portfolio consumer path | P1 | GAP-07-E | Complete |
| GAP-07-F | 2026-09-24 | 建立 canonical identity 與 external broker codes 的 effective-dated mapping contract及 native lookup seam | P1 | GAP-07-E, ADR-001 | Complete |
| GAP-07-E | 2026-09-24 | 建立 Backtest / Risk explicit override 與 canonical specification 的 compatibility resolution seam | P1 | GAP-07-D, ADR-001 | Complete |
| GAP-07-MARGIN-001 | 2026-09-24 | Effective-date canonical margin、contract precedence 與 override separation；DuckDB 尚缺 currency/source/contract_id/published_at 且使用 DOUBLE，broker actual snapshot 未建立 | P1 | GAP-07-D | Partial — runtime domain and compatibility path complete; database/live pending |
| GAP-07-D | 2026-09-24 | 建立 canonical MarginScheduleEntry 與 effective-date resolver | P1 | GAP-07-C, ADR-001 | Complete |
| GAP-07-C | 2026-09-24 | 建立 canonical TradingSessionRef 與 `[open, close)` boundary policy | P1 | GAP-07-B, ADR-001 | Complete |
| GAP-07-SESSION-EXPIRY | 2026-09-24 | Expiry-day 13:30 close 僅存在 Resolver 特例，規則尚未集中 | P1 | GAP-07-SESSION-001 | Open — MUST FIX BEFORE LIVE |
| GAP-07-SESSION-001 | 2026-09-24 | Session rule/time 在 rules、source、resolver、normalizer 間重複 | P1 | GAP-07-C | Open — later session-rule slice |
| GAP-07-TIME-001 | 2026-09-24 | Operational timestamp 尚未全面建立 timezone-aware boundary | P1 | GAP-07-C | Open — MUST FIX BEFORE LIVE |
| GAP-07-B | 2026-09-24 | 建立 broker-neutral listed Contract Specification、series/lifecycle 與 legacy compatibility | P1 | GAP-07-A, ADR-001 | Complete |
| GAP-07-A | 2026-09-24 | 建立 broker-neutral canonical Instrument Specification 與 legacy compatibility | P1 | GAP-07-A0, ADR-001 | Complete |
| GAP-07-A0 | 2026-09-24 | 確認 canonical symbol 與 V1 official product semantics | P1 | GAP-07 pre-check | Complete |
| GAP-REPO-001 | 2026-09-24 | GitHub default branch `main`，開發使用 `master` | P2 | Governance decision | Open |
| GAP-REPO-002 | 2026-09-24 | `data/` 為未追蹤本機資產，需可重現性與提交治理 | P1 | Data governance design | Open |
| GAP-ENV-001 | 2026-09-24 | Codex pytest TEMP directory PermissionError | P2 | Environment access | Open |
| GAP-DOC-001 | 2026-09-24 | 舊文件 commit、測試與能力描述漂移 | P2 | M0-A | Open |
| GAP-ARCH-001 | 2026-09-24 | Backtest / Trading / Broker package boundary 未明確 | P1 | M0-B | Open |
| GAP-ARCH-002 | 2026-09-24 | domain/backtest model duplication | P1 | M0-B | Open |
| GAP-ARCH-003 | 2026-09-24 | `strategy/` 與 `strategies/` duplication | P2 | M0-B | Open |
| GAP-BROKER-001 | 2026-09-24 | explicit OrderIntent / PositionEffect；legacy `Order.contract` 仍直接作為 broker lookup key | P1 | GAP-07, M0-B | Open |
| GAP-BROKER-002 | 2026-09-24 | broker capability matrix 與 remaining mapping semantics / persistence | P2 | M0-B, GAP-07-F | Partial — mapping contract complete; capability matrix pending |
| GAP-PERSIST-001 | 2026-09-24 | Decision Provenance 未持久化 | P1 | GAP-08 | Open |
| GAP-SIM-001 | 2026-09-24 | SimulationBroker / fault injection 未建立 | P2 | Broker boundary | Open |
| GAP-APP-001 | 2026-09-24 | ASP.NET Core Application/API 未建立 | P1 | Operational state model | Planned |
| GAP-WEB-001 | 2026-09-24 | React/TypeScript Workspace 未建立 | P1 | Application API | Planned |
| GAP-LIVE-001 | 2026-09-24 | LIVE_AUTO authorization / runtime safety 未建立 | P0 | Reconciliation, persistence, OMS | Open |
| GAP-REVIEW-001 | 2026-09-24 | Trading Review / audit interface 未建立 | P2 | Decision provenance | Open |

## Master Ordered GAP

| Order | ID | Scope | Status |
|---:|---|---|---|
| 1 | M0-B | Architecture Boundary ADR | Complete / pending commit |
| 2 | GAP-DOC-001 | Documentation drift | Open |
| 3 | GAP-REPO-001 | Default branch governance | Open |
| 4 | GAP-REPO-002 | Local data asset governance | Open |
| 5 | GAP-ENV-001 | Codex pytest TEMP permission | Open |
| 6 | GAP-07-A0 | Canonical symbol / official product semantics decision | Complete |
| 7 | GAP-07-A | Canonical Instrument Specification | Complete |
| 8 | GAP-07-B | Canonical Contract Specification | Complete |
| 9 | GAP-07-C | Canonical Trading Session Reference | Complete |
| 9.1 | GAP-07-TIME-001 | Timezone-aware timestamp boundary | Open — MUST FIX BEFORE LIVE |
| 9.2 | GAP-07-SESSION-001 | Session rule duplication / boundary consistency | Open — later session-rule slice |
| 9.3 | GAP-07-SESSION-EXPIRY | Expiry-day special session rule consolidation | Open — MUST FIX BEFORE LIVE |
| 9.4 | GAP-07-D | Canonical Margin Schedule / Effective-Date Resolver | Complete |
| 9.5 | GAP-07-E | Backtest / Risk Compatibility Resolution | Complete |
| 9.6 | GAP-07-F | BrokerInstrumentReference / Broker Mapping Contract | Complete |
| 9.7 | GAP-07-E2 | Actual Backtest multiplier consumer integration | Complete |
| 9.8 | GAP-07-E3 | Margin actual risk consumer wiring | Complete |
| 9.9 | GAP-07-MARGIN-001 | Margin schema / broker actual completion | Partial — runtime domain and compatibility path complete; database/live pending |
| 9.10 | GAP-07 | Contract / Futures Specification final acceptance | Closure pending |
| 10 | GAP-ARCH-001 | Backtest / Trading / Broker package boundary | Open |
| 11 | GAP-ARCH-002 | Canonical domain/backtest model boundary | Open |
| 12 | GAP-ARCH-003 | Strategy package consolidation direction | Open |
| 13 | GAP-BROKER-001 | Explicit OrderIntent / PositionEffect | Open |
| 14 | GAP-BROKER-002 | Broker capability matrix / remaining mapping semantics | Partial — mapping contract complete; capability matrix pending |
| 15 | GAP-ACCOUNT-001 | Broker Account / Position Sync | Pending |
| 16 | GAP-08 | Trading State Persistence & Recovery | Pending |
| 17 | GAP-PERSIST-001 | Decision Provenance | Open |
| 18 | GAP-09 | Incremental Feature / Market State Engine | Pending |
| 19 | GAP-SIM-001 | SimulationBroker / fault injection | Open |
| 20 | GAP-LIVE-001 | LIVE_AUTO authorization / runtime safety | Open |
| 21 | GAP-REVIEW-001 | Trading Review / audit interface | Open |
| 22 | GAP-APP-001 | ASP.NET Core Application/API | Planned |
| 23 | GAP-WEB-001 | React/TypeScript Workspace | Planned |

## Entry Rules

- P0：money / live safety；P1：V1 architecture blocker；P2：重要但可分離；P3：Post-V1 deferred。
- GAP 不等於立即實作。先確認 dependency、acceptance criteria、owner 與可否獨立執行。
- 7 天可能延遲時建立 Delay Review：原因、V1 影響、Post-V1 可能、scope creep、低價值過度優化、拆分與模型選擇。
