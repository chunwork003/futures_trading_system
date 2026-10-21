# B3 V1 — D1 v1.8 Owner Decisions, Workbench/Shortcut Correction and Visual Review

**Date:** 2026-10-21 (Asia/Taipei). **Review status:** `PRECODE_DESIGN_CANDIDATE / HUMAN_REVIEW_PENDING` (discussion labels only).  
**Official accepted design pin:** `9643bfc93a1631154be877536a1c91fc58df84be`.  
**Design branch:** `design/b3-v1-ui-precode-review-20261017`. **Source artifact:** `prototypes/B3_V1_D1_FullDashboard_v1_8_DESIGN_CANDIDATE.html`.  
**Origin:** v1.7 complete interactive dashboard, prior v1.4 10-case checklist, v1.5 and v1.6 KEEP-01..15 preservation controls.  
**Boundary:** static standalone UI/UX design prototype with synthetic mock data; **no formal React / ASP.NET / Python implementation, Broker/Market API connection, execution authority, architecture amendment, Work Order / Grant, or Human Design Acceptance**.

## Exact owner decisions (2026-10-21)

| Decision | Owner-approved interpretation | v1.8 candidate behavior |
|---|---|---|
| D18-OWN-01 | Keep Quick/Shortcut JSON export in **lower-left corner** | Export button relocated to Quick dialog footer left; modal transition cleans stale exported buttons. |
| D18-OWN-02 | Left rail **hover only** (no click-pinning), delay close **2.0 seconds** after pointer leaves | `mouseenter` opens, `mouseleave` schedules 2000ms; entering flyout cancels timeout, Esc still closes; flyout width follows actual items, no large title / extra space, 75% transparent backdrop target. |
| D18-OWN-03 | **Only customizable pages** may combine functional categories. **My Assets** must remain capital/performance/cashflow oriented | Workbench A-category control locked on regular pages and on Portfolio / My Assets; only `custom-1` allows category switch. Existing legacy all-portfolio dashboard modules remain as historically displayed; no newly authorized cross-category API. |
| D18-OWN-04 | First version B representation options = 6 + **綜合** | `指標卡 / 圖表 / 比較 / 清單 / 表格 / 文字摘要 / 綜合` as semantic filtered choices. C lists only matching available prototypes, no invented source data. |

## UX/UI correction details

1. **Quick editor** retains selected-feature tree, reorder/remove, categorical source selection (UI01–UI19), and adds a fixed single row with Display, Spacing, Category and a narrow **visual glyph** selector; last option `＋匯入…` triggers native PNG/WebP browser picker directly (mock local preview, 250KB limit, no backend upload). Shortcut JSON export is bottom-left.
2. **Hover flyout** adopts content-based max width and small padding, glass/translucent effect, hover-only interaction and delayed close; no click pinning. Keyboard accessibility still needs a full focus-management review (the prototype triggers on focus but does not implement a complete focus-trap protocol).
3. **Palette** uses independently authored color wheel + five swatches and five harmony approaches; default presets 深藍 / 暖棕 / 翡翠; custom palette naming/add/remove and per-role editable color inputs; HEX and RGB fields available when editing selected swatch. Theme change is a *draft*, Cancel/Esc restore role colors and user custom palette list in the standalone page. **Not a pixel-for-pixel Adobe clone and not an official product integration.**
4. **Workbench Editor** directly opens as a three-pane dialog from Settings → 工作台版型, retaining all eight original homepage modules. Left: page/category hierarchy plus proposed category-shared *geometry* checkbox and per-page choice between category default/personal design; centre: 12×8 occupancy grid, vacant cells and modules with `−`; right: A category (locked except Custom), B presentation type, C filtered module registry. Footer-left JSON.
5. **Drag / drop** starts on pointer-down, uses transparent whole-footprint ghost, clamps proposed `(x,y,w,h)` to the canvas and checks all cells via `fits`; applies only on pointer-up if valid. Save/Cancel/Esc isolates the draft; changes do not touch the live Dashboard until Save.
6. **Module management** in Workbench now has entry, return, search, existing edit, clone, create, and delete candidates. In-use delete needs a subject-compatible replacement. Reentrant edit returns to Workbench module management rather than losing the parent context. The prototype is a concept; deletion/replacement needs a revisioned, permissioned server contract later.
7. **Page template sharing:** if selected for a category, geometries `(x,y,w,h)` can be propagated to corresponding positions of each page's *own existing module instances*. It intentionally does **not copy one page's modules, source bindings, or official UI identity into another page**. This sharing behavior is a candidate for formal data/contract design review; it does not create a new resource API.
8. **Font accessibility:** 1500/1100/780 px × 100/125/150% mock font-size geometry profiles were measured; the candidate avoids test-detected horizontal and card-inner overflow. This is bounded visual QA, not a WCAG certification or all-browser/OS zoom test.

## Test evidence (design only)

- **Regressions:** `qa/B3_D1_v1_8_REGRESSION_TEST.py` and `qa/B3_D1_v1_8_REGRESSION_REPORT.json` — **12/12 PASS**, 0 JavaScript page exceptions for these scenarios. Test endpoints: eight baseline dashboard modules; 2s hover; quick editor and native icon selection; palette Cancel; workbench left/middle/right components; ordinary page category lock vs custom; pointer drag of whole card to truly vacant row; module-management navigation, new and copy; draft rollback; source identity isolation; no cross-page changes from Cancel.
- **Visual audit:** `qa/B3_D1_v1_8_VISUAL_AUDIT.json` — **9/9** geometry samples show zero horizontal/document and baseline-card inner overflow at 1500/1100/780 widths and font sizes 100/125/150%. This measure does not cover every item under long localized strings, 200% zoom, high density custom modules or all 19 UI pages.
- **Visual Reviewer mandate:** inspection of alignment / size / hierarchy / spacing / legibility / responsive states, but **no authority to delete, redefine, or relabel existing features or to change approved B3 architecture and APIs**.
- Browser implementation: headless Chromium, HTML `set_content`, synthetic test fixtures only. No backend, real account, risk validation, authorized trading, API history or persistent storage involved.

## Known risks and incomplete design gates (do not report as PASS)

| ID | Area | Disposition / next gate |
|---|---|---|
| D18-G01 | All existing approved navigation/module interactions (v0.2–v1.7) | **PARTIAL** — this iteration preserves the homepage and key settings workflows, but exhaustive KEEP-01..15 and D1-R14-01..10 cross-version E2E audit still pending. |
| D18-G02 | Workspace drag/drop and occupancy | **PARTIAL** — whole-footprint valid drop tested. Edge collisions, nested scroll offset, touch, transform scaling, drag cancel, multi-row and dense packs need tests. |
| D18-G03 | Page/class unified template semantics | **PROPOSAL** — geometry sharing only, never source/subject transfer. Need formal authorization scope, CAS revision and no unauthorized content reuse. |
| D18-G04 | Native icon import | **PARTIAL** — client PNG/WebP MIME/size checked; does not prove file byte magic, image decode sanitization, security/cross-device storage, or formal asset upload API. SVG not supported. |
| D18-G05 | Theme and contrast | **PARTIAL** — role colors and custom palette drafts; contrast of all arbitrary combinations and alert palettes not fully reviewed. Safe data-quality semantics must remain visible. |
| D18-G06 | Representation Module B/C menu on underdeveloped pages | **UNVERIFIED** — no invented modules for non-UI01/08 areas. Do not substitute fabricated DTO/producers for real source contracts. |
| D18-G07 | Real multi-window/per-account startup, scheduling, alert/news | **UNVERIFIED / FORMAL_REVIEW_REQUIRED** — B3 source/currentness, Auth/Subject, Source/Cut/Quality, scheduler and persistence require bounded architecture review. |
| D18-G08 | Wide monitor + 200% font + keyboard/screen-reader/contrast | **NOT_TESTED** — further visual & accessibility tests before D1 acceptance. |
| D18-G09 | Precise source/DTO/contract mapping for 19 UI, 6 MA10 units, historical findings | **UNVERIFIED / PRECODE HANDOFF BLOCKER** — continue source-bound review, preserve official identities. |

## Owner next visual checkpoint

Review the full HTML prototype with these three paths: `左下齒輪 → 快捷` (JSON lower-left, icon last import); `右上 ≡ → 面板` (wheel, custom palette, Cancel); `右上 ≡ → 工作台版型` (category/page left → A/B/C right → whole-area drop in centre → save / cancel). Send screenshots or say no more D1 edits only after visual approval. **D1 remains open.**