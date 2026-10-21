# B3 V1 D1 v1.6 — Feature Preservation, Source Boundary & Visual UI Reviewer

**Timestamp:** 2026-10-21 (Asia/Taipei).  **Disposition:** `PRECODE_DESIGN_CANDIDATE / HUMAN_REVIEW_PENDING` (informal design labels; NOT machine governance states). **Human-confirmed module rule:** A — one exact data subject per module, represented by different types of information.  **Accepted architecture pin unchanged:** `9643bfc93a1631154be877536a1c91fc58df84be`.

**Design artifacts in this branch:**
- `prototypes/B3_V1_D1_FullDashboard_v1_6_RECOVERY_CANDIDATE.html` — one standalone full homepage + settings + editor; synthetic DEMO only, no fetch/WebSocket/Broker/order.
- `qa/B3_D1_v1_6_REGRESSION_TEST.py` — repeatable standalone Playwright visual and interaction regression; no formal app tests.
- This report, supplementing the *unchanged* `D1_V1_4_CORRECTION_REGISTER_AND_ACCEPTANCE_CHECKLIST.md`, `D1_V1_4_VISUAL_UI_REVIEW_PROTOCOL.md`, `D1_V1_5_FEATURE_PRESERVATION_AUDIT.md` and earlier v0.2–v1.5 history. Do not overwrite historical findings.

## Outcome and testing scope

**30/30 design-only automated checks PASS** using Chromium 2026-10-21 for checked functions and viewport/typography combinations: 1500px, 1100px, 780px × 100/125/150% font. For all eight default cards, body overflow >2px: none; document horizontal overflow: none. The script is committed to enable future exact regressions. Initial implementation contained a JS parser error and chart bars encoded *deltas* rather than amounts; both were corrected **before final 30/30 check**. Therefore the final artifact does not inherit an unverified PASS from preliminary versions.

**Do not confuse the 30 targeted tests with complete design acceptance, source authorization, or implementation QA.** A successful standalone HTML fixture does not prove a B3 DataSubjectRef, licensed Market feed, real Snapshot consistency, Order Receipt or Broker authority.

## KEEP-01–15 capability preservation crosswalk

| ID | Previous deficit | New v1.6 design behavior / evidence | Remaining boundary / classification |
|---|---|---|---|
| KEEP-01 | Eight homepage modules | All eight preserved, stable source `UI01` summary and `UI08` drilldown identifiers in candidate registry | SOURCE_CONFIRMED page boundaries; actual read-model source **UNVERIFIED** |
| KEEP-02 | Four portfolios + global-follow + per-card pin lost | Four mock portfolios; main selection changes unpinned overview/capital/strategy/trend/asset values; independent card data pager and pin; per-card portfolio/cut label | **PROPOSAL**, cross-account/Auth/permission and source/cut rebind require FORMAL_REVIEW_REQUIRED if new DTO/contract |
| KEEP-03 | Chart periods not bound to rendered series | Seven periods (day/week/biweek/month/quarter/half/year) change six x-axis labels; 4 strategy columns per period = 24 independent amount bars; total line and tooltip show amount, previous-period amount delta and percentage; strategy rows same. Synthetic strategy sum normalized to homepage synthetic total for a single subject | **PROPOSAL**, historical return denominator and actual cut/source/period aggregation **UNVERIFIED** |
| KEEP-04 | Asset filtering, sorting and display views lost | All/asset-class tabs; class checkbox subset on overview; amount/return asc/desc sorting, UNKNOWN last; fixed 6 visible asset cells; holdings simple/list toggle; portfolio factor/period source label | **PROPOSAL**; classification dimension, pagination/query and verified aggregate calculations need DTO review; filters must not silently change authoritative total |
| KEEP-05 | Global search and 19 UI links missing | 19 official UI identities addressed in one search/shortcut FeatureRegistry (28 page/subfeature design entries). Results are explicitly **route previews only**, not actual app navigation or unverified service evidence | SOURCE_CONFIRMED UI identity; per-subfeature contract links **UNVERIFIED** |
| KEEP-06 | Shortcut detailed selection/ordering/modes regressed | Separate bottom-left settings: multi-group selection and filter, reorder, icon/text/both mode, spacing, 24 pictograms, appended + PNG/WebP import option; Save or Cancel and design JSON export | **PROPOSAL**. Server preference save, SVG hardening, cross-device imported assets **NOT IMPLEMENTED** |
| KEEP-07 | Translucent rail and auto-close | Compact category overlay (50% themed background), hover hold, outside click/Esc and 1.8s pointer-leave auto-close from v1.5 retained | **PARTIAL** screen-reader/focus-trap and complete keyboard navigation unverified |
| KEEP-08 | Workbench export and empty cell + | 12-column coordinate/occupancy grid, drop-to-empty +, categorized module catalog, draft Save/Cancel, and JSON export in Settings → Workbench | **PARTIAL** exhaustive collision/snap gesture edge cases, revision/CAS/local/remote persistence unverified |
| KEEP-09 | One exact subject NxM, >4 regions | 6×2 creates 7 region cells; same subject per module, per-slot field/view, mock preview, independent editor returns to parent Settings | **PARTIAL** typed Source/DTO field binding, all split/merge scenarios and durable template revision unverified |
| KEEP-10 | Typography/palette presets missing | Recovered existing theme wheel + precise HEX/RGB, edit/Cancel; added typography group, density scale, named in-tab palette drafts; visual proportions adjusted at 9 screen/font matrices | **PARTIAL** WCAG contrast and custom theme semantic token completeness, palettes are not server persisted |
| KEEP-11 | Start modes / multi-window | Existing demo default/custom/last startup mode selector and account/environment safety notes retained from v1.5; cancel rollback test from v1.5 | **UNVERIFIED** actual browser session restoration, multiple authenticated account isolation and persistence need formal review |
| KEEP-12 | Visual reviewer overstepped | Visual reviewer scope limited to alignments, sizes, typography, density, contrast, beauty and recommendations; must **not** change product features, accepted identities, authority or governance | SOURCE_CONFIRMED *discussion process decision*, not formal Independent Reviewer authority |
| KEEP-13 | Single card zoom, fullscreen, export | Single-card read-only zoom restored; fullscreen workbench/desktop via Settings; both workbench and shortcuts can export JSON for review | **PARTIAL** zoom body controls are static preview, and JSON export is local-only with no B3 persistence |
| KEEP-14 | News carousel | 3 mock items, working ‹ › news pager; each item remains SOURCE UNVERIFIED | Provider, attribution, rights, realtime/cut/license **UNVERIFIED** |
| KEEP-15 | Full UI/API/GAP closure | Permanent official UI01–UI19 feature coverage indexed, source-identity not changed | **NOT DONE**: full 19 UI ↔ API/DTO/unit / 64 findings crosswalk belongs D9 and formally bounded review |

## D1-R14 correction gate mapping (no blanket claim)

- **R14-01/02**: eight default cards + categories have bounded PASS for test combos; not full proof for custom long content, 200% fonts or every detail state.
- **R14-03/04**: compact rail, icon mode, import entry design tested; modal keyboard/focus, SVG sanitization and cross-session persistence remain.
- **R14-05**: grid occupancy and empty cells +, insert draft and cancel verified; edge cases after resize/drag all possible geometries not exhaustive.
- **R14-06**: palette wheel, role edits, candidate custom themes and cancel partially exercised; full contrast/cascade test not done.
- **R14-07/08/09**: 6×2 seven slots, one subject, module/workbench separation and return to settings tested; typed metrics and future persistence require source review.
- **R14-10**: incomplete by definition: only scoped design regression, not all 19 pages nor certified architecture.

## Visual UI Reviewer findings (bounded, presentation-only)

**Fixed in current candidate:**
- `VUI16-F01` (P1): dashboard header/card alignment and same-template outer height; cards do not vertically scroll at default.
- `VUI16-F02` (P1): strategy card overflow (125/150% fonts) addressed with compact typographic row rhythm, without removing any of four strategy entries.
- `VUI16-F03` (P1): 1100px 125/150% top-row horizontal overflow addressed with responsive reduced header chrome/search width, not deleting the six top menu entries.
- `VUI16-F04` (P1): 780px, 150% font allocation card overflow addressed by a declared small-width donut profile, retaining all categories and safety status.
- `VUI16-F05` (P0 semantic): each strategy column uses **current per-period amount**, not delta-height; tooltip reports prior-period money and percent. Mock total is coherent with homepage value. For UNKNOWN, numeric trend and allocation percentage hide.

**Still open / Reviewer can only recommend:**
- `VUI16-F06` (P1): 200% user font profile, ultrawide 2560px, extreme language lengths / OS-level browser zoom, high contrast WCAG role-pair audit and keyboard focus paths **NOT TESTED**.
- `VUI16-F07` (P1): distribution of whitespace, longer numeric labels and watchlist/asset chart multiple independent source cuts not yet formally reconciled. Reviewer shall **NOT** remove feature to "simplify" the screen.
- `VUI16-F08` (P1): Tab/Space/Esc focus-management and screen-reader semantics need dedicated design review; popup does not prove accessible just because mouse-click works.

## Measured functionality and review instructions

Run the QA from the design artifacts with 

```bash
python qa/B3_D1_v1_6_REGRESSION_TEST.py prototypes/B3_V1_D1_FullDashboard_v1_6_RECOVERY_CANDIDATE.html
```

Requires Python Playwright and installed Chromium. Default executable `/usr/bin/chromium`, change using `CHROMIUM_PATH`. The test reports **30** targeted checks; a changed prototype MUST rerun them. Screenshots are delivered as conversation artifacts, not production design license references.

## Hard governance boundary

This version remains **design-only standalone mock HTML**, not B3 frontend implementation. No accepted B3 Architecture, MA10/PK11/DTO/API, Order/Capital/Risk permission, LAB/PAPER/LIVE authority or Broker I/O changes were made. In particular portfolio pinning is visual mock subject rebinding and **not** a multi-account authorization scheme. Notes for possible persistence and historical data improvements are 
`FORMAL_REVIEW_REQUIRED` if contracts change; Human Design Acceptance is separate from Coding Authorization.

**D1 status:** `DESIGN_CANDIDATE / OWNER_FEEDBACK_PENDING`. No D1 closure. Before design acceptance, address KEEP-10/11/15, VUI16-F06–08 and the full R14-10 crosswalk or record reviewed bounded exceptions with Human authority. Never silently conclude D1 PASS.