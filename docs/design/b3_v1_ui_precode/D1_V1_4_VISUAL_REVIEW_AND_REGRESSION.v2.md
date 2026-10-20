# B3 V1 D1 v1.4 — Visual UI Reviewer / Regression Supplement v2

**Date** 2026-10-20 (Asia/Taipei). **Status** `PRECODE_DESIGN_CANDIDATE / CORRECTION_IN_PROGRESS`. The source-accepted B3 pin stays `9643bfc93a1631154be877536a1c91fc58df84be`. D1 user decision A (single verified DataSubjectRef per Module) governs this candidate. **No Human Design Acceptance or Coding Grant.**

## Revision trace

- Original full candidate: `prototypes/B3_V1_D1_FullDashboard_v1_4_CANDIDATE.html`, Git initial commit `47e98be6`.
- Visual-review and regression report v1: `D1_V1_4_VISUAL_REVIEW_AND_REGRESSION.v1.md`, commit `4b1ea1f2`; contains original failures and unchanged documentation for audit history.
- Final tested intermediate candidate: same prototype path, updated Git commit `ce253c43d3e57955fc55684bae9aa985c5b8fb64`. Container artifact exact UTF-8 SHA256: `e5f2bffb7782c40f43a168fb195f7baa51b362220704d015b955992ec4c0b0a4`. Use final Git Blob identity for Repository exact bytes.

## VUI findings / changes since v1

| ID | Previous finding | v2 evidence | Status |
|---|---|---|---|
| VUI14-F01 | Trend plot overflow 49 px at 1500/1100/780 | Internal linechart allocated minmax(0,1fr) + 62px bar row; browser DOM reports no card overflow at tested default viewport widths | **FIXED / TEST PASS bounded** |
| VUI14-F02 | News card 125% +4px, 150% +57px overflow | Shortened optional descriptive copy without hiding source/rights warning; removed default paragraph margins; font stress at 100/125/150% on 1500px reports zero card overflow | **FIXED / TEST PASS bounded** |
| VUI14-F06 | ICON importer only validates, no preview | Added local FileReader-based image preview, scope selection, application on explicit shortcut Save; PNG/WebP MIME and 250KB checks, SVG disallowed. This does not upload or persist to B3 API. | **IMPLEMENTED PROTOTYPE / security & usability edge cases not fully reviewed** |
| D1-R14-08 | Slot data field not persisted; custom module blank after placement | Slot now stores same-subject field and render kind; created module stores template ID; homepage displays bounded mock KPI/line/bar/list/quality per slot. Remains mock, not a DTO or datafeed binding | **IMPLEMENTED PROTOTYPE / FORMAL API BINDING UNVERIFIED** |

## Regression actually rerun

Five Playwright browser groups (all PASS without JS page errors): original 8 modules + 6 asset slots + UNKNOWN state; translucent rail + independent shortcut manager and icon import input; occupancy-aware workbench + Cancel/Save; single-subject NxM 6×2 with 7 blocks and return to parent Settings; palette role control. Browser geometry at 1500/1100/780px: doc horizontal overflow 0 and no default card/card-body content overflow. At 1500px, simulated 100%, 125%, 150% body font scale: no card overflow after news fix.

**This is not a blanket PASS of D1-R14-01..10.** Remaining unverified or partial:
- Theme color harmony and dynamic WCAG foreground contrast; color Cancel/undo semantic round-trip (D1-R14-06).
- Icon security (actual signature sniff, decode failure, upload path, cross-device persistence, sanitization) and imported SVG policy (D1-R14-04).
- All card content under 19 UI/64 findings, all class tabs, 1920/2560 displays and 125/150% across narrow viewport, dense labels/translation, input hit areas and keyboard accessibility (D1-R14-01/02/03/10).
- Advanced grid splitting/merging and exhaustive overlap invariants (D1-R14-07); module source data history/currency authority and typed producer binding (D1-R14-08).
- Saved layout persistence, account/window context and multi-monitor test evidence.
- Trading/menu links, scheduling and News are a bounded UI visualization, not authorized official implementation.

## Visual Reviewer next bounded recommendations

1. **Align repeated KPI cards** on consistent 8px subgrid; top-line primary numerical baseline and negative sign/currency typography should be identical.
2. **Use stable chart legend** at fixed 160px rather than letting it crowd the plot; preserve tooltip as the provenance of each decomposed series, not a cosmetic line.
3. **Treat under-filled module state honestly**: keep stable reserved slots or swap to a defined smaller standard template only on deliberate user resize; never invent extra values to fill space.
4. **Contrast check all palette role pairs** after user modification and keep LAB/PAPER/LIVE/UNKNOWN distinction independent of theme. This is a future design gate, not yet passed.
5. **Reduce developer annotations** by default but keep an explicit review toggle so API/DTO/Source/Cut verification remains auditable at Design Handoff.
6. **Never claim every link is functional**: the standalone prototype has incomplete real navigation and no licensed market/news provider; source verification remains needed.

Visual reference links (not product implementation evidence): TradingView saved layouts and split view, and IBM Carbon 8px grid/data table guidelines. See v1 protocol `D1_V1_4_VISUAL_UI_REVIEW_PROTOCOL.md`.

**Release rule:** Owner review of visually complete D1 after D1-R14/VUI gates pass. Repository design branch artifacts are non-authoritative. Before any Coding authorization, reconcile 19 UI, six MA10 units, source/DTO/API and 64 findings in the final review package.
