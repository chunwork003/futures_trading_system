# B3 V1 UI/UX — D1 Global App Shell 討論紀錄 v0.4

> 2026-10-18 (Asia/Taipei) · PRECODE DESIGN PROPOSAL · AWAITING HUMAN FEEDBACK · NOT HUMAN ACCEPTED · NOT CODING AUTHORIZED.
>
> Source-bound base: `9643bfc93a1631154be877536a1c91fc58df84be`.
> Previous reviewed draft: `D1_GLOBAL_APP_SHELL_DISCUSSION.v0.3.md` on this design branch.
> The interactive v0.4 HTML artifact is presented to Human in the corresponding ChatGPT design review; its configuration must be exported/returned for precise layout persistence. At time of this record the new v0.4 HTML **is not committed in this Git branch**; this Markdown is the durable decision log. Existing committed v0.3 HTML remains available for regression/reference.

## Round D1-04 — Human feedback and responses

| Item | Human input | Design v0.4 resolution | Classification |
|---|---|---|---|
| D1-04-01 | Top `目前投資組合` should be `投資組合`; place `目前投資組合` and related functions within dropdown | Main top label changed; submenu: overview UI01, portfolio switch, holdings/groups/allocation UI08, cashflow UI12, risk UI11 | PROPOSAL; UI identity/route source confirmed |
| D1-04-02 | Market submenu by 台股 / 美股 / 加密貨幣, then stocks/bonds/RTF and more | Two-level expandable menus under each geography/market; stocks/bonds/ETF/futures/indices where appropriate; `RTF` preserved as **terminology unclear**, UI candidate displays `ETF（RTF？）`; no supported-trading claim | PROPOSAL / UNVERIFIED asset/venue coverage |
| D1-04-03 | Lab submenu correspond to Lab functions | Group Strategy Builder UI04, Research UI05, Comparison UI06, Bond/Rate Lab UI13; PAPER Simulation UI07 and Library/Deployment UI19 explicitly distinct | SOURCE_CONFIRMED IDs / PROPOSAL grouping |
| D1-04-04 | News: active investments / index and margin-rate indicators / commodities; reference 鉅亨網 and MacroMicro | Menu groups: current holdings, indices, margin financing, yields, volume/volatility, energy/metals/agricultural, macro/central banks | PROPOSAL, news data source/API/license/recency UNVERIFIED |
| D1-04-05 | Performance should split asset class then strategy; vertical money axis in 萬; min day; day/week/biweek/month/quarter/half-year/year | Chart selection asset → strategy; TWD vertical numeric ticks in 萬; seven interactive aggregation ranges; tooltips show dates and demo amounts/differences | PROPOSAL. Historical sampling, currency, return attribution, classification DTO and cut verification UNVERIFIED |
| D1-04-06 | Donut show each class percent and amount around chart, details in tabstrip with overflow arrows | Donut with external callout annotations, six classes and percentages/amounts; detail tabs with previous/next pager, two example subitems | PROPOSAL; exact portfolio grouping and projection/cut UNVERIFIED |
| D1-04-07 | Capital state must show now + day/week/biweek/month amount and percent deltas | Current capital demo value + clickable D/W/BW/M comparison, percentage with pre-period denominator | PROPOSAL; valid capital producer semantics and stable cut FORMAL_REVIEW_REQUIRED if changed |
| D1-04-08 | Default up=red, down=negative and user-adjustable | Interpreted as Taiwan convention `positive/red; negative/green with explicit − sign`; settings menu toggles to global positive/green, negative/red | OWNER_DECISION_REQUIRED on ambiguous phrase `跌為負`, PROPOSAL presentation setting |
| D1-04-09 | Preserve left area configurable like shortcuts and preserve expandable dropdown | Existing portfolio tree retained; separate quick-link list with add/remove/order using up/down and drag, export in JSON | PROPOSAL. Persistent preferences/sync require schema/provider decision |

## Current candidate visual structure (D1 v0.4)
- Top: B3 name; Portfolio / Market / Lab / News dropdown menus; account/environment; hamburger settings, including red/green convention toggle.
- Main: portfolio summary, current capital, strategy KPI, provisional news carousel; asset→strategy filtered performance chart, 7 granularities; allocation donut around-label values and paged asset detail tabs; asset sparkline cards; simplified/list holdings.
- Left: permanent expandable portfolio tree + configurable favorite shortcuts. No reidentification of 19 official UI routes.
- Editing: drag/drop/resizing (+/-), title/content editor, zoom/fullscreen, JSON export; no Git auto-write, no server persistence, no broker actions.
- All numbers/dates/headlines are explicit **synthetic DEMO only**, not realtime, not authoritative financial or news evidence.
- FRESH/STALE/PARTIAL/UNKNOWN toggles are scenarios; when coverage not trustable, hide complete money aggregates/percentages. The UI never infers `0` from `missing`.

## B3 Source boundary / contract candidates

**Verified UI scopes:** UI01 Dashboard (/dashboard, getDashboard/getAccountCapital/getHealth), UI08 Portfolio (/portfolio, getPortfolios/listGroups/queryAttribution/other budget & group operations), UI03 Market, UI02 Chart, UI04 Strategy Builder, UI05 Research, UI06 Comparison, UI07 Simulation, UI11 Risk, UI12 Cash Flow, UI13 Bond/Rate Lab, UI17 Settings and UI19 Library/Deployment. Their identities and API producers stay source-bound to accepted baseline and MA10/PK11.

**New or deepened UX features requiring targeted crosswalk:** menu categorization by venue/type; brokerage support flags; structured portfolio class-strategy hierarchy, historical capital comparisons and return methodology; news/market-indicator provider licensing and storage; keyboard navigation/accessibility; theme/preferences across devices; allocation snapshot/currency/coverage; exact filter semantics and mode (category labels versus persisted model definitions).

**Suggested source checks before implementation:** UI_PAGE_CONTRACTS JSON; API Catalog operation GET/DTO; asset instruments vs listings/venue mapping; MA06 capital/attribution classification; MA03 historical series and adjustment; MA05 macro datasets; permission/granularity snapshot semantics; UI17 preferences persistence; News data provider and commercial license. Avoid inventing API.

## Visual/browser checks (local design fixture, not product qualification)

- Browser: headless Chromium via Playwright; no page errors observed.
- Top market → 台股 expand and child menu works; News macro/credit topic expands.
- Capital weekly comparison shows explicit signed amount and percent.
- Chart asset→strategy options update; day view displays TWD and 萬 y axis; all D/W/BW/M/Q/H/Y selectors are rendered.
- Allocation detail tab pagination switches first/second three asset classes.
- Left quick links can be added and reordered by drag and buttons.
- Settings color mode toggles Taiwan/global semantics.
- UNKNOWN hides aggregate number and allocation donut, not rendered as zero.
- These checks are **prototype interaction tests only**, not MA10 official tests/E2E/Actual evidence.

## Gate and next round

- Status: `D1_V0_4_AWAITING_HUMAN_FEEDBACK` (informal review label only).
- Never equate proposed market/news headings with a new UI20 or true provider endpoints. RTF/ETF abbreviation needs Human confirmation.
- Continue revising D1 until Human explicitly states no further design adjustments.
- Any authoritative capital, market/source classification, cross-device layout persistence, news licensed feed, DTO/API changes must be routed to the appropriate independent architecture review before Coding.
- D1 Design Acceptance ≠ Coding Authorization. No production source files, commits to accepted baseline/main/master, runtime authority, WO, Grant, Broker I/O.
