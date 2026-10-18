# B3 V1 UI/UX — D1 v0.3 Screenshot-based Review and Prototype

> PRECODE DESIGN CANDIDATE, NOT HUMAN ACCEPTED. 2026-10-18 (Asia/Taipei).

## Source and traceability
- Fixed accepted B3 design source commit: `9643bfc93a1631154be877536a1c91fc58df84be`.
- Earlier D1 record: `docs/design/b3_v1_ui_precode/D1_GLOBAL_APP_SHELL_DISCUSSION.v0.2.md`.
- This version's interactive standalone HTML: `docs/design/b3_v1_ui_precode/prototypes/B3_V1_D1_AppShell_Interactive_v0_3.html`.
- Original Human composite reference screenshot SHA256: `8334a28b7a497f5a81337c54085b6dba4a499ef2ba7334599d7500ef48b31edb` (provided via conversation, not included/reproduced as a Git binary).
- HTML prototype SHA256: `947141118574056094e226a2c7e830bb6f52205ed5b5eb8027ad0d0d57465a21` (UTF-8 bytes).
- Source-verified page IDs stay stable: UI01 Dashboard (`/dashboard`), UI08 Portfolio (`/portfolio`), UI02 Chart (`/chart`), UI03 Market (`/market`), UI04 Strategy Builder, UI05 Research, UI06 Comparison, UI13 Bond/Rate Lab, UI17 Settings, UI18 Audit.
- MA10-U01 shared shell + MA10-U02 market/dashboard/portfolio/cash. PK11 not authorized for implementation.

## Human input, requested changes, and disposition
| ID | Human input | D1 v0.3 resolution | Design category |
|---|---|---|---|
| D1-03-01 | Use third dashboard visual as base, replace screenshot red-framed areas with supplied left Portfolio list, central trend/line chart, right class summary and bottom holdings list | 12-col grid with narrow left Portfolio tree, top summary row, center wide chart + allocation, bottom assets and holdings | PROPOSAL |
| D1-03-02 | Assets must show both quantity/value changes and synchronized line trend, mouse hover with value changes | Each of 6 asset tiles has synthetic sparkline, hover gives dated amount and period delta; main chart has time/amount hover, shared demo month domain | PROPOSAL; true shared producer/snapshot binding UNVERIFIED |
| D1-03-03 | Bottom section switch simple/list mode via icon | `▦` and `☷` switch 6 demo positions between cards/list | PROPOSAL |
| D1-03-04 | Top Portfolio, Market, Lab, News must be dropdowns or navigable menus | Dropdowns with B3 official UI ID route previews. No fake navigation to unbuilt pages. News clearly provisional | SOURCE_CONFIRMED IDs / PROPOSAL UX |
| D1-03-05 | Main row: overview, capital, strategy performance and small rotating investing-news pane | Four summary tiles with clickable news prev/next | PROPOSAL; news source/license/API UNVERIFIED |
| D1-03-06 | Continue live layout discussion, drag/edit/+/-, enlarged/fullscreen and Git record | 8 editable/reorderable modules, 3/4/6/8/9/12-col widths, preset heights, change module content, maximize, global fullscreen request, export versioned JSON | PROPOSAL; no automatic Git writes from browser |

## Initial layout

- Global B3 product name and top dropdowns: Current Portfolio → UI01/UI08/UI12/UI11; Market → UI03/UI02; Lab → UI04/UI05/UI06/UI13; News → new proposed UX entry (not a 20th UI Identity).
- Right: LAB DEMO, sample account dropdown (no real change), hamburger menu (layout, add, fullscreen, export/reset, UI17, UI18, help).
- Trust strip persists with DEMO/Source/Cut/Quality and separate selectable FRESH/PARTIAL/STALE/UNKNOWN visual scenarios.
- Left: Dashboard, Portfolio with multiple named entries and Add New design stub, Screener, Watchlist/Chart, News, Strategy, Orders, Automation.
- Default 8 modules: D01 Overview (3/12); D02 Capital (3/12); D03 Strategy Performance (3/12); D04 News (3/12); D05 Trend + bars (8/12); D06 Asset donut/summary (4/12); D07 Six asset cards with sparkline (12/12); D08 Holdings table/list toggle (12/12).
- Asset/Strategy/Horizon/Period filter bar is visual-only.
- All financial values are deliberately synthetic, non-real holdings, non-real news. When partial/stale/unknown, metrics and aggregate trend/donut hide numeric claims rather than treating missing as zero. An FRESH UI toggle cannot prove real freshness.

## Browser checks
Using Chromium Playwright on standalone HTML source rendered with set_content: 8 modules / 6 asset cards; top News dropdown opens; news carousel changes; simple view displays 6 cards; list view 6 rows; card + changes width 3→4; edit changes title; UNKNOWN hides KPI and sparkline; return FRESH restores 6 sparklines; no page JS errors. Standalone file navigation was blocked by browser security policy in testing environment, therefore rendered via set_content; browser open via local downloaded HTML may differ. Preview screenshot available as ChatGPT output artifact, not committed binary.

## Further review topics before Human D1 Acceptance
1. Does the Portfolio side tree need hierarchy: account → portfolio → strategy group → positions? Clarify if these are B3 resource entities or navigation-only bookmarks.
2. Visual alignment of asset tiles, stock screener and watchlist, responsive settings, and whether Bottom Dock is optional for the home page.
3. Chart and tile hover should synchronize source cut, cursor, currency/time-zone and benchmark/normalization policies. Need cross-source DTO binding and no invented return definitions.
4. New News function: provider/feed rights, watchlist-symbol relevance, stale provenance, licensing, link destinations, API ownership; **do not** assume B3 has a news API, and don't introduce UI20.
5. Persistent layout preference, dashboard card registry and drag drop save/sync need future contract, possibly formal design review if server persistence added.
6. User-supplied JSON exports are feedback input, to be reviewed and committed explicitly; HTML cannot commit Git automatically, and no account permission/authority can be derived from mock state.

## Review and governance
- `D1 v0.3` = DESIGN_PROPOSAL_NOT_ACCEPTED / AWAITING_HUMAN_FEEDBACK (informal review labels only).
- No Coding, runtime proof, BFF client, order/capital authority, Product React implementation, official WO/Grant, or main/master modifications.
- This Git branch houses discussion documents and a standalone concept HTML solely for design collaboration. Human Design Acceptance is separate from Engineering authorization.
- Keep D1 open until Human confirms no further changes; append next discussion revision instead of replacing history.
