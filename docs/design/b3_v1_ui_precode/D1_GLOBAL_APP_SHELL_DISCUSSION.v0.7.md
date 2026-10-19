# B3 V1 / D1 Global App Shell — Design Review v0.7

**Record class:** UI/UX PRE-CODING DESIGN DRAFT ONLY; `PROPOSAL`, not Human-accepted. 2026-10-19 (Asia/Taipei).

## Fixed baseline and continuation
- Accepted B3 V1 source/pin: `9643bfc93a1631154be877536a1c91fc58df84be`; preserve 19 UI permanent identities, MA10-U01..U06, PK11 and source / authority contracts.
- Prior revisions in this design branch: `D1_GLOBAL_APP_SHELL_DISCUSSION.v0.2.md` through `v0.6.md`. This document is an append-only new review revision, not a replacement of prior records.
- Design-only implementation artifact: `docs/design/b3_v1_ui_precode/prototypes/B3_V1_D1_AppShell_Interactive_v0_7.html`, UTF-8 SHA256 `ce21b5d1ba758c45e58bd25264a2f4ec565167021c9bc28ae47ee82f168f4ec9`.
- Human supplied three reference screenshots on 2026-10-19: previous sidebar with red markings; Adobe palette-wheel interaction example; top modules with ‹ › controls. They serve as feedback/visual reference, not adopted product source or third-party copy.
- No product coding, no WO / Grant, no Repository runtime modifications, no merge to authoritative branch, and no formal architecture acceptance by this design commit.

## Human request intake and disposition

| ID | Human request | Proposed v0.7 behavior | Status / source boundary |
|---|---|---|---|
| D1-07-01 | Left side all user-selected shortcuts, one Edit at bottom; selected links grouped by functional class, no mixing with duplicated fixed navigation | Entire fixed sidebar and portfolio tree removed visually. Left shows selected entries grouped by Portfolio, Market/Chart, Research/Lab, Trading/Risk, Engineering/Audit, Settings. Category empty → not shown. Single bottom Edit opens dialog with 19 official pages plus hierarchical per-page subfeatures; selected gets check/color; move/drop, spacing +/-, Cancel vs Save | PROPOSAL; formal UI ID mapping SOURCE_CONFIRMED; subfeature anchors DESIGN_CANDIDATE_NOT_API_ID |
| D1-07-02 | Merge font/size/layout/visibility into `面板設定`; Adobe-like palette interaction, full-palette preset and single role color, preview/default/apply | Hamburger → 面板設定: palette wheel with harmony modes, five theme presets, 9 editable role colors; tabbed Fonts (Arial Latin, Microsoft JhengHei Chinese, per-category sizes); Display (titles/notes, round corners, gain/loss palette). Live preview; Cancel restores prior theme+fonts, Apply retains in this tab; Export JSON for Git persistence | PROPOSAL; Adobe screenshots are inspiration only, no copied code/assets. Server/cloud persistence and DesignToken full coverage UNVERIFIED |
| D1-07-03 | If module has multiple related records automatically provide ‹ › and change actual content; e.g. four portfolios while a card shows one | Generic header pager appears for multiple-record card types. 4 distinct **synthetic** Portfolio demo datasets change overview amount, return, capital amount and period plot, strategy figures, chart trend, asset classification amounts and holdings amounts; news uses 3 mock entries. Selection per module, no fabricated backend query. Content link retains official UI/page subfeature target | PROPOSAL; actual multiple portfolio/Account resource DTO, pagination and cross-card synchronization UNVERIFIED |
| D1-07-04 | Can multiple monitors/pages/accounts be open concurrently? | Browser can open multiple windows/tabs and OS can place them on different monitors; `⊞ 新視窗` is design demonstration only (popup may be blocked), not real B3 context/session capability. Recommend pinning exact account/environment/portfolio/resource context per window/workspace; do not use mutable browser-global account for transactional commands. Separate identities may need browser profiles or server session isolation | TECHNOLOGY_FEASIBLE / B3_ACTUAL_UNVERIFIED; FORMAL_REVIEW_REQUIRED for Account/Permission/Persistence/Isolation semantics |
| D1-07-05 | Identify missing D1 design discussions, clarify Dashboard/home vs entire shell | See Design Checklist below and proposed gates; do not prematurely close D1 | OWNER_DECISION_REQUIRED for preferences only after visual walkthrough |

## Source-bound UI Contract consequences

- `UI01 Dashboard` (`/dashboard`; getDashboard, getHealth, getAccountCapital) owns current-home summaries and health, not UI08's capital/portfolio mutation commands.
- `UI08 Portfolio` (`/portfolio`; getPortfolios/listGroups/queryAttribution/...): portfolio selection/drilldown. UI01 cards may link to it; do not transfer authoritative ownership.
- `UI17 Settings` may host user visual preferences; **not** proof that a preferences API/DTO, color sharing, or remote persistence exists.
- `UI02` Chart, `UI03` Market, `UI04` Strategy, `UI05` Research, `UI09` Orders, `UI16` Progress, `UI18` Audit are represented in a shared display-only Feature Registry.
- `NEWS` is not a verified 20th official UI identity; production feed, licensing, source vintage, news-to-instrument linking and event freshness need bounded source/contract review.
- Multi-data pager **must bind to actual snapshot / cursor / resource scope** on implementation; currently all synthetic. It must not combine cross-account or cross-cut sums in one authoritative result.
- LAB/PAPER/LIVE account switching must invalidate appropriately scoped data, query resource permissions, clear unsafe order drafts, and preserve server-authoritative receipt lookups for pending/unknown commands.
- UI display preferences cannot hide environment / source / quality / UNKNOWN / redactions / permission warnings, or override risk semantics.

## Browser design checks (not formal QA)
- Chromium headless preview was rendered via `set_content` because file:// navigation is blocked in the sandbox. 1520x970 visual screenshot generated separately.
- 8 modules present, 4 categorized shortcut groups and 6 selected shortcuts by default.
- Overview module ‹ ›: demo value changed `NT$ 3.50M` → `NT$ 2.59M`; corresponding portfolio label changed, not label-only.
- Capital module ‹ ›: amount changed to `NT$ 60.7萬`; asset module ‹ › changed first card amount to `NT$ 770,687`; News changed its title to next candidate article.
- Shortcut modal lists 6 categories and 19 official page sections; Cancel discards selection; Save increases selected links from 6 to 7 and shows new group, without changing official identities.
- Panel theme Jade preview changed `--bg` to `#0c1715`, Cancel restored `#0a101a`; Apply Plum changed to `#140f1a`; grouped font/display changes were exercised.
- UNKNOWN summary amount became `—`; no uncaught JavaScript page error in browser test.
- Known scope: not browser E2E against B3; no real API, server account switching, Broker, data license, persistence, cross-window synchronization, formal accessibility/contrast test, multi-monitor OS test.

## D1 completeness checklist / next design review (not yet approved)

| Topic | Why it matters | Proposed review strategy | Status |
|---|---|---|---|
| D1-G01 Home default | Account A/B, last-open vs pinned portfolio, UI01 vs UI08 | Default UI01 investment overview, preserve last UI08 navigation as a separate view | OWNER_DECISION_REQUIRED |
| D1-G02 Multiple portfolio card data | Independent ‹ › or lock all widgets to global portfolio? | Offer modes: `跟隨主選組合` (default) / `單卡釘選` (optional). Need snapshot/cut binding | OWNER_DECISION_REQUIRED, underlying Source/DTO UNVERIFIED |
| D1-G03 Multiple monitors / accounts | Cross-window account bleed, permission confusion, stale drafts | Pinned workspace context `env, account, portfolio, scope`; no accidental mutation on UI switch; session isolation formal review | FORMAL_REVIEW_REQUIRED |
| D1-G04 Portfolio summary metrics | Unrealized/realized PnL, equity, purchasing power, cash, strategy returns, FX | Metric definition sheet by Owner and producer, denomination, as-of/cut/coverage, source; no frontend authority recompute | UNVERIFIED / possible FORMAL_REVIEW_REQUIRED |
| D1-G05 Dashboard cards vs Portfolio details | Duplicate UI01/UI08 interactions | Show bounded summary, click to UI08; no UI08 command in UI01 without contract | SOURCE_CONFIRMED principle |
| D1-G06 Widget taxonomy and links | Adding new modules/subfeatures not in 19 UI | Shared Feature Registry and card registry with stable IDs, role/availability/version; UI ID unaffected | PROPOSAL |
| D1-G07 Layout/palette persistence | Local vs account vs device vs multi-monitor; reset/import/version conflicts | Separate Visual Preferences from authoritative account state; local prototype JSON export only; durable schema needs review | UNVERIFIED / FORMAL_REVIEW_REQUIRED if backend |
| D1-G08 Startup loading/stale/error | Avoid empty=zero, stale=realtime, unknown=failed order | Review full MA10 state matrix (initial, verified-empty, partial, stale, offline, permission-denied, conflict 409, UNKNOWN, pending receipts) | SOURCE_CONFIRMED obligations |
| D1-G09 Context switching | LAB/PAPER/LIVE + multiple identities | Explicit text and confirmation for scope, requery, no stale order drafts, server gate | FORMAL_REVIEW_REQUIRED for new contract |
| D1-G10 Navigation discoverability | User may remove all shortcuts | Persistent top menu remains global access to all 19 pages; show empty-shortcut Edit entry; keyboard and screen reader checks | PROPOSAL |
| D1-G11 Responsive and ultrawide | Multi-monitor screen size and small display | 12-col desktop, ultrawide split/breakpoints, narrow stacked view, font scaling and density; test overflow and focus order | PROPOSAL |
| D1-G12 Design accessibility | Theme picker may result in unreadable red/green/labels | WCAG contrast and non-color indicators, keyboard switch and high-contrast fallback; future automated checks | UNVERIFIED; DESIGN_REVIEW_REQUIRED |
| D1-G13 Dashboard startup and recovery | Network reconnect, snapshots diverge by card | Each card records Source/Cut/Quality and explicit resnapshot; avoid cross-snapshot aggregate falsehood | SOURCE_CONFIRMED MA10 principles |
| D1-G14 Trading gestures | Single-click accidental order from dashboard | Dashboard actions remain view/drilldown or non-authoritative proposals; any trade/risk requires explicit B3 authorization workflow | SOURCE_CONFIRMED safety |
| D1-G15 Audit evidence | Exact operation receipt, context and actor | UI18 receives audit trace, operation IDs and coverage; no faux No order | SOURCE_CONFIRMED scope; exact binding to verify |

## D1 decision continuity

1. `D1 v0.7`: PROPOSAL / AWAITING_HUMAN_FEEDBACK (informal discussion labels, not formal machine states).
2. Continue D1 revisions and evaluate Human screenshots with feasible/difficult/alternative decision outcomes. Only close when Human explicitly says no more modifications; D2 is not authorized by this draft.
3. Design record in Git is not Human UI Acceptance; Human Acceptance not Coding Authorization.
4. At pre-Coding assembly, reconsolidate all approved UI01..UI19 and MA10-U01..U06, API DTO, 64 finding crosswalk, source gaps, Human decisions and independent review concerns into `B3_V1_UI_UX_DESIGN_REVIEW_PACKAGE`.
