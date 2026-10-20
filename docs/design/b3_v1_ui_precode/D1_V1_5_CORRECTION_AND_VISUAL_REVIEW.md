# B3 V1 / D1 v1.5 — Functional Regression and Visual Design Review

**Date:** 2026-10-21 (Asia/Taipei).  
**Design status:** `PRECODE_DESIGN_CANDIDATE / HUMAN_FEEDBACK_PENDING` (informal design-only labels; not official machine states or accepted architecture).  
**Preserved accepted source:** `9643bfc93a1631154be877536a1c91fc58df84be`.  
**Git design branch:** `design/b3-v1-ui-precode-review-20261017`.  
**Prototype:** `docs/design/b3_v1_ui_precode/prototypes/B3_V1_D1_FullDashboard_v1_5_CANDIDATE.html`.  
**Prototype SHA256 (local UTF-8 bytes):** `85372a656ce7c14676e80d8898a665440829654414573cc331150b1567dd9bde`. Verify published Git blob separately.  
**Human source:** annotated v1.4 screenshots and nine numbered owner corrections, 2026-10-20.  
**Mode:** standalone HTML/CSS/JS *design prototype* using completely synthetic market/capital data; no B3 frontend product implementation, no Broker/API/Server I/O, no WO/Grant, and no formal acceptance.

## Authority of review roles — correction of prior role boundary

- `FUNCTIONAL_UI_REVIEWER`: tests behavior, regressions, navigation identity, workflow continuity, Save/Cancel/Esc and expected interactions. Does **not** approve capital/risk/API semantics.
- `VISUAL_UI_REVIEWER`: **advisory only** for grid alignment, card dimension, typography, palettes, user-perceived hierarchy, chart visual legibility and accessibility. **Cannot delete/add product features or change existing function ownership, UI Identity, schema/API, business logic, authority, account/environment, or scheduling**. A visual finding requiring such a change becomes an owner proposal and source-bound formal-review referral, never an independent decision.
- `SOURCE/CONTRACT REVIEW`: UI01–UI19, B3 MA10/PK11, DTO, Source/Cut/Quality, permission and lifecycle are separate from visual approval; absent evidence remains UNVERIFIED.

## Nine owner-requested changes, actual findings and disposition

| ID | Request | v1.5 design implementation | Status |
|---|---|---|---|
| D1-15-01 | 50% translucent popups, no flyout heading; pointer leaves without clicking, hide after delay | Rail flyout 50% alpha with blur, header hidden, tooltip on rail-icon hover; auto closes ~1.9s after pointer leaves rail/flyout, without mouse click. Main dialog background 50% alpha + backdrop blur; menu 50% alpha | **TARGETED_BROWSER_PASS**; full contrast and keyboard-focus audit not complete |
| D1-15-02 | Undo regression to left gear; imported-icon + should be final picker option | Independent left-bottom shortcut modal; 24 built-in pictograms, final 25th `＋` opens PNG/WebP file chooser, category selector and preview. Only explicit Save updates the rail. No backend upload or SVG support | **TARGETED_BROWSER_PASS**; import exploit/invalid-signature tests not complete |
| D1-15-03 | Top 6 nav menus inactive | Top Portfolio/Market/Lab/Tools/Trading/News buttons now actually open dropdowns. Known routes keep official UIxx IDs; click updates design-only hash and shows descriptive feedback; candidate links clearly marked | **TARGETED_BROWSER_PASS**; other real pages not implemented |
| D1-15-04 | Financial modules too sparse; combination chart needs strategy value columns per period and hovered total/each strategy prior amount AND % change | Overview/capital/strategy/news information density unified; portfolio chart shows line + **seven timepoint stacked strategy columns**, each split into trend/yield/rates/other; hover shows period total, delta and %, each strategy value, delta and %. First period explicitly marks prior unavailable. Per-period labels change with selected time unit, all values remain **synthetic**. | **TARGETED_BROWSER_PASS**; metric formula/real producer remains UNVERIFIED |
| D1-15-05 | Palette lost color wheel, codes hidden until HEX/RGB edit | Global Settings `面板／配色` restores clickable color wheel, role-color chips, preset deep/warm/jade, separate HEX and RGB tabs with typed input; field colors preview; Cancel restores prior colors. Codes not printed under idle swatches. | **TARGETED_BROWSER_PASS**; full WCAG arbitrary-role contrast and wheel drag kinetics not complete |
| D1-15-06 | Drag whole module footprint translucently and snap only on mouse release; catalog category then feature | Workbench editor has category → feature selectors; uses 12-column actual occupancy, drag image 50% alpha, whole-card ghost/validity preview at hovered (x,y) with size (w,h), drop to commit location on mouse release; empty cells show +. Invalid collisions rejected. | **TARGETED_BROWSER_PASS**: dragged capital 3×1 from (4,1) to (4,6). Full multi-cell drag and collision matrix not yet complete |
| D1-15-07 | Module creator needs numbered slots and immediate preview | Every created slot gains #01/#02 etc, displays a synthetic amount/chart-type preview, right inspector shows field/type/current data subject immediately after selection | **TARGETED_BROWSER_PASS**; typed DTO field eligibility and true API binding UNVERIFIED |
| D1-15-08 | Startup/multi-window settings were broken | Restored three startup modes (default/custom/last workspace), custom UI page checkboxes, 1–4 window count and visual window-plan preview. Settings form state staged: Cancel restores mode/page selection, Save commits prototype-only preferences; account/environment isolation is documented as pending formal authority review | **TARGETED_BROWSER_PASS** for option change and Cancel, **UNVERIFIED** actual cross-browser/window/session persistence |
| D1-15-09 | Visual role only aesthetics/measure, not feature or architecture changes | Explicit governance restrictions and separate reviewer decision matrix in this document. No official B3 identity/API/Capital/Order/Risk changes | **RECORDED**; independent B3 architecture acceptance not asserted |

## Executed reproducible local browser checks (not official E2E)

- Environment: installed Chromium at `/usr/bin/chromium`; Playwright Python `set_content` of one standalone HTML; no network/API requests.
- Initial DOM: **8 default cards**, zero uncaught JS page errors.
- Portfolio/Market navigation: Market dropdown opens with **4** entries and closes when clicked again.
- Rail: flyout opacity **0.5**, hides automatically after pointer leaves for ~2200ms without click. Left-bottom shortcut picker has **24 icon choices + final Import tile**.
- Palette: restored color wheel and **8 role chips**. Warm preset changes `--accent` from `#56b7fa` to `#d69b5c`; Cancel restores `#56b7fa`.
- Startup: select custom and UI02, Cancel, reopen: mode returns to **default**. Startup multiwindow preview is interactive but does not open actual multi-account sessions.
- Workbench: **36** empty cells initially; drag a **3×1** Capital module from grid row 1 to row 6, full-area snapping updates its `grid-row:6/span 1`; Cancel returns to prior homepage.
- Module editor: add first empty slot, numbered `#01` and populated demo inspector appear; Cancel returns to source Settings.
- Chart: hover strategy timepoint shows total and **four strategies**, each prior change amount/%, with first-point prior reported unavailable.
- Layout audit: **1920, 1500, 1100, 780px × font factors 100%, 125%, 150%** = **12 cases**. `documentElement.scrollWidth - innerWidth = 0`; no `card-body.scrollHeight - clientHeight > 2px` among original 8 cards, for all 12 cases. **This checks overflow, not full WCAG or all text collisions.**
- Screenshots generated as conversation artifacts: `B3_V1_D1_v1_5_HOME.png`, `RAIL.png`, `QUICK.png`, `PALETTE.png`, `WORKBENCH_AFTER.png`, `MODULE.png`, `1100.png`.
- Evidence scripts in session artifact working environment: `test_d1_v15.py`, `test_d1_v15_extra.py`, `audit_d1_v15.py`. Generated as design-review QA, not committed as product code.

## Outstanding gates, not silently PASS

1. **D1-R14 full acceptance not yet passed**: no exhaustive all-card 1/6/8 records × every asset class × zoom/palette permutation. B3 actual source/API/DTO, producer and dataset snapshot not bound.
2. Custom icon import currently validates browser-reported type and size, but not binary signatures/decoding adversarial cases; no official asset persistence/API or SVG sanitizer. Requires security review if production import is requested.
3. Current palette exposes swatch colors and RGB/HEX entry but requires further WCAG contrast checks for all custom combinations. Visual role cannot suppress mandatory LAB/PAPER/LIVE, UNKNOWN/PARTIAL/STALE and permission alerts.
4. Multi-window is a **settings and workspace-plan prototype** only; exact browser session separation, same-account vs different-account policy, state pin and save revisions require source-bound Architecture/Authority review.
5. TradingView-like navigation is a **functional design link map**, not a deployed page router or backend availability claim.
6. Strategy bars and period sampling are mock compositions; portfolio aggregation (capital, asset/strategy return, currency/valuation) must be contract verified. Missing historical series must remain UNVERIFIED, never treated as zero.
7. Nested module NxM and drag occupancy cover targeted positive scenarios, not proof of all invalid collisions, keyboard DnD, undo/redo, 19-page consistency or 64 findings.
8. Visual design review is a process advisory, **does not authorize product Coding**. Human D1 review remains open.

## Next D1 review sequence

1. Owner reviews this complete v1.5 home + Workbench + Module + Palette + Nav without further architectural refactoring.
2. Address remaining visual failures and complete `D1-R14-01..10` / `VUI-01..10` exhaustive cases with evidence. New state/contract obligations escalated separately; unrelated pages not blocked.
3. Continue D1 until owner explicitly says no additional adjustment; then compose complete `B3_V1_UI_UX_DESIGN_REVIEW_PACKAGE` across all UI01..UI19 and six MA10 units before any WO/Grant.

**Status:** `PROPOSAL / AWAITING_HUMAN_VISUAL_REVIEW`. No implementation or design acceptance asserted.
