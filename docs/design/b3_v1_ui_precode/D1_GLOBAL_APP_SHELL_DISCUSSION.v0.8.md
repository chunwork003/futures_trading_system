# B3 V1 — D1 Global App Shell / Investment Overview, visual design discussion v0.8

- **Date**: 2026-10-19 (Asia/Taipei).
- **Design status**: `PROPOSAL / OWNER_FEEDBACK_PENDING`, not Human Design Acceptance, not Coding Authorization.
- **Fixed B3 source pin**: `9643bfc93a1631154be877536a1c91fc58df84be`.
- **Design branch**: `design/b3-v1-ui-precode-review-20261017`.
- **Previous record**: `D1_GLOBAL_APP_SHELL_DISCUSSION.v0.7.md`.
- **Standalone interactive visual review source**: `docs/design/b3_v1_ui_precode/prototypes/B3_V1_D1_AppShell_Interactive_v0_8.html`. This HTML is design-only with synthetic mock values and no B3 API / broker connection.
- **Human screenshot references**: seven uploaded screenshots dated 2026-10-19, illustrating crowded edit controls, icon rail/flyout navigation, fixed-height data cards, FinLab left category rail, individual-stock/strategy dropdowns, workflow scheduling and research reports. Referenced for UX patterns, not copied as third-party assets.
- **Official UI identity retained**: UI01 Dashboard (`/dashboard`), UI08 Portfolio (`/portfolio`), UI02 Chart (`/chart`), UI03 Market (`/market`), UI04 Strategy Builder, UI05 Research, UI06 Comparison, UI09 Orders, UI11 Risk, UI16 Automation/Progress, UI17 Settings. No official `UI20` is created.
- **Status terms**: `SOURCE_CONFIRMED / PROPOSAL / UNVERIFIED / OWNER_DECISION_REQUIRED / FORMAL_REVIEW_REQUIRED` are discussion classifications, not formal machine governance statuses.

## Owner feedback / disposition by numbered request

| Ref | Owner input and screenshot finding | Proposed v0.8 response | Design / contract status |
|---|---|---|---|
| D1-08-01 | Applying warm-brown palette leaves blue chrome; text should react to light/dark; custom presets +/- | Unify app shell/menu/card/list/selection CSS role tokens, apply harmony to chart and asset series, automatically adapt foreground to background luminance; retain gain/loss/status semantically. UI allows add named preset, apply, delete. No automatic WCAG audit of arbitrary user colors yet | PROPOSAL. Visual semantics must not suppress warnings. Contrast/gain-loss regression pending |
| D1-08-02 | '面板設定' renamed '面板', layout edit, add/move/size controls belong under 設定 rather than always-visible top row | Hamburger now opens Settings hub, with 面板 (theme/font/display), 工作台／快捷, 啟動與多視窗, 更新與排程. Top editing toolbar removed. Module +/-/edit/remove appear only in edit mode from Settings; read-only inspect/zoom/data pager remain | PROPOSAL. Official UI17 Settings page retained separately |
| D1-08-03 | Consider multiple displays, browser pages and accounts, identify architectural changes | Demo 'new window' action only. Browser multi-window physically possible; design for per-window pinned Environment/Account/Portfolio/Scope, new-tab vs restore modes, re-auth/permission/snapshot boundaries. Same cookie may share login, separate identities may require separate browser profiles/session policy. **Frontend-only context pin is not account authority** | UNVERIFIED runtime; FORMAL_REVIEW_REQUIRED: MA01/Auth N/AuthZ, MA10-U01/U06, UI01/UI08, UI09/UI11 and persistence |
| D1-08-04 | Fixed module size/height irrespective of data volume; overflow via pages | Cards use fixed 12-column span and exact height in prototype; content scrolls inside and assets/holdings have internal row pagination (3 and 4 items respectively). Data switching never expands the outer card | PROPOSAL. Real Snapshot cursor/pagination contract must be checked |
| D1-08-05 | Explain 'every widget follows current portfolio' | Example: main portfolio 1 -> 2 automatically rebinds summary/capital/strategy/chart/cards to portfolio 2; cards with `📌` keep own selected portfolio 1 with explicit label; News independent. Option between Follow Main and Independent in Settings. No cross-account mixing or authoritative aggregation | PROPOSAL. Source/cut/permission context semantics review needed |
| D1-08-06 | Default launch = portfolio overview; configurable three startup modes | Settings Startup: (1) fixed UI01 homepage default; (2) chosen page set via UI ID checkboxes, count equals checked set, (3) restore last workspace. Exported as candidate JSON, **not durable browser/server restore**; existing last layout implementation absent | OWNER preference largely decided; actual persistence UNVERIFIED / FORMAL_REVIEW_REQUIRED for server |
| D1-08-07 | Accept recommendation for account/environment switching | Context badges always visible; on change server must rerun permission, rebind resource scope, reset unsafe draft, retain unknown order receipt query; user interface cannot grant authority | SOURCE_CONFIRMED safety principle. Multi-window design FORMAL_REVIEW_REQUIRED |
| D1-08-08 | Accept metric/capital definitions; currency and units may be muted/optional | Capital, equity, unrealized/realized PnL, cash available, budget, strategy and total returns must each have producer, denominator, valuation timing/currency/FX, coverage/source/quality; proposal: subdued default currency/unit on summary, full display option. Mixed-currency/risk/trading contexts cannot hide critical currency | PROPOSAL UI; financial metric DTO source needs bounded verification |
| D1-08-09 | Accept data status/updates; investigate efficient cadence | No real timer/polling in HTML. Proposed visible UI01 portfolio/capital read models ~30–60s if allowed, background/idle reduce; market eligible event push with resnapshot gap recovery; order/risk receipts/event server-only, research jobs event or ~10–30s fallback; news ~5–15min dependent on licensed feed. Manual refresh on uncertain/important state; preserve stale/partial/UNKNOWN. **Not a provider SLA or adopted cadence** | UNVERIFIED; FORMAL_REVIEW_REQUIRED if stream/rate new contract |
| D1-08-10 | Accept layout persistence scope | Preferences candidate hierarchy: B3 default -> user profile -> workspace -> per window/screen layout, with revision/CAS, export/import, reset, no broker secret/local auth, no implicit cross account leak | PROPOSAL; persistence contract FORMAL_REVIEW_REQUIRED |
| D1-08-11 | Global search and module-level function search, shortcut keys later | Top global page/subfeature search; editing a module includes search over same Feature Registry as rail and nav. Shortcuts, keyboard mapping and accessible patterns remain later design reviews; avoid shortcut keys executing trades | PROPOSAL |
| D1-08-12 | FinLab-like left category icon rail with light flyout selected shortcuts, default collapsed; allow full open in Settings | Narrow category icon rail defaults; clicking category displays themed light/different panel with **only selected shortcuts for that category**; option to use fully expanded style, modal edit remains behind selected category; no copy of third-party branding/assets | PROPOSAL |
| D1-08-13 | Market menu individual stock subfeatures and extra Tools; Strategy Tools in Lab | Market: company overview, sector, chart, compare, watchlist candidates mapped to UI03/UI02. Tools: display-only percent calculator, chart indicators, risk preview, research scheduling proposal. Lab includes Strategy Builder UI04, Research UI05, Comparison UI06, Research Scheduling candidate. Missing operations cannot be treated as implemented | PROPOSAL + UNVERIFIED for sector/stock comparison and tools |
| D1-08-14 | Scheduling and research workflows desirable | Distinguish `UI05 Research runs` (existing run/query/cancel operations) from **new time-triggered research scheduler** (NOT source-verified) and `UI16 Automation/Progress` governance/workflow. Display proposed workflow: exact strategy rev + dataset snapshot + schedule/time zone -> authorized scheduler -> operation receipt + run -> result/notification. No browser-based unattended job or broker authority. | FORMAL_REVIEW_REQUIRED: schedule contract, service runner, entitlement, quota, failure/reentry, operation receipts, immutable snapshot, audit |

## Prototype review features (design-only)

- Header: portfolio / market / Lab / News (news candidate) / Tools / More; search over 19 official UI pages plus selected indexed subfeatures.
- Compact icon rail and themed selected-shortcut flyout; default closed, full expansion in Settings.
- Current-portfolio default dashboard: UI01 read-only summary linked to UI08 detail, with fixed-height editable display components.
- Static demo portfolio 1–4 switch; data pager; main-follow or independent card context; pin/unpin cards; mixed views labelled by portfolio.
- Theme editor: wheel, harmony, full palette, manual colors, custom named palette +/−, readable color contrast adapts; separate gain/loss and data-quality semantics; font families/sizes by category; unit label prominence setting.
- Settings layout edit mode, module add/edit/resize/reorder/remove, JSON export, full screen; normal mode hides edit chrome.
- Startup selection and refresh policy are **interactive design inputs only**; not runtime and not device synchronization.
- Market stock tool and strategy tool navigation displays a candidate route/status; calculator only computes math, no investment or broker authority.

## Test evidence and known limits

- Local browser: Chromium Playwright via `set_content`; tests on 1500x920 canvas.
- Observations: 8 modules, edit controls hidden by default; rail flyout opens/closes, global search returns matching features; Settings cancel restores side mode; edit mode exposes 32 per-card controls and can exit; startup custom page list provides 9 selectable sample official pages; warm colors update page RGB(27,21,15), module header RGB(74,54,34), selected rail RGB(246,189,106); top switch to portfolio 2 changes overview KPI `NT$ 2.59M`; individually moving portfolio card automatically pins; asset page flip retains card height **385px → 385px**; UNKNOWN hides total summary `—`; browser script errors **none**.
- Fixed card design not yet tested for every breakpoint, long real-string / i18n overflow, WCAG contrast of every color combination, content pagination against a real cursor.
- Does not establish actual B3 API implementation, Capital/Risk/Order state or Authority, broker connectivity, active market data provider, non-mock pagination/snapshot, schedule execution, multiple account permission, cross-window tab persistence or custom themes synchronized between devices.
- Third-party UI screenshots used as inspiration; no direct duplication of proprietary UI code/assets.

## Decision register and formal review gates

- `D1-D01` — Homepage: UI01 investment overview as startup **Owner explicitly requested**; treat as design direction, not Human final D1 acceptance.
- `D1-D02` — Default shortcut view: icon rail + flyout selected shortcuts; switchable to expanded rail, **Owner direction received**.
- `D1-D03` — Default portfolio synchronization: `follow main`, allow individual `📌` pin; **OWNER_DECISION_REQUIRED after preview**. Cross-account mix prohibited.
- `D1-D04` — Currency/unit summaries muted by default while preserving meaningful units in detail and mandatory action contexts; Owner direction received; exact display style yet to review.
- `D1-D05` — Palette scheme and contrast for user-generated swatches need a separate visual acceptance and accessibility test; owner may provide screenshots.
- `D1-D06` — Fixed widget height/pagination and multi-data switching require real cursor/snapshot/cut contract at UI01/UI08; **FORMAL_REVIEW_REQUIRED if new DTO semantics**.
- `D1-D07` — Per-window selected Account/Environment/Portfolio and three startup modes: implementation qualification and Security/Authority review mandatory.
- `D1-D08` — Planned Research Scheduler, Finance Tools and Market individual stock comparison: verify against accepted UI/API Producer first; no new official UI identity or unconditional schedule/coding authority.
- `D1-D09` — Define portfolio KPI's basis (PnL numerator/denominator, cash equity vs available balance, FX, return sampling), update freshness cut and sources before exact Coding handoff.
- `D1-D10` — Keep D1 open until Human explicitly states no further changes. Final Coding handoff must consolidate this version with all earlier D1 records and full UI01..UI19/MA10-U01..U06/DTO/API/64-finding crosswalk.

**No product coding, no repository runtime modification, no official B3 Architecture amendment, no WO/Grant and no Human Design Acceptance asserted by this document.**
