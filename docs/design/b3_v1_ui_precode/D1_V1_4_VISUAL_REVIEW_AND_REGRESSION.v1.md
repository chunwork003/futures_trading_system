# B3 D1 v1.4 Candidate — Functional Regression + Visual UI Reviewer Results

**Date:** 2026-10-20 (Asia/Taipei). **Review result:** `CORRECTION_IN_PROGRESS`, **not PASS or Human accepted**. These are informal design labels, not machine governance states.  
**Source baseline:** `9643bfc93a1631154be877536a1c91fc58df84be`. Official UI01–UI19, MA10/PK11 unchanged.  
**Prototype:** `docs/design/b3_v1_ui_precode/prototypes/B3_V1_D1_FullDashboard_v1_4_CANDIDATE.html` (standalone mock HTML, no market/broker/server calls).  
**Checks:** `D1_V1_4_CORRECTION_REGISTER_AND_ACCEPTANCE_CHECKLIST.md`; `D1_V1_4_VISUAL_UI_REVIEW_PROTOCOL.md`.  
**Human choice:** **A — one exact source-bound subject per module, multiple different presentations**. This is the premise of this prototype.

## Overall status

The prototype keeps the **eight core homepage cards** and implements a new coordinate-based Workbench Editor plus a unified '模組' editor. It is an *intermediate coherent design candidate*, not a claim that all prior D1 v1.3 polish and functions have been preserved. **Several capabilities are explicitly incomplete.** The visual design role has identified a measurable issue and prevented a false PASS claim.

### D1-R14-01–10 regression matrix

| Case | Result | Evidence / limitation |
|---|---|---|
| D1-R14-01 all standard modules use template, no clipped finance data | **PARTIAL** | At 1500/1100/780 px, 8 default cards have zero inner/body scroll overflow *after fixing trend by 49px*. At 150% font, News card overflows by **57px** and requires responsive variant. Formal uniform module registry and arbitrary labels not verified. |
| D1-R14-02 asset All/Stocks and 1/6/8 records fixed | **PARTIAL** | Browser: All→Stocks maintained 6 slots; UNKNOWN masks overall equity. Complete full tab/cut/portfolio matrix not tested. |
| D1-R14-03 shortcut flyout correct | **PARTIAL** | Rail click opens/closes translucent overlay and gear opens separate quick editor; no animation collision in tested run. Keyboard focus, all modes and long labels not yet audited. |
| D1-R14-04 icon add/import | **PARTIAL** | 24 pictogram options and ＋ PNG/WebP selection (<=250KB, MIME validation). Imported icon image decode/preview, persistence, SVG sanitizer and file security tests **not completed**; SVG intentionally disallowed. |
| D1-R14-05 coordinate-based workbench gaps | **PASS — targeted concept** | 12-column `(x,y,w,h)` coordinate occupancy; 36 empty gap targets in initial 12×8 editor example; plus in empty cell, drag existing to free cell; Cancel returns homepage unchanged 8 cards; Save adds 9th card and returns settings. Real collision edge cases/multiple drop targets still need tests. |
| D1-R14-06 color wheel alignment, hex edit | **PARTIAL** | Unified CSS role-color editor, manual `#RRGGBB` and color input; theme preset updates accent. Full Adobe-like wheel and palette harmony, every token coverage/automatic light-dark contrast, Cancel theme rollback and hover-only swatch labels **incomplete**. |
| D1-R14-07 NxM modular slots unlimited four cap | **PASS — targeted concept** | 6×2 editor accepts 7 separately added 1×1 slots; non-overlapping placement, slot resize validation, drag to empty slot; no fixed 4-block code path. Save returns parent Settings. Full split/merge/multi-cell span coverage tests pending. |
| D1-R14-08 unified module editor, no S–XL, same subject | **PARTIAL** | Single '模組' entry, `subject→NxM→+→data visualization`, initial right inspector absent until slot added, no S–XL, auto-generated module name. **Field choice not yet durably bound per slot**, history API not verified; custom module display still a placeholder. |
| D1-R14-09 Workbench vs single-module roles; nested Save/Cancel | **PASS — targeted concept** | Independent Settings→Workbench or Settings→Module. Workbench modifies card instances; Module internal slots. Save/Cancel returns to originating Settings tab. Browser check passed. |
| D1-R14-10 full source-wide regression | **NOT YET PASS** | 5 targeted browser scenarios pass; 1500/1100/780 px geometry audit; not 19 UI workflow or 64 Finding Crosswalk; no 125/150% full contrast accessibility signoff, long strings, multi-account/session, genuine DTO or browser persistence. |

### VISUAL_UI_REVIEWER findings (additional independent design lens)

| Finding | Severity | Evidence | Proposed action |
|---|---|---|---|
| `VUI14-F01` | P0 for final design acceptance | Trend SVG + stack originally exceeded parent by **49px** at 1500/1100/780px, resulting in visually cut content. | Fixed by chart-area two-row layout, SVG and bar-height allocation. Repeated measurements: **zero overflow in 8 cards** at all 3 widths for default font. |
| `VUI14-F02` | P1 | News card at 125% font still overflows 4px; at 150% by 57px. | Define font-scale responsive template / shorten optional news excerpt or increase *template* standard height in zoom profile; preserve critical status. Do not hide essential text. |
| `VUI14-F03` | P1 | Cash/money summary, asset panel and chart have different level of visual density. New renderer improved full-width typography but still needs hierarchy consistency. | Normalize currency/return baseline, KPI group layout, 8px spacing and icon scheme. |
| `VUI14-F04` | P1 | Theme preset currently changes accent and role color inputs, not a fully harmonious preset with contrast auto-adjustment. | Complete semantic color token cascade, contrast algorithm, default-safe fallbacks, staged Cancel/Save. |
| `VUI14-F05` | P1 | Blank placeholder asset slots visible when less than 6 records; visually stable but potentially wasteful at one entry. | Add **same-subject** alternative detail panes within a fixed module capacity only if contract supplies data; otherwise neutral reserved slots, never invented values. |
| `VUI14-F06` | P1 | Icon import picker validates MIME/size but does not yet create a persisted preview or integrate across sessions. | Confirm local preview, format policy and permission-safe persistence before adoption. |

### Executed browser checks

- Chromium headless via Playwright, standalone HTML `set_content`, **no B3 production/E2E testing**.
- 5 targeted test groups passed with no uncaught JS exceptions:
  1. 8 homepage cards, six asset slots after All/Stocks switch, UNKNOWN placeholder.
  2. Translucent sidebar popup, independent Quick Editor and icon file input.
  3. Empty grid + add 9th, Cancel rollback, Save applies to main page.
  4. Unified 6×2 Module allows 7 cells and returns to Settings after Save.
  5. Theme accent setting and constant dialog structure.
- DOM overflow audit: `1500px, 1100px, 780px` widths — horizontal document overflow **0px**; card and card-body overflow **0px** across 8 original modules at default typography.
- Font-zoom simulation (increase body text): `100%` no overflow, `125%` News +4px, `150%` News +57px. This remains an open issue.
- Original prototype JS initially contained a syntax-brace defect; fixed and reran tests. Original trend geometry failed; fixed and reran. The final published candidate is the retested version, not the initial failed bytes.

## Visual benchmark source and proposed guidance

- TradingView public saved-layout and split-view UX: https://www.tradingview.com/support/solutions/43000746975-tradingview-layouts-a-quick-guide/ and https://www.tradingview.com/support/solutions/43000753069-simple-steps-to-split-view-mode/ ; draw on independent workspaces and tool clarity only, not their broker authority or private data schema.
- IBM Carbon design grid (8px mini-unit): https://www.carbondesignsystem.com/building-blocks/foundations/2x-grid/overview ; data table usage and icon focus: https://www.carbondesignsystem.com/building-blocks/core/components/data-table/guidelines .

## Governance and next action

- **No claim that D1-R14-01–10 or VUI-01–10 all pass.** D1 v1.4 remains `PROPOSAL / CORRECTION_IN_PROGRESS` until remaining P0/P1 items are rectified and Owner explicitly accepts.
- Design-only Git branch, without authority to change accepted UI01/08 IDs, DTO, LAB/PAPER/LIVE permission, capital/risk/order semantics, API, master, Work Order or Coding Grant.
- Next bounded improvements: font 125/150% responsive profile (VUI14-F02); icon image local preview + cancel semantics (D1-R14-04); color role/contrast and rollback (D1-R14-06); complete per-slot field binding (D1-R14-08); verify true empty-cell drag and all preset modules against DPI/pagination combinations.
