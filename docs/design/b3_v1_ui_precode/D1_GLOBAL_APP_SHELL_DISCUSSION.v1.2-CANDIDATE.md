# B3 V1 / D1 投資總覽＋App Shell — v1.2 設計修正與回歸紀錄

**Date:** 2026-10-19 (Asia/Taipei)  
**Status:** `PROPOSAL / HUMAN_REVIEW_PENDING`（設計討論標籤，非正式治理狀態）  
**B3 accepted baseline:** `9643bfc93a1631154be877536a1c91fc58df84be`  
**Prior design artifacts:** `D1_GLOBAL_APP_SHELL_DISCUSSION.v0.2.md` 至 `v0.9.md`、`v1.0-CANDIDATE.md`、`v1.1-CANDIDATE.md`、`D1_v1_1_CUSTOM_MODULE_DESIGN_SPEC.md`。既有版本完整保留，未覆寫。  
**Design-only HTML:** `docs/design/b3_v1_ui_precode/prototypes/B3_V1_D1_FullDashboard_Independent_Editors_v1_2.html`  
**Local exact-byte SHA256:** `b05b8c9d7b58d817a91ae3500167b86fd7ff24ccaa680a96659c20da57d472f4`（須以 Git 已發布 blob 內容為最終 Repository 對照）。  
**Implementation boundary:** Standalone interactive visual prototype, synthetic/mock data only. No React/ASP.NET/Python product code, no Broker/Market API, no official WO/Grant/merge/Coding Authorization.

## Human-requested six corrections and concrete dispositions

| Finding | Observed v1.1 regression or requirement | v1.2 design implementation | Test / classification |
|---|---|---|---|
| D1-12-01 | Prior discussed '左下快捷設定 vs 右上全域設定' regressed: left-bottom gear still invoked `openFonts()` | Left-bottom `⚙` now directly opens separate `快捷編輯` dialog, not global Settings. Right-top `≡` opens global Settings only. Shortcut editor includes selected categories/functions, 24 built-in monochrome SVG icon designs and grouped icon selectors, collapsed/expanded rail preference, Save/Cancel, optional JSON export; does not grant user-defined upload/executable SVG privileges. | Browser: open left gear → shortcut dialog visible, global Settings hidden; changing ICON and side-mode then Cancel leaves originals unchanged. PROPOSAL. External icon file upload still FORMAL_REVIEW_REQUIRED for sanitizer/CSP/assets. |
| D1-12-02 | Global settings window jumps size depending on tab | `全域設定` dialog fixed to `min(820px,90dvh)` in height and `min(1210px,96vw)` in width. Header/tabs/footer fixed; **only tab content scrolls vertically**. On smaller screens viewport limits apply. | Browser checked all seven tabs: 820px (Color / Font / Display / Workbench / Templates / Startup / Refresh). PASS for tested desktop breakpoint. |
| D1-12-03 | '快捷 / 工作台' are separate responsibilities, not one configuration pane | Top-right Settings now has distinct `工作台版型` and `模組模板庫` tabs. No visible shortcut editing there. Sidebar presentation settings were moved into the bottom-left shortcut editor. Hidden IDs remain only for backward-compatible event handler bindings, not navigation. | Browser confirmed `settingShortcuts` hidden and templates editor only in templates tab. PROPOSAL. |
| D1-12-04 | Setting the full workbench layout vs creating the internal content of a custom template must not be the same action | **Workbench Layout Editor:** positions/sizes/add/remove/order module instances of the whole page. **Custom Module Studio:** defines module category/size/internal A/B/C slot content and saves reusable templates in 'My Template Library'. Template size compatibility and feature-source gating stay as already proposed. | Browser verified distinct modal IDs and different opening paths; full homepage eight original cards unchanged on studio open. |
| D1-12-05 | Workbench layout editing must occur in independent popup/page, NOT editing live Dashboard by a toggle; explicit Save/Cancel/Escape | New `layoutEditShade` independent 12-column workbench grid with left catalog, central whole-page layout preview, selected-module inspector, order up/down, drag reordering, compatible size +/- and remove. All changes staged in `layoutDraft` clone. `Cancel` / `Esc` discard; `儲存版型` copies to Dashboard. Reset only resets the **draft**, not live Dashboard, until explicit Save. Normal Dashboard does not show old edit controls. | Browser test: initial 8 cards; draft resize first 3→4 columns, press Escape → live card still 3; reopen resize + Save → live card 4. PASS. |
| D1-12-06 | Address previously discussed items first, no new unrelated work | Regression review below; v1.2 focused on settings boundaries and independent editing. Does not mark D1 adopted. | OWNER_REVIEW_PENDING |

## Scope-bound regression ledger

- **Unchanged and retained from v0.9/v1.1:** UI01 Investment Overview homepage with original 8 card modules; UI08 drill-down navigation; 19 immutable UI01–UI19 IDs with Feature Registry; market/lab/tools/trading/news top nav; top search near Account; LAB/PAPER/LIVE mock cues; source/cut/quality; chart/card portfolio selections; UNKNOWN-safe mock values; fixed-capacity asset and holdings cards; Main Portfolio follow/pin behavior; per-card zoom; A/B/C Template Studio; design-only JSON export.
- **Restored specifically in v1.2:** left gear no longer opens global Settings; shortcut and workbench separated; workbench edits do not alter real displayed dashboard until Save; distinct module template library; independent editor has Escape/Cancel rollback.
- **Still PROPOSAL / UNVERIFIED:** actual frontend preference persistence, server-side layout/Template Registry schema, multi-window per-account Environment/Permission/Portfolio pin, responsive size-readability at every density, real UI01/UI08 Portfolio/Cash/Return Snapshot/DTO calculation semantics, Research Scheduler service, external SVG/file upload hardening. These cannot be marked complete from a local HTML preview.
- **Practical remaining quality review:** detailed template capacity constraint on *every* S/M/L/XL variant, minimum-size policy for chart and KPIs, 150%/200% font stress testing, color contrast/keyboard focus, ARIA dialogs and focus trap, collision layout/viewport widths, routing & permission constraints. These must be qualified before D1 Design Acceptance/PK11 Coding handoff.
- **Known design boundary:** the standalone Layout Editor is a 12-column *schematic full-page preview*, not pixel-exact reproduction of every financial graph; the underlying full Dashboard remains accessible after Save. It has no server API, persistence assurance, Broker action or Human Design Acceptance effect.
- **No new B3 identity or authority:** UI01 is Dashboard `/dashboard`; UI08 Portfolio `/portfolio`; UI17 Settings `/settings`; MA10-U01 shared state/layout applies. A template is a personal visual design object, **not** a new UI20, API, risk/capital decision or Broker authority.
- **Design records** belong on `design/b3-v1-ui-precode-review-20261017`, not master. Consolidate all accepted visuals, 19 UI contracts, six MA10 Units, 64 findings crosswalk and missing DTO evidence into final `B3_V1_UI_UX_DESIGN_REVIEW_PACKAGE` before any formal Coding process.

## Browser check detail

Standalone Chromium headless loaded HTML through `set_content` (sandbox file:// restriction). 1550x980:
- Eight initial dashboard cards; no uncaught JavaScript errors.
- Left `⚙` opens independent Quick Editor; Cancel restores display mode and pre-edit icon names. 24 icon options available per category.
- Seven tabs produce fixed Settings height **820px** at test viewport.
- Separate Workbench Layout Editor height **850px**, includes eight draft cards, catalog, movable/resizable draft; Escape discards draft; Save commits 3→4 column change to visible Dashboard.
- Separate Module Studio `A/B/C` opens only from `模組模板庫` tab, not from layout editor. No JavaScript runtime errors.
- Screenshots: `B3_V1_D1_v1_2_dashboard_preview.png`, `B3_V1_D1_v1_2_settings_preview.png`, `B3_V1_D1_v1_2_layout_preview.png`, `B3_V1_D1_v1_2_shortcuts_preview.png` as conversation deliverables, not committed binary assets to this Git design branch.

## Human gate

**D1 v1.2 = PROPOSAL / HUMAN_REVIEW_PENDING.** Await visual review of (1) separate bottom-left shortcut modal (2) fixed global Settings with Workbench vs Template tabs (3) independent staging, Save, Cancel/Esc. Do not advance to D2 or declare D1 Human Design Acceptance without explicit owner confirmation. Human design feedback does not authorize PK11 coding.
