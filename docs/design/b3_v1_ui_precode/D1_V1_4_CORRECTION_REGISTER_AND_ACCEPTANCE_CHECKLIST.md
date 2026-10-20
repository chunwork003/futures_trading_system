# B3 V1 — D1 v1.4 Corrective Design Register & Regression Acceptance Checklist

> **Status:** `SOURCE_INSPECTED / CORRECTION_REQUIRED / HUMAN_CLARIFICATION_PENDING` (design-only review labels, not formal machine governance states).  
> **Recorded:** 2026-10-20 (Asia/Taipei).  
> **Accepted B3 V1 source pin:** `9643bfc93a1631154be877536a1c91fc58df84be` (source architecture, UI01–UI19 and MA10/PK11 remain unchanged).  
> **Examined visual prototype:** `docs/design/b3_v1_ui_precode/prototypes/B3_V1_D1_FullDashboard_Integrated_v1_3.html`; published Git design branch commit `3b9aeed4e0c299b32a35e406fa595d37f893d99a`; separate review note `D1_GLOBAL_APP_SHELL_DISCUSSION.v1.3-CANDIDATE.md`.  
> **Owner feedback:** 10 annotated screenshots uploaded on 2026-10-20 and ten numbered requirements (UI overflow, asset tab instability, rail overlay, icon import, layout gap, palette, region grid cap, consolidated builder, scope, stop-and-confirm).  
> **Scope:** Pre-coding UX/design prototypes and their review, **not** product React/ASP.NET/Python work, not B3 Authority/API amendment, not WO/Grant, not implementation authorization.

## Implementation rule for this iteration

1. **Do not advertise a v1.4 corrected prototype until it exists and passes all required browser checks.**
2. This register is the immutable input for a **future v1.4 correction**; its creation is not a correction PASS.
3. **Structural ambiguity must be put to Human before rebuilding.** Owner's instruction: clarify and receive approval first when definition unclear.
4. Keep historic D1 v0.2–v1.3 records and artifacts; do not overwrite them. After each correction, append actual changed files, precise browser evidence, counterexamples, outstanding failures and an explicit owner review gate to a new numbered Git record.
5. A test PASS in standalone mocked HTML is not runtime/API/Market/Broker conformance, source approval or Human Design Acceptance.

## Verified root causes from v1.3 prototype *source*, not production evidence

- **Actual four-region limit:** local prototype `patternValid()` checks `d.slots.length>4`; `patternAddZone` rejects `slots.length>=4` with '最多四個可複用區塊'; `studioSave` explicitly truncates `d.slots.slice(0,4)` and pads back to 4. Consequently additional region blocks cannot be created/reused freely. This is a **CODE_OBSERVED** cause.
- **Not an occupancy-aware workbench:** `renderLayoutEditor()` maps the ordered `layoutDraft` array to CSS grid articles; drag/drop only reorders around another occupied card. No explicit `(x,y,w,h)` page-cell occupancy array or 'empty cell' target. This is a **CODE_OBSERVED** cause of unselectable visually unused space.
- **Inconsistent renderer/template guarantees:** `assetCards()`, `content(m)`, `renderCustomModule()` and module-specific CSS apply separate content rules. Some content has fixed heights or `overflow:hidden`; screenshots show cash/currency text clipping and asset content changing composition. **REPRODUCIBLE_BY_OWNER_SCREENSHOT**, requiring systematic responsive/density visual measurements before PASS.
- **Rail flyout conflicting modes:** CSS includes multiple overrides for `.rail-flyout` in fixed/absolute/expanded/push responsive modes; different display selections can overlay or offset the page. **CODE_OBSERVED + OWNER_SCREENSHOT**; fix with one explicit position model and viewport collision logic.
- **Palette labels on-screen:** v1.3 palette markup prints role token / HEX code below swatches by default; unlike requested hover/focus-only labels. **OWNER_SCREENSHOT**.
- **Global vs account/portfolio context:** any module creation or template saving can only capture display bindings; official UI01 read-only summary and UI08 Portfolio ownership remain distinct. Existing accepted MA10/B3 constraints do not grant new data producer or risk/capital authority.

## P0/P1 acceptance cases (repeat after *every* future prototype revision)

| ID | Class | Scope / stimulus | Exact acceptance criteria | Negative / regression cases | Evidence required |
|---|---|---|---|---|---|
| `D1-R14-01` | P0 | All **default** dashboard modules, four top summary cards, portfolio chart, asset summary, six asset cards, holdings | Each module uses declared layout grid, slot capacity and min readable footprint; all required metrics visible; **no unintended clipping**, overlap, body scroll or inner vertical scrollbar; consistent top/bottom spacing. Empty-space minimization by valid presentation choice, not fabricated measures. | Cash row cut off, one card half-empty at same size, long source label clipping, selected 125%/150% typography | Screenshot + DOM bounding boxes/overflow at standard and enlarged font; card/template matrix |
| `D1-R14-02` | P0 | Asset total / Stocks / Bonds / Futures / ETF / Cash / Other, 1/6/8 records and 2 different portfolios | Outer module height, header, slot count and relative position unchanged for **same template+size** when category or page changes. Records > capacity paginate; records < capacity use safe placeholder, not a random mix of unrelated measures. | Switch Stocks → All causes height jump, data merges across incompatible source/cut, unknown as zero | Before/after pixel bounds, items count, pager state and Source/Cut/Quality |
| `D1-R14-03` | P0 | Default compact rail, text-only mode, icon+text mode, expanded mode | Popup is translucent themed overlay near clicked icon, no horizontal page displacement or incorrect overlap; height fits chosen entries and viewport, not artificially tall; click outside/Esc closes with restored focus; rail gear remains shortcut-only. | Click Schedule, flyout opens behind page, popup pushes whole dashboard, flyout intercepts rail icon | Screenshots with positions for all rail modes, keyboard sequence |
| `D1-R14-04` | P1 | Shortcut category icon picker | 20+ valid bundled pictograms with visual selection; a clearly labelled **＋ 匯入圖示** control, preview, Cancel/Save. Preview may support local SVG/PNG; imported SVG sanitized or disallowed until formal security review. Validate MIME, type/size; never inject raw SVG/HTML or accept arbitrary external script URL. | Malformed SVG, huge icon, unsupported format, Cancel should not save, new icon doesn't propagate to rail | Icon palette screenshots, import success/error and security negative test |
| `D1-R14-05` | P0 | Workbench layout editor, 12-col page, deleting/resizing/reordering a card | Every **truly vacant** grid cell cluster must expose target/＋, allow insert valid module, accept drag/drop at its coordinates; occupied cells cannot overlap; auto-packing only if user selected it, not silently. Preserve (x,y,w,h) identity and on-screen outline, maintain unsaved draft; Save applies, Cancel/Esc restores exact prior layout. | Blank after delete has no plus; impossible drag into gap; two cards collide; empty spacer confuses actual occupancy; reopen after cancel changed layout | Before/after grid occupancy matrix, drag test, save/cancel tests |
| `D1-R14-06` | P1 | Global Settings → Panel theme | Align all swatch rows/inputs/labels. Codes hidden in default wheel layout; hover/keyboard focus reveals role + #HEX. Color popover/edit field supports typed `#RRGGBB` and RGB, validates format and updates visible preview. Cancel restores all relevant role colors/fonts; Apply persists only design draft. Ensure contrast and data-quality colors. | Brown theme retains blue border; swatches not aligned, unreadable foreground, invalid HEX accepted, Cancel incomplete | Warm/dark/light preset screenshots, contrast/keyboard cases, CSS token coverage |
| `D1-R14-07` | P0 | Module **internal** grid editor: `N×M` bounded dimensions, 1×1 minimum cells | Every valid free cell can be clicked +, split/merge/resize/move regions while preserving a legal non-overlapping coverage; no **hard-coded 4-slot cap**. Distinguish occupied, empty, disabled; provide message if no free cells. If grid is full, user may split existing regions without data loss confirmation. | Build 6×2 with 5, 6, 8... blocks; drag region to empty target; content bindings don't follow region unexpectedly | Occupancy map, grid coverage test, >=5 region test, undo/cancel/save |
| `D1-R14-08` | P0 — owner clarification | Combined **「模組」** builder | Replace separate '模組版型' and '建立模組' steps with **one editor**: choose data subject/category, choose N×M physical units, click + on slots; right inspector appears only after slot selected and offers metric/data, presentation (numeric/text/chart), subtype (sparkline/line/bar/etc), period/quality where source permits; no user-facing S/M/L/XL, no required custom template name. Generate stable internal ID automatically. | Mix account A capital with account B portfolio; select unavailable historical series as if API exists; empty right inspector default; changing data subject silently preserves invalid binding | User approval of same-subject scope, form state transitions, binding permissions and source/cut display |
| `D1-R14-09` | P0 | **Workbench page layout** versus combined single module editor | '工作台版型' controls module **instances** and positions; '模組' controls internal same-subject data representation. User can create/save module, then place/edit/reuse instances on workbench. No extra '模板庫' prerequisite modal that loses settings context. Save/Cancel/Esc from nested editor returns to the originating setting page, not to dashboard. | Start module edit while global settings open, Cancel unexpectedly closes all; instance edit changes template for every placement unexpectedly | Screen recording of nested return path and module placement |
| `D1-R14-10` | P0 | Source-wide regression after correction | Audit all eight built-in modules + newly created multi-region modules, all 19 official feature links without renaming UI identity, LAB/PAPER/LIVE context, UNKNOWN/STALE/PARTIAL, group-follow vs pinned, sidebar/shell, menu and account state. Run at 1440/1920/wide + narrow, 100/125/150% fonts, multiple palettes, 1/6/8 data records. NO product API, broker or repository runtime modifications. | v0.8 regression revived; v1.1 template-only demo replacing full dashboard; mock value mistaken for cash authority; incomplete test claimed PASS | Structured PASS/FAIL table with screenshot + artifact version SHA, no undocumented skip |

## Proposed simplified design model — clarification required before source modification

```
FeatureRegistry  →  official UI01..UI19 and approved subfeature IDs
DataSubjectRef    →  one authorized account / portfolio / instrument / strategy / research subject,
                     exact environment, snapshot/cut and producer / permission scope
ModuleDefinition  →  generated internal ID + subject reference + N×M grid + slot bindings
ModuleSlot        →  x/y/w/h + supported metric + presentation + subtype + display options
WorkbenchLayout   →  module instances with actual page-grid x/y/w/h, selected pinned subject,
                     visual preferences and draft revision
```

The proposed module builder **does not itself grant creation of arbitrary financial APIs or mixed-authority data**. Example `目前資金 2×1` can show `金額/變化` in cell 1 and `日/月折線` in cell 2 only if the source has a suitable verified history producer. Otherwise the history option is visibly disabled/`UNVERIFIED`, not a synthetic real-data claim.

### Essential unresolved Owner interpretation

**Does '同個資訊' mean one exact source-bound `DataSubjectRef` throughout a module**, such as '帳戶 A／PAPER／目前資金' with different metrics or historical views in the cells (**A, recommended**), or one *broad feature category* such as '投資組合' where different data resources can be combined in cells (**B, requires explicit consistency/authority rules**)? Ask before rebuilding the combined module editor.

## Engineering boundaries and governance gates

- Current checklist is a **design/audit deliverable** only, not an engineering Work Order or authorization to code the official platform.
- Formal accepted B3/MA10 UI IDs, API catalog and operation, DTO/revision, source/cut/quality, risk/capital/order authority and LAB/PAPER/LIVE boundaries remain binding. UI01 Dashboard vs UI08 Portfolio ownership must not be blurred by a user-configured card.
- Any server persistence, icon upload, new historical metrics/time series, cross-window context, multi-account permissions or scheduler execution requires source verification and appropriate architecture/independent review. Do not assert they exist because a design prototype displays controls.
- Preserve existing design branch versions, do not change master, and never claim `Human Design Acceptance` or `Coding Authorization` from this review.
- When Owner selects A/B and confirms, build **one cohesive** v1.4 correction rather than a chain of untracked patches. Each criterion gets PASS/FAIL/NOT_TESTED with concrete evidence; no 'all done' if P0 fails. On final review, crosswalk D1 to UI01/UI08 and MA10-U01/U02/U06, then later 19 UI and 64 Findings at D9.
