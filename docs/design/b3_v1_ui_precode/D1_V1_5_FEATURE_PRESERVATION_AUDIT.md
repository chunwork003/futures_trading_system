# D1 v1.3 → v1.5 precode design prototype: feature preservation audit

**Status:** `REGRESSION_REVIEW_REQUIRED` — not formal QA or design acceptance. 2026-10-21, design-only branch. 

**Baseline:** Accepted B3 architecture pin `9643bfc93a1631154be877536a1c91fc58df84be` unchanged. **Artifacts compared:** `prototypes/B3_V1_D1_FullDashboard_Integrated_v1_3.html` (prior 200k+ char feature-rich visual prototype) versus `prototypes/B3_V1_D1_FullDashboard_v1_5_IN_PROGRESS.html` (smaller rebuilt proof-of-concept). Automated string occurrence counts are only triage and **do not prove behavioral presence**; verify each UI journey with browser tests.

## Mandatory boundary

The Visual UI Reviewer is limited to layout alignment, typography, contrast, spacing, density, screen responsiveness and recommendations. The Visual UI Reviewer has **no authority to remove, relocate, simplify, rewrite or disable Human-discussed features, API/DTO bindings, official UI01–UI19 identities, permissions, risk/capital/order authority or screen workflows**. Functional changes require explicit Human decision and source-bound review. UX proposal acceptance is not Coding Authorization.

## Carry-forward inventory and remaining regressions

| ID | Capability required from prior D1 discussion | v1.5 finding | Gate before D1 acceptance |
|---|---|---|---|
| KEEP-01 | UI01 investment overview with 8 core module cards and UI08 drilldown boundary | **PRESENT** eight-card mocked baseline; no official live API | Preserve, compare semantics against UI01/08 contracts |
| KEEP-02 | Four portfolio datasets with main-selection follow and optional individual pin | **REGRESSED/NOT DEMONSTRATED**: v1.5 shows fixed portfolio 1 context, main-follow/pin editor not implemented | Re-add observable 4 datasets with permission/source labels, test all card rebinding and exception pins |
| KEEP-03 | Numeric/time-range selectors, trend chart per period and all strategy bars/deltas | **PARTIAL**: 6 sample periods × four strategy bars with hover amount/% now tested, but all period controls display and are not bound to a true interval derivation | Wire selected period to rendered series, recalculate both previous-period delta and %, verify symbol/cut |
| KEEP-04 | Dashboard card asset All/Stocks/Bonds/Futures/etc filters, optional asset visibility selection, sort amount/return and simple/list toggle | **REGRESSED/PARTIAL**: category tab and six-card pager remain; aggregate visibility and sorting mode not all present | Restore classification and sort/view modes, stable template with no body scroll |
| KEEP-05 | Cross-card navigation, indexed 19 UI pages and subfeature search | **PARTIAL**: six primary dropdown groups restored, ID route preview only; global search input visually shown but no search behavior | Restore shared FeatureRegistry/search and visible permission-safe links without inventing runtime |
| KEEP-06 | Left shortcuts chosen by page or subfeature, group, reorder, density/spacing, icon+text/text/icon mode, 20+ icons, import | **REGRESSED/PARTIAL**: five category icons + standalone icon preview picker; no complete subfeature checkbox/selected shortcuts editor like v1.3 | Reconcile complete shortcut editor and all 19 official UI page/subfeature mapping; never use menu redesign to remove it |
| KEEP-07 | Compact translucent rail flyout, auto-close, outside/Esc behavior | **PARTIAL PASS**: 50% background, no title, auto-close after ~1.8 s; keyboard and expanded mode not exhaustively tested | Keyboard/focus, long labels, 1100/780 collision and hit targets |
| KEEP-08 | Workbench with drag/drop, empty cell plus, reuse saved templates, copy/export JSON, rollback | **PARTIAL**: coordinate grid, multi-cell preview/snap, categorized catalog and Cancel/Save; JSON export, collision/undo/keyboard incomplete | Return full workbench experience; 12-column grid, no overlapping IDs, exported revision/scope |
| KEEP-09 | One '模組' editor same exact data subject, NxM regions and per-region field/presentation, live visual previews | **PARTIAL**: NxM editor no 4-region limit, R1C1 indicator and sample; limited rendering kinds, no durable typed B3 sources or full region edit support | Browser tests for >4 slots, field changes, Save/Cancel, draggable span/merge; API whitelist review |
| KEEP-10 | Settings: typography groups, all semantic theme tokens, Adobe-like wheel & precise color, roles, default/user presets, save/cancel | **PARTIAL**: wheel, HEX/RGB, 50% blurred modal, Cancel restores; full font role grouping, custom theme palette presets/contrast coverage lost | Restore grouped font controls and palette preset library and contrast; do not obscure LAB/PAPER/LIVE/UNKNOWN |
| KEEP-11 | Startup modes: default/custom/last, per window/account scopes | **PARTIAL**: conceptual 3 modes and page-selection, Cancel/Esc rollback; no durable save or real multi-window account isolation | Formal source/persistence/session review; avoid claiming runtime ability |
| KEEP-12 | Visual review role independent from feature/architecture reviewer | **PROCESS RULE CONFIRMED**; design branch protocol and this audit explicitly limit scope | Test evidence separately from reviewer advice; require Human confirmation for changing workflows |
| KEEP-13 | Card fullscreen, fullscreen workspace, modal state and icon layout export | **NOT DEMONSTRATED** in v1.5 despite previous versions | Restore design-only fullscreen / export if Human still wants, don't silently delete |
| KEEP-14 | News source/cut/licensing; carousel next/previous by article | **PARTIAL** mock news card with unverified label; article carousel pager may not operate | Verify carousel behavior and source ambiguity; licensed provider before product |
| KEEP-15 | 19 UI contracts / 6 MA10 units / 64 findings handoff | **NOT COMPLETE** (design stage D1) | Maintain crosswalk and formal D9 review gate; no acceptance yet |

## Correction philosophy

1. **Do not call v1.5 a complete replacement for v1.3.** Any smaller reimplementation must either preserve every accepted interactive behavior, or flag it as temporarily missing and prevent closure.
2. Treat source and Human prior accepted design decisions independently of reviewer personal visual preferences. No feature deletion by aesthetics.
3. Do the work as cohesive, tested modules; for each item record exact expected/observed results, screenshots, full-page geometry, source binding and Git commit.
4. Keep the standalone HTML pure mock with no back-end or broker actions. Distinguish SOURCE_CONFIRMED from PROPOSAL and UNVERIFIED; no invented API/scheduler/persistence rights.
5. User expressly requests a continuation instruction if not possible in the same turn: **任務尚未完成，請按「繼續」，接續完成後續任務**.