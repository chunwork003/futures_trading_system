# B3 D1 v1.4 — Frontend Visual Design Reviewer (美編 UI 審核) Protocol

**Date** 2026-10-20 (Asia/Taipei). **Stage** Pre-coding design candidate only; not Human Design Acceptance / WO / PK11 Coding Authorization. Source baseline `9643bfc93a1631154be877536a1c91fc58df84be`.

## Reviewer independence and inputs
Add a distinct `VISUAL_UI_REVIEWER` lens to every D1 (and subsequently UI01–UI19) design revision. Inputs: rendered screenshots at defined breakpoints and font zoom, browser DOM geometry, Human annotated screenshots, design templates / source constraints, regression outcomes. Visual reviewer is an *advisory design role* and cannot make formal Architecture/Authority/Coding decisions or assert Independent Reviewer status.

## Industry patterns, consciously adapted
- TradingView published guide describes saved chart layouts, symbol/interval/chart controls, left/right/bottom panels and split view. Adopt **workspace clarity, layout persistence as a candidate, separation of tools from main canvas**; do not copy TradingView branded assets, code, broker / order authority or undocumented functionality.
  - https://www.tradingview.com/support/solutions/43000746975-tradingview-layouts-a-quick-guide/
  - https://www.tradingview.com/support/solutions/43000753069-simple-steps-to-split-view-mode/
- IBM Carbon 2x Grid foundations recommend an 8px mini unit and consistent type/layout/icon rhythm. Adopt **8px spacing system** (4px micro spacing as necessary), shared row-height, predictable scan path.
  - https://www.carbondesignsystem.com/building-blocks/foundations/2x-grid/overview
- Carbon table design recommends stable typography, table alignment, and clear hover/selected/focus states. Financial data should have units / provenance without clutter; right-align numeric columns and use tabular numbers.
  - https://www.carbondesignsystem.com/building-blocks/core/components/data-table/guidelines

## VUI-GATE checklist, mandatory for each candidate

| ID | Visual acceptance category | Proposed measurable criteria | Failure examples |
|---|---|---|---|
| VUI-01 | Hierarchy | Page title > module title > KPI > explanatory secondary text; design/debug text not default; safety labels not hidable | Tiny critical state; oversized debug copy |
| VUI-02 | Alignment | Grid positions aligned within 8px rhythm; same sized cards identical outer bounds & header/footer locations; numbers tabular/right align | Column headers shift; content jumps on tabs |
| VUI-03 | Density | Default S/M/L single-subject templates fill their intended area with genuinely supported metrics/charts; no artificial fillers or fabricated financial numbers | Tiny center chart, 60% blank with clipping elsewhere |
| VUI-04 | Responsive | Test 1440, 1920, narrow 1100 px and 125/150% font; no overlap, text truncation or inner scroll; responsive content templates may change at breakpoints, not based on row count | Cash module cut off; asset tab resizes |
| VUI-05 | Navigation | Rail 44–56px, overlay near trigger, transparent/themed; no canvas reflow or hit target obscured; hover/focus consistent | Flyout overlaps category buttons or pushes chart |
| VUI-06 | Accessibility | Keyboard focus visible, Esc works; information not color-only; numerical signs; contrast audit for custom palette before future implementation | Red/green only; disabled illegible |
| VUI-07 | Chart legibility | Axis scale, units and tooltip understandable; view total & strategy/asset decomposition with source/cut; avoid chartjunk | One generic line with no compare |
| VUI-08 | Settings | Dialog keeps stable dimensions and clear section grouping; footer Save/Cancel reachable; Cancel genuinely rolls back | Settings bounces / closes all modals |
| VUI-09 | Editable grid | Every unoccupied valid cell visible as +/- drop target; snap-to-grid; no overlapping module regions; occupancy verified | Empty space cannot accept a card |
| VUI-10 | Trust | LAB/PAPER/LIVE, account, source quality, UNKNOWN/PARTIAL/STALE identifiable, visually distinct from mock; no UI permission grants | Fake funds shown as authoritative |

## Evaluation method
For each candidate:
1. Visual baseline screenshot for full dashboard, global Settings, left shortcuts, Workbench, combined Module editor, light/dark palettes.
2. Automated DOM box and overflow audit at multiple breakpoints; check no card collision; document measured failures.
3. Scenario interaction check: portfolio 1→2, asset All→Stocks→Bonds, 1/6/8 rows, font scale, unknown, save/cancel/Esc, icon chooser, occupied/empty canvas.
4. Produce **review findings** with Severity P0 (unsafe/unusable) / P1 (layout inconsistency) / P2 (polish), reproduction, recommendation, screenshot, and whether Source/DTO/Authority review is required.
5. Pass criteria: all D1-R14-01...10 and VUI-01...10 must be explicitly PASS or documented accepted exceptions before Owner design acceptance; `NOT_TESTED` never equals PASS.
6. Proposals involving new server persistence, data authority or API change remain `FORMAL_REVIEW_REQUIRED` and cannot be implemented by the design role.

**Status:** Adopted as process for design reviews under this branch. Not an accepted UI layout or formal governance amendment.
