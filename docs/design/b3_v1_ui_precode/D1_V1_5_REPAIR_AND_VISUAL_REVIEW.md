# B3 V1 / D1 v1.5 — bounded repair checkpoint, UX & visual audit

- **Recorded:** 2026-10-21 (Asia/Taipei)
- **Authority:** design-only source-locked B3 V1 pin `9643bfc93a1631154be877536a1c91fc58df84be`.
- **Prior version:** `prototypes/B3_V1_D1_FullDashboard_v1_4_CANDIDATE.html` and v1.4 correction/visual review documents.
- **Artifact:** `prototypes/B3_V1_D1_FullDashboard_v1_5_IN_PROGRESS.html`.
- **Scope:** standalone HTML visual discussion prototype with synthetic data; no B3 API/Broker I/O, no product React/ASP.NET/Python, no branch merge, no WO/Grant.
- **Status:** `PARTIALLY_CORRECTED / HUMAN_REVIEW_NOT_YET_READY`, not a formal governance status, not D1 closure.
- **Owner decisions carried:** module scope A (same exact resource subject, multiple formats), preserve 19 official UI identities, visual reviewer may **advise only on spacing, sizing, hierarchy, typography, color, contrast, clipping, aesthetics**; it MUST NOT amend existing workflows, features, formal architecture/DTO/API, authority permissions, or implementation scope by itself. Functional changes require explicit Owner request and separate functional/source-bound review.

## Current 9 feedback items — true status and bounded evidence

| No. | Requested correction | Actual state at this checkpoint | Gate |
|---|---|---|---|
| 1 | Left popups 50%-transparent, heading removed, timer close after mouse leave | Flyout uses 0.5 opacity with blur, heading hidden; timer 1.8 seconds after pointer leaves rail/flyout. Shared modal visual has 0.5 background alpha with blur; full keyboard/focus/contrast not verified | TARGETED_PASS / full VUI review PENDING |
| 2 | Repair shortcut editor; `＋匯入` last ICON selection | Each category dropdown now ends with `＋ 匯入自訂 ICON…`, which expands PNG/WebP import. Separate shortcut modal remains and Cancel does not commit. Thorough uploaded image decode/security tests not complete | TARGETED_PASS / safety NOT_TESTED |
| 3 | Top menu unresponsive | All six top categories have clickable dropdown, grounded page ID/route *preview* links. Clicking a link currently shows design-only preview/toast; no claim of actual B3 routing | TARGETED_PASS / FULL_ROUTE_NOT_IMPLEMENTED |
| 4 | Strategy/portfolio chart each date with independent bars & hover amount and percent compared to previous period | 6 demo periods × 4 demo strategy series: independent signed bars = **24**, full prior-month comparison for each strategy and total with amount and percentage in hover, shared synthetic portfolio value line. All labeled DEMO. Calculation and producer/DTO authority unverified | TARGETED_PASS for interaction, source-bound NOT_TESTED |
| 5 | Color wheel and HEX under expandable RGB/HEX | Restored color wheel; click selects accent; collapsible RGB/HEX details allow manual HEX. Global swatches hide default HEX and reveal on hover/focus. Cancel/Escape restores previous theme role values. **Full theme-token propagation and contrast under arbitrary user palettes not yet passed** | TARGETED_PASS; VISUAL_REVIEW_PENDING |
| 6 | Workbench dragging translucent hover ghost across entire covered area; categorized module catalog | Drag to actual coordinate-backed empty cells; free area for dragged module highlighted/translucent and snaps on drop (not on initial mouse hover); Cancel rollback remains. Catalog still a flat quick-list — **two-stage Category → Subfeature picker NOT YET implemented**. Exhaustive drag collision/resizing not tested | PARTIAL / P0 remainder |
| 7 | NxM slot labels, direct rendered sample on selection | Slot labeled R[row]C[column], previewed financial/demo value or chart symbols while building, independent subject enforced by editor UI. Arbitrary info bindings not API validated | TARGETED_PASS / DTO REVIEW_PENDING |
| 8 | Startup/multi-window settings broken | Settings controls for default/custom/restore, custom page multiselect; same dialogue displays selected pages. Cancel/Escape rollback tested. True relaunch/persist/new window/account scoped context has not been implemented, requires source/architecture review | TARGETED_PASS for concept, PRODUCT_RUNTIME_UNVERIFIED |
| 9 | Visual Reviewer limited in scope; maximum effort, no unauthorized feature changes | Visual-role restrictions clarified in this record. Current UI is still missing multiple earlier v1.3 full-shell behaviors; the previous v1.4 simplification is **not** an authoritative replacement for accepted precode interaction spec. No feature removal is authorized merely by visual polish | PROCESS_BOUNDARY_RECORDED / REGRESSION_PENDING |

## Executed browser tests (Chromium with local set_content)

- Fixture: pure standalone HTML, no network/B3 API/broker.
- `B3_D1_v1_5_BROWSER_CHECKS.json` — 18 named interactive checks **TRUE**, no unhandled JS errors, exact artifact SHA256 included there.
- Main dashboard: original 8 modules; click Market dropdown; toggles.
- Rail: 50% background alpha, no header; mouse leaves and 2050ms later flyout closes.
- Shortcut editor: independent from global settings, `＋匯入` as last category option and opens importer.
- Palette: click wheel changes accent; Cancel restores; startup custom choice + two pages; Esc reverts default.
- Chart: 24 independent bars, hover displays four strategy delta amounts and percentages plus total.
- Module: R1C1 sample value visible on first new slot.
- Workbench: explicit gap + exists, drag-to-empty changes module coordinates; no JS errors.
- Measured default font widths 1920/1440/1100/780: document horizontal overflow zero; after 780px trend responsive min-height fix, default inner card overflow zero. **This is not full 125/150% font, palette, keyboard and all 19 UI workflows qualification.**

## Visual UI Reviewer findings and required next checks

- **VUI-15-P0:** v1.4 reduced prototype to ~40KiB whereas v1.3 precode design HTML was >200KiB. It did not preserve full legacy experience (e.g., advanced widget/chart controls, side modes, custom modules/settings workflow). Future consolidation must compare all agreed functions, not simply accept the shorter v1.4 mock. Need a source-/feature-level full regression crosswalk.
- **VUI-15-P1:** consistent 8px grid, tabular figures, typed source state, no overlap and no nonessential explanation copy by default. Preserve essential Environment/Account/Source/Quality and permission context independent of theming.
- **VUI-15-P1:** new bar chart has synthetic data and interactive tooltip; further inspect legend/currency and time point alignment at 125%, 150%, 1920/2560 ultrawide before acceptance.
- **VUI-15-P1:** light/dark/orange palettes and custom roles need algorithmic foreground contrast checks, rollback, multi-screen visual comparisons; do not allow user palette to obscure trading/staleness/UNKNOWN warnings.
- **VUI-15-P1:** role-specific rule: visual reviewer *may recommend* changes to aesthetics/layout but **cannot unilaterally remove buttons, simplify workflows, change feature locations/IDs or data contract semantics**. A functional change goes through a distinct Owner-design review.
- **VUI-15-P1:** Workbench catalog should implement `類別→子功能模組` before final v1.5 PASS; interaction dragging empty multi-cell slot needs opacity + range bounding box, keyboard alternative, and unambiguous grid snap.
- **VUI-15-P1:** real startup persistence and window/account isolation belong to B3 permission/persistence design, not the HTML mock. Do not promise operational multi-account safety.

## Still unresolved / acceptance gate

- This checkpoint is not `D1-R14-01...10 ALL PASS`, not full v1.5 and not Human Design Acceptance. At minimum: Workbench category picker, general template controls, visual/full-feature compatibility with v1.3, full palette/contrast and 125/150% multiwidth screen states, real semantically typed producer binding and Owner visual acceptance remain pending.
- Design-only Git artifacts must stay on `design/b3-v1-ui-precode-review-20261017`, no accepted branch changes, no formal product Coding.
- On next continuation, address all P0 outstanding in this file plus `D1_V1_4_CORRECTION_REGISTER_AND_ACCEPTANCE_CHECKLIST.md` and re-test. Leave prior versions intact as immutable evidence.