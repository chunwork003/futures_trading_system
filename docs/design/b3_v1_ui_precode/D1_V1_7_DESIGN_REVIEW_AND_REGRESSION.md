# B3 V1 — D1 v1.7 Full Dashboard / Workspace Design Review

**Recorded:** 2026-10-21 (Asia/Taipei)  
**Status:** `PROPOSAL / HUMAN_REVIEW_PENDING` — informal design labels only, **not** formal machine states, not Human Design Acceptance, not Coding Authorization.  
**B3 Accepted Source Pin:** `9643bfc93a1631154be877536a1c91fc58df84be`.  
**Branch:** `design/b3-v1-ui-precode-review-20261017` (isolated prototype/design-only).  
**Input:** Owner feedback, five annotated screenshots (2026-10-21), prior D1 v0.2–v1.6 records, KEEP-01–15 and D1-R14-01–10 regression registers.  
**Prototype:** `prototypes/B3_V1_D1_FullDashboard_v1_7_REVIEW_CANDIDATE.html` (synthetic financial data and news; no real B3 API or broker call).  
**Repeatable Browser Test:** `qa/B3_D1_v1_7_REGRESSION_TEST.py`, report `qa/B3_D1_v1_7_REGRESSION_REPORT.json`.

## Owner issue → design change / verification matrix

| ID | Owner correction | Candidate v1.7 response | Result / boundary |
|---|---|---|---|
| D1-17-01 | Left flyout **75% transparency**; shortcut modal left-side controls should wrap | CSS uses 25% background color + backdrop blur (75% nominal transparent); controls arranged in flex/grid minmax with wrapping and long-label break; flyout remains a selected-shortcut list with no editor title | Targeted functional & geometry checks, **visual contrast not formally WCAG qualified** |
| D1-17-02 | Two direct dropdowns `類別 / 圖案`, icon import final item invokes native chooser | Direct category+symbol select in left shortcut editor; glyph choices + last `＋匯入`; native PNG/WebP picker (<=250KB) without intermediary modal; per-category choice staged until Save | **Prototype PASS** for select, collapsed categories, DOM; imported file decode/CSP/authorization remains **UNVERIFIED** |
| D1-17-03 | Shortcut feature groups show `＋/－`, default collapsed | `d17-catbtn` per category, default collapsed, expand/collapse with aria-expanded; keeps same Feature Registry / UI IDs | **Prototype PASS** |
| D1-17-04 | Adobe-like theme wheel + five swatches, default themes, custom/save/remove and manual color controls | Preserves original color wheel/individual colors and adds five-swatch strip, predefined 深藍/暖棕/翡翠, custom named palettes, HEX editing and preview; separated status/gain-loss safety colors | **PARTIAL**: visual preview and UI operation, **not** complete design token coverage, contrast qualification, font settings or cross-session persistence |
| D1-17-05 | `工作台版型` immediately open editor; JSON export inside; no full-screen | Settings `工作台版型` now opens stand-alone **工作區編輯**. Page selector and export JSON embedded in editor; independent draft with Save/Cancel. | **Prototype PASS** for direct access, JSON control and view tabs. Fully persisted multi-page workspace API remains **UNVERIFIED** |
| D1-17-06 | All pages' layouts plus selected assets, categorized module palette, combined Module Editing with query/edit/copy/new/delete | Workspace page selector offers All+P1–P5 and UI02–19 planning placeholders; Catalog still grouped; module management tab supports search, copy, rename/inspect, new and guarded delete (warn if used). | **PARTIAL**: actual editing of slot geometry/complete live preview in management mode, deletion replacement picker, and all 19 page-specific design profiles **not fully implemented**; never imply each page exists in running B3 |
| D1-17-07 | Startup page chooser must have **Add** pages | Custom startup add button, chip list/remove, full UI01–19 candidates; doesn't launch real windows | **Prototype PASS** for candidate UI; runtime multi-account/window isolation **FORMAL_REVIEW_REQUIRED** |
| D1-17-08 | **All portfolios overview** must differ from P1..P5 and support renaming | Distinct `'all'` and `'p1'... 'p5'` workbench page keys. All overview shows five mock portfolio comparison cards, cross-portfolio capital conceptual layout; individual page uses original default strategy chart and single-portfolio modules. Rename action for P1..P5 (design-only local state). | **Prototype PASS** for switch and 24 strategy bars on P1. Cross-portfolio sum is **synthetic nonauthoritative** and may never override true account/currency/cut integrity. |
| D1-17-09 | Financial chart per-period strategy changes (amount/%), allocation labels around plot | On individual page preserves six periods × four strategy bar series + total line; hover shows per-strategy current amount and difference from prior period (amount/%). Allocation shows five classification labels with amounts and percentages next to donut. All overview has per-portfolio six-period small comparison series and percentage indicator. | **PARTIAL**: real aggregation semantics (market value vs equity, strategy category, cash, FX, and authorization) unresolved; five cards' bars are synthetic visual samples. |
| D1-17-10 | Include independent Visual UI Reviewer, no unilateral contract/function modification | Test against existing D1 visual reviewer and KEEP ledger; responsive corrections at 1100px allocation and 780px chart height; all source and authority changes remain formally gated | **Prototype PASS bounded; formal reviewer NOT RUN** |

## Browser evidence and visual reviewer findings

- Playwright Chromium run from `B3_D1_v1_7_REGRESSION_TEST.py` on standalone file rendered via `page.set_content`, **not B3 API integration**.
- **11/11 targeted cases PASS** in last tested bytes (artifact/report SHA must be compared). These include 1510/1100/780px, one 125% and one 150% font case, eight cards, no horizontal document or card overflow in the tested scenarios, no page JS errors, plus features described above.
- Original first audit found an allocation overflow at 1100px and both trend/allocation overflow at 780px; responsive template corrections applied and audit rerun. Adding six-period per-portfolio microbars later exposed another 780px overflow; corrected with larger mobile trend standard template height (not record-count-driven).
- Visual reviewer **P1**: all-overview five comparison cards visually needed richer per-period data. Added time-point microbars with hover current total (synthetic); still needs explicit historical metric definitions and detailed period change tooltip in formal chart spec.
- Visual reviewer **P1**: arbitrary large fonts, very long Chinese names, high-contrast theme and 1920/2560px monitor patterns not exhaustively tested. 
- Visual reviewer **P1**: Theme swatches and imported SVG security; only PNG/WebP accepted. Custom color harmony / contrast and real storage remain missing.
- **P0 source safety**: `UNKNOWN` must never assert cash values, financial performance or exposure as real. All-overview synthetic amount/percent is masked for UNKNOWN in this candidate; remaining non-authoritative labels must remain explicitly DEMO.

## B3 contract boundary / design choices retained

- Official UI Identity remains **UI01...UI19**. UI01 Dashboard is an investment overview, UI08 Portfolio has its own portfolio/detail ownership; no UI20.
- Design approved by Owner: **one exact source-bound data subject per module**, multiple displays. Cross-subject or cross-cut authoritative merges require explicit approved producer contracts, never frontend summation.
- React → ASP.NET BFF → Python API → core/persistence, formal permission/risk/capital/order authority and LAB/PAPER/LIVE isolation remain unaffected by the HTML concept.
- New layout saving / cross-device preferences, multi-window/account pinning, multi-portfolio authoritative aggregation, news authorization, scheduler service, updated DTO or exact cash/equity return calculations require source verification and potentially **FORMAL_REVIEW_REQUIRED**. No mock is actual provider evidence.
- Standalone HTML is a **discussion tool**: changes remain in memory until exported, and Git commit of this prototype is *not* user preference persistence.

## Follow-up D1 gate and unresolved requirements

1. **Cross-portfolio all-view KPI semantics**: Owner to examine design; exact financial source/currency/cut and whether the comparison should be return-only vs aggregate value are **UNVERIFIED**.
2. Full module library edit workflow: replace used module via selected replacement template, edit slots rather than only rename, CAS/revision and undo. Candidate only; must not misstate as complete.
3. Workspace page templates for UI02–UI19 and independent asset subsection layouts require detailed page design; current page picker is a **navigation/design shell**, not 19 rendered pages.
4. Persistent named themes, full color token coverage, WCAG color/focus/a11y, keyboard shortcuts and icon import validation remain to review.
5. D1-R14-01..10 and KEEP-01..15 **not collectively closed**. Do not label D1 Human accepted / formal review PASS / authorized coding.

**Next action:** Owner visually checks v1.7 complete HTML, especially the separation of All overview and P1–P5 and module management. Only after feedback update this register and cohesive HTML, then re-run the same checks and additional risks. **Visual UI Reviewer has advisory design scope only; cannot alter B3 functions/architecture.**