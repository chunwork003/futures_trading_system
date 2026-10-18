# B3 V1 — D1 Global App Shell v0.6
**Record:** PRECODE_DESIGN_CANDIDATE / NOT HUMAN ACCEPTED / NO CODING AUTHORIZATION
**Basis:** accepted B3 source commit `9643bfc93a1631154be877536a1c91fc58df84be`
**Design branch:** `design/b3-v1-ui-precode-review-20261017`
**Previous record:** `D1_GLOBAL_APP_SHELL_DISCUSSION.v0.5.md`
**Interactive prototype:** `prototypes/B3_V1_D1_AppShell_Interactive_v0_6.html`
**Prototype SHA256 (UTF-8):** `4d4d7c824431d554293d562db29a4ae73d6de38fae36a3d8e109afa62bc002f9`
**Preview file outside Git:** `B3_V1_D1_v0_6_preview_900.png` (reference screenshot; Git stores full interactive HTML source).

## Latest Human feedback — outstanding continuation
"資產類別與資產清單要有總覽/分類資產（股票/債券/期貨…）頁籤，總覽可自行勾選顯示的資產類型；在各分頁按金額／投報欄可由大到小、小到大排序。"

## Implemented solely in standalone design prototype
- Two **independent** classification controls: asset tile module and Portfolio Assets holdings module.
- Tabs: `總覽 / 股票 / 債券 / 期貨 / ETF / 現金 / 其他`. Page/contract identity remains UI01 Dashboard summary linked to UI08 Portfolio details.
- Overall tab exposes `☑ 顯示類別` with separate category checkboxes per module; checked categories only affect rendered rows/cards. Opening a specific class tab shows that class regardless of overview checkbox.
- `金額` and `投報` sort controls in both modules and additional sortable amount/ROI headers in holdings table: click switches between descending/ascending, new field starts descending. State per module/tab. Null/UNKNOWN values placed after verified demo numeric values.
- Holdings retains card/table toggle. Synthetic value sparklines retain hover amount/delta for asset cards.
- Quality `UNKNOWN`: hide financial value, disable numeric sorting. Zero is never inferred from missing data.
- Export JSON includes category tab, checked categories, sorting state in `portfolio_asset_views`, flagged `classification_status: UI_DESIGN_CANDIDATE_NOT_PRODUCER_TAXONOMY`.
- All values are synthetic demonstration only, not B3 source-connected positions or ROI.

## Targeted browser checks (2026-10-19)
Chromium + Playwright standalone HTML via `set_content`:
- 8 editable modules; six source demo tiles and six synthetic holdings rows at first load.
- Stock & futures tabs render only corresponding asset tiles; Bond tab resolves corresponding Bond ETF tile; returning to Overall retains visibility choices.
- Overall checkbox excludes Bond class, without removing Bond-specific tab availability.
- Amount ascending and ROI descending sorting produce expected demonstration sequence.
- Bond holdings tab shows two bond ETF demo rows; Overview class checkbox can exclude futures.
- Holding ROI sort puts known higher value first; card/list toggle works and retains selected display count.
- UNKNOWN hides numeric amounts and disables value sorting; FRESH restoration shows remaining sparkline cards.
- v0.5 font settings and shortcut editor open; viewport 1000px had document scrollWidth matching viewport; no JS pageerror.
This is a bounded interaction test, not backend/E2E/product authorization.

## SOURCE_CONFIRMED vs PROPOSAL / UNVERIFIED
- SOURCE_CONFIRMED: UI01 Dashboard `/dashboard` and UI08 Portfolio `/portfolio`; MA10-U01 layout, U02 Dashboard/Portfolio context, data quality semantics. API operations include `getDashboard`, `getAccountCapital`, `getPortfolios`, `listGroups`, `queryAttribution`. All exact operation availability is source-spec, not proof deployed.
- PROPOSAL: tabs, overall category selection, sort buttons, default sort, theme, presentation-only grouping and synthetic tooltip.
- UNVERIFIED: official cross-asset classification taxonomy, capability to query/sort directly on API, performance denominator/window/currency and class-level aggregates.
- Important counterexample: bond ETF is both fund vehicle ETF and debt exposure; if `資產類別` mixes underlying asset vs tradable instrument type, double-count and inconsistent filters may result. Recommended future design: two explicit axes `資產曝險類別` and `商品型態` with B3 Producer authority, not inferred string matching. No authority changes committed.
- Filtered view **must not change overall portfolio valuation, weighting or capital/risk permissions**. If an aggregate is scoped to filtered data, label the universe and coverage separately.
- FORMAL_REVIEW_REQUIRED if adding typed query/filter/sort operation, persisted cross-device preferences, new classification meaning, or capital/return computational contract.
- OWNER_DECISION_REQUIRED: later confirm whether to expose Exposure Class vs Instrument Kind as one/two tab rows; don't block D1 layout iteration.

## Status / next owner review
- `D1 v0.6` is awaiting Human modifications and eventual explicit confirmation. No D1 Design Acceptance, WO, Grant, merge, production code, React/ASP.NET/Python change, runtime release or live trading operations.
- Before Coding Handoff, revalidate exact UI/API/DTO and Producer/Consumer and 64 finding crosswalk; keep original 19 permanent UI identities.
