# B3 V1 — D1 v1.10 working checkpoint, integrated recovery gate (NOT FOR HUMAN VISUAL SIGNOFF)

**Date**: 2026-10-21 (Asia/Taipei).
**Human instruction**: continue until every previously requested D1 design correction is addressed; **do not deliver iterative previews or ask for item-by-item testing**. If unfinished, request the single word 「繼續」.
**Design authority baseline**: `9643bfc93a1631154be877536a1c91fc58df84be`.
**Design-only branch**: `design/b3-v1-ui-precode-review-20261017`.
**WIP prototype**: `docs/design/b3_v1_ui_precode/prototypes/B3_V1_D1_FullDashboard_v1_10_WIP.html`.
**B3 runtime authority**: none. No React, Python, ASP.NET, broker, formal UI identity, API, DAO, SQL migration, Work Order or Coding Grant changes.
**Owner decisions inherited**: A exact single DataSubjectRef/module; three layers 工作區 → 模組 → 資訊模組; A/B/C filtering on workbench; default/custom startup scenarios; hover-only shortcut flyout 2-second close; custom pages only allow cross-category; seven presentation kinds (KPI, chart, compare, list, table, text, composite); Visual Reviewer only makes presentation/legibility suggestions.

## Critical post-publication regression evidence

Fresh rerun of `B3_D1_v1_9_REGRESSION_TEST.py` against the exact saved v1.9 HTML **failed** at selector `#d19Kind`: `d19RenderInspector()` referenced `group` without declaration, causing the A/B/C inspector construction to throw. A historical 18/18 claim cannot be relied on for those bytes. This WIP adds `const group=d19.group` inside that function, and the same 18-case bounded browser script now completes **18/18 PASS**. This is a tested repair, **not a blanket D1 acceptance**.

## v1.10 internal WIP modifications implemented so far

| ID | Actual change | Evidence / qualification |
|---|---|---|
| W10-01 | Restore undeclared `group` in workbench A/B/C inspector | Prior script reproduced failure; rerun **18/18 PASS** |
| W10-02 | Shortcut icon dropdown has **remove-custom / restore semantic default** item and retains native import as **last** item | New 8-case browser regression verifies selector, reset and import ordering |
| W10-03 | Category `統一模板` now applies only valid same-cardinality **(x,y,w,h) geometry** across its member page drafts, keeping each page's own module identity/subject | Browser verified moving `all` first card to row 6 then save & reopening `p1` shows same first-card geometry; source and permission bindings not copied |
| W10-04 | Module NxM information slots support pointer drag to nearest legal cell, per-slot width ± / height ± / delete, checked rectangular occupancy | New test verifies resizing 1→2 columns and back; exhaustive collision/cancel cases outstanding |
| W10-05 | Panel now exposes grouped typography (English Arial/Chinese Microsoft JhengHei, general, card title, main number, note) with staged Cancel/Esc/Save | Browser changed KPI 29→33, Cancel restored 29, Save 31 persisted in design page |
| W10-06 | Theme role coverage expanded beyond root background to header/trust/rail/cards/assets/controls/editors; foreground chosen for contrast if invalid | Warm-brown role inspection verified header/trust/rail/card/button all warm; Cancel returns accent to base; all user-designed palettes need exhaustive contrast validation |
| W10-07 | Global top nav now independently scrolls at high zoom, responsive card KPI size and total-group text wraps | 1500,1100,780 widths × 100,125,150% `body.style.zoom` browser geometry: **23/23 bounded checks PASS** including no body horizontal and baseline card-body overflow, plus individual chart 24 strategy columns, UNKNOWN masking, no JS page errors |

**Verified HTML checkpoint Git commit**: `51a5c9cbccd4eed3a9c1743b42665f97a231c2f7`. Note: tests were local containers / Chromium headless; runtime or deployment evidence not implied.

## Master acceptance checklist: previous owner requests must not regress

Discussion codes below are **review bookkeeping**, not new official machine states.

| Gate | Expected integrated behavior | Current WIP status |
|---|---|---|
| D1-M01 | Full UI01 investment dashboard always displays original eight default cards, with coherent comprehensive view distinct from p1–p5 and per-card pinning | PARTIAL: homepage and portfolio switch verified; exhaustive 5-set/asset-pinned account matrix outstanding |
| D1-M02 | All data cards use declared information templates; equal-size cards aligned, meaningful supported contents, no clipping/inner vertical scroll at 1/6/8 records; page-turn outer geometry invariant | PARTIAL: 9 visual-zoom combinations and baseline cards measured; all tab/filter/long-text permutations outstanding |
| D1-M03 | Time aggregation day/week/biweek/month/quarter/halfyear/year; per-timepoint separate bars for each strategy, prior change amount **and percent** in tooltip, valid total identity | PARTIAL: individual portfolio SVG has 24 strategy bars, tooltip semantic correctness/period aggregation not exhaustively checked |
| D1-M04 | Asset donut and labels include category amount/share, six-slot asset categories/holdings, optional sorting and no filter induced misstatement of total funds | PARTIAL: verify all tab/sort combinations and data quality labels |
| D1-M05 | Compact icon-only default side rail; selected shortcuts grouped; flyout auto fits items, 75% transparency, hover only, closes after 2s; no main-canvas push | PARTIAL: existing v1.8 baseline; all modes/zoom focus and visual collision need retest |
| D1-M06 | Quick editor exclusively bottom-left, selected/unselected feature hierarchy, order/delete, display/spacing, *semantic visual icon picker*, imported local PNG/WebP last, reset/delete, JSON bottom-left, Save/Cancel | PARTIAL: selector reset/import and feature tree tested; upload malformed-magic/decode edge cases, density and full rollback yet to verify |
| D1-M07 | Top nav Portfolio/Market/Lab/Tools/Trading/News with News last, search beside account, Settings under upper-right ≡; no 'More' | PASS bounded: baseline navigation and toolbar responsive retested; route entitlement remains mock |
| D1-M08 | Global Panel Adobe-inspired editable wheel/harmonies/five-swatch handles, click-color HEX/RGB popover, named default/custom themes, semantic theme role coverage, font sizes/families by group; theme Save/Cancel | PARTIAL: wheel/preset/theme role/rollback & grouped typography present; precise handle lines / per-swatch popover, all 5 custom roles and arbitrary contrast to be thoroughly reviewed |
| D1-M09 | Workbench opens **directly** into independent three-pane editor; left category/page tree + unified template checkbox; personal pages can select own layout; center grid; right A/B/C with preview + Add | PARTIAL: A/B/C blocker fixed; checkbox geometry sync bounded; complete category/page source conformance outstanding |
| D1-M10 | Drag **whole rectangular footprint** with translucent ghost, nearest legal slot when occupied, preserve (x,y,w,h), explicit Save/Cancel/Esc, no unexpected reflow, empty slots can remain blank | PARTIAL: basic pointer drag tested; dense/full-edge collision matrix, resize and UI focus pending |
| D1-M11 | Workbench module-management search/edit/copy/new/delete in-used-with-compatible-replacement; revert to originating Settings tab; JSON footer left | PARTIAL: second-layer entry and module workflow tested; full replacement transaction/rollback/persistence pending |
| D1-M12 | Module editor left categorized tree, central NxM adjustable regions with IDs, right A-G fields (locked subject category, editable name, preview, save/overwrite-or-new), no hard 4-slot limit | PARTIAL: slot >4, resize/move and A-G core tested; exhaustive deletion/resizing conflicts and focus pending |
| D1-M13 | Information module third layer supports data vs UI navigation, X time / Y authorized subject field, output type, day–year, aggregate, units/precision, data flow and visual preview; no arbitrary front-end SQL | PARTIAL: `QuerySpec` design-only UI tested; real producer/DTO/Source/Cut/Quality field binding UNVERIFIED; any new API needs FORMAL_REVIEW |
| D1-M14 | Launch configuration separate default/custom/restore, new scenario pages with tab/window assignment, optional multiple display layouts; never leak account or trading authority | PARTIAL: mock scenario addition and cancel test; true window creation, saving, auth isolation not authorized |
| D1-M15 | All 19 official UI IDs & six MA10 Units preserved, previous 64 findings crosswalk and 19 UI/UI18 precise mapping included at Design Handoff | NOT COMPLETE: source-bound documentation gate, NOT automatically solved by mock HTML |
| D1-M16 | Visual Reviewer audits density, alignment, 8px rhythm, typography, semantic color quality, responsive 200%, contrast, keyboard/pointer, without changing product functionality | PARTIAL: bounded 1500/1100/780 × 100/125/150 measured; 200%, 2560, WCAG, screenshot inspection outstanding |
| D1-M17 | All changes documented in Git, source pin, SHA, operations and negative tests; prior versions immutable; no claim of Human Design Acceptance or product Coding Authorization | IN PROGRESS: this WIP checkpoint recorded |

## Release/handoff rule

**Do not show v1.10 WIP as a final preview or invite Human testing yet.** Continue development against every D1-M gate, re-run D1-R14-01…10 and KEEP-01…15, produce reviewer-verified screenshots and report. When all design-interaction gates complete, prepare one cohesive complete dashboard prototype and one consolidated test/review package. Mark contracts requiring formal architecture/authority evidence separately as `UNVERIFIED/FORMAL_REVIEW_REQUIRED`, not as fake back-end capabilities.

Until then the user-facing response is only: 「任務尚未完成，請按『繼續』，接續完成後續任務」.
