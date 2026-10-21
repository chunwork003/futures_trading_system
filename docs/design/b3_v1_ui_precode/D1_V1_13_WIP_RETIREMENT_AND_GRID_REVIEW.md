# B3 D1 v1.13 — Atomic Module Replacement + Whole-Footprint Drag QA Checkpoint

**Date:** 2026-10-21 Asia/Taipei  
**Status:** `DESIGN_WIP / HUMAN_REVIEW_NOT_READY`. Informal review labels; not official Architecture/Authority machine state.  
**B3 source-bound design pin:** `9643bfc93a1631154be877536a1c91fc58df84be`.  
**Design-only branch:** `design/b3-v1-ui-precode-review-20261017`.  
**Prototype:** `docs/design/b3_v1_ui_precode/prototypes/B3_V1_D1_FullDashboard_v1_13_WIP.html`  
**Local tested source SHA256:** `06e1d461c3f5c48b3768eced93ba290fa88b370c32df1225bb9f393eb67aed91`  
**Prototype Git commit:** `09f4c98f125c4666fd97fc0569ae3ad9f5dab224`.  
**User's explicit delivery rule:** Do not request iterative visual testing, provide intermediate screenshots, or mark D1 finished until all previous corrections have been implemented and reviewed. While incomplete, only ask to reply 「繼續」.  
**Boundary:** A standalone HTML/JS design study with synthetic/mock data. This is not product React/ASP.NET/Python implementation, server-persisted versioning, market/broker evidence, official UI01–UI19 amendment, Work Order, Grant or Coding Authorization.

## Two concrete prior-version root defects corrected

### A. In-use Module deletion was non-atomic (P0 design/data reference integrity)

Previous `d19DeleteModule` immediately changed every workspace instance's `templateId/title` to the replacement *before* displaying the final `confirm(...)`. Thus, selecting a replacement but choosing **Cancel** on the final confirmation left the original template present **while live design drafts already referred to another**. This directly violates the user's requirement to warn and choose a replacement, then honor Save/Cancel/Esc without side effects.

New v1.13 behavior:
1. Present in-editor named select of **only** available custom templates with same authorized design subject **and** category and at least one defined information slot; do not demand the user type internal IDs.
2. No draft or library mutations when choosing or canceling this panel.
3. On final confirmation **Cancel**, reference graph and module library remain byte-equivalent to pre-action state.
4. On final **Confirm**, copy draft/library, update *all* referencing workspace pages, then atomically publish replacement references plus remove retired definition. Keep module instances' coordinates/footprints unchanged; if the replacement's natural internal size differs, visual editor must be revisited.
5. Entire editor's Cancel/Esc still discards even a previously confirmed **staged** retirement.
6. Unsupported category/subject replacements and deletion with no candidate are blocked, requiring the owner to create an appropriate alternative.

**Negative counterexample now covered:** decline native final confirm after selecting replacement; former behavior incorrectly changed `templateId`, v1.13 keeps both original references and original module.

### B. Far out-of-canvas pointer release snapped modules to a boundary rather than canceling movement (P1)

Original `d19GridPoint` clamped out-of-range mouse coordinates to a valid grid location. A pointer dropped far outside the workspace could unexpectedly move a full rectangle to the edge. New `d19GridPoint` explicitly marks `outside` beyond a 16px edge-tolerance and returns no candidate on pointer-up; the current coordinates remain unchanged. The translucent ghost displays out-of-bounds state. Within the canvas, full rectangular collision and nearest legal position logic remains, not first-cell-only insertion.

## Reproducible bounded design-browser evidence

The latest HTML file was used for **all** suites. Playwright was run locally with Chromium against the synthetic HTML via `set_content` (not the production app). Source hash is pinned above.

| Regression suite | Passed | Fail | Key claims |
|---|---:|---:|---|
| Three-layer editor inherited suite | 18 | 0 | Workspace/module/info navigation, A/B/C category restrictions, startup scenario cancel |
| Portfolio/asset/quick editor matrix | 26 | 0 | Eight original cards, all/p2, asset six slots and pager, toolbar, UNKNOWN masks |
| Color wheel/harmony | 13 | 0 | Five swatches, HEX/RGB popup/Cancel, no JavaScript error |
| Responsive width/zoom smoke | 14 | 0 | 2560/1920/1500/1100/780px and 100/125/150/200% simulated CSS zoom, no unexpected body/card overflow |
| Module retirement (incl. multi-workspace) | 10 | 0 | Replacement select; cancel panel; decline final confirm; confirmed update to **two** workspace refs; entire editor cancel rolls back |
| Grid geometry property/pointer suite | 5 | 0 | Legal nearest occupied-rectangle, **600 generated size/position cases**, far outside pointer canceled, no JS errors |
| **Total bounded cases** | **86** | **0** | Not a claim of 86 formal B3 acceptance tests |

All tests were re-run on the exact final local prototype after its last change. The geometry suite's 600 randomized property examples are **one aggregate reported PASS case**, not 600 individually reported cases. Prior prototype, reporting and test scripts remain in the conversation working container; portable Git QA tests should be captured before handoff.

## Open issues explicitly NOT finished

1. Complete `D1-M01..17`, `D1-R14-01..10`, `KEEP-01..15` across previous design versions, not just the above six suites.
2. Implement and verify full custom-template usage replacement UX with detailed preview, typed successor revisions, complete undo/safe Save, and every module internal NxM split/merge edge; the current selector is a **bounded design candidate**.
3. Review all 19 UI/6 MA10/64 findings, exact UI18 mapping and source-bound DTO/API QuerySpec governance; no frontend-executable SQL.
4. Multi-account/multi-window session isolation, startup persistence and broker Order/Risk/Capital authority require formal source review; mock controls are not evidence.
5. Accessibility: **native** browser zoom, true large-text 200%, keyboard trap/Esc/focus restoration, ARIA, SVG chart tooltip semantic text, all color palettes' contrast/semantic tokens.
6. Chart time aggregations (day/week/biweek/month/quarter/halfyear/year), amount and prior-period % per strategy and cross-cut/FX safety require source-bound metric verification.
7. Module sizing in workbench and nested info editor across legal rectangle footprints, fixed-capacity pages, empty/8+ data, 2560 ultrawide and narrow modes require full Visual Reviewer signoff.
8. External icon import MIME/magic/decode and local-only sandbox, user-defined palette color input, Cancel rollback and browser persistence continue pending the final integrated regression.
9. Reviewer roles: Visual UI Reviewer may advise on alignment/visual hierarchy only, never remove agreed functionality or change accepted architecture.

**Release instruction:** Maintain `v1.13 WIP` and continue bounded improvements on subsequent turns. **Do not present a new full preview or claim Human Acceptance** until all user-requested D1 UI behavior is consolidated and formally reviewable.
