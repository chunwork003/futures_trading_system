# B3 V1 UI/UX — D1 Global App Shell 討論紀錄 v0.2

- Record type: **PRECODE_UI_DESIGN_DISCUSSION_CANDIDATE**, non-authoritative; **not Human accepted**.
- Date: 2026-10-17 (Asia/Taipei).
- Fixed accepted source commit: `9643bfc93a1631154be877536a1c91fc58df84be`.
- Git design branch: `design/b3-v1-ui-precode-review-20261017`.
- Scope: `D1 / Global App Shell + portfolio-start Dashboard presentation`; design-only, no product React/ASP.NET/Python modification, no B3 contract amendment, no WO/Grant or runtime authorization.
- Source anchors: `docs/architecture/multi_asset/10_WEB_UI_API.md`; `docs/program/publication/B3-V1-ACCEPTED-BASELINE-PUBLICATION/engineering/contracts/ui/UI01.json`, `UI08.json`; `docs/program/publication/B3-V1-ACCEPTED-BASELINE-PUBLICATION/engineering/packages/PK11/README.md`.
- Status vocabulary: `SOURCE_CONFIRMED`, `PROPOSAL`, `UNVERIFIED`, `OWNER_DECISION_REQUIRED`, `FORMAL_REVIEW_REQUIRED`. These are review labels, **not formal machine governance statuses**.

## Human feedback intake — round D1-02

1. All page discussions/iterations/decisions must be versioned in Git; GPT conversation and memory cannot be the authority. A final consolidation occurs before Coding.
2. For every new UI feature: test whether it is already planned, whether a new feature has an owner/API, where it belongs, downstream expansion, interactive links and ramifications. Evaluate alternatives; do not silently add a feature into accepted contracts.
3. Maintain `UI01..UI19` permanent IDs, source mapping, issue/change register and Coding handoff references.
4. Provide editable prototype: module position, size, scope, contents, `edit/replace/+/-`, direct drag-and-drop, instant preview.
5. Review every new image or owner suggestion for feasibility and improvements. Log proposals, distinguish difficult/impossible features and alternatives. Remain on D1 until Human says no further adjustments and explicitly accepts; unrelated work may continue.
6. Provide enlarge/fullscreen workspace capability.
7. D1 header: B3 product/system title; `目前投資組合` / `市場` / `實驗室` / `新聞` tabs; account at right; `≡` menu with provisional settings.
8. Start at current-portfolio overview, with filters by asset class, trade horizon and strategy, plus strategy, performance, capital and risk summaries. Deliver first revised interactive draft before requesting final decision.

## Existing vs proposed feature mapping

| Design item | B3 anchor | Status / implementation boundary |
|---|---|---|
| Shared Desktop 12-column navigation, context/header, main, right drawer | MA10 / MA10-U01 | SOURCE_CONFIRMED layout semantic. Exact visual arrangement below is PROPOSAL |
| Start/home investment overview | `UI01 Dashboard`, route `/dashboard`; `getDashboard`, `getAccountCapital`, `getHealth` | SOURCE_CONFIRMED page / operations; PROPOSAL content grouping |
| Portfolio drilldown, groups, allocation, attribution, capital/budget | `UI08 Portfolio`, route `/portfolio`; `getPortfolios`, `listGroups`, `queryAttribution`, `previewBudgetAllocation`, `confirmBudgetAllocation` | SOURCE_CONFIRMED separate page. Do not rename/reassign ID or imply UI01 owns UI08 commands |
| Market & Chart top navigation | `UI03 Market`, `UI02 Chart` | SOURCE_CONFIRMED pages, PROPOSAL global navigation presentation |
| Lab top navigation | `UI04 Strategy Builder`, `UI05 Research`, `UI06 Comparison`, `UI13 Bond/Rate Lab` | SOURCE_CONFIRMED pages, PROPOSAL grouping |
| News global navigation | no directly evidenced distinct UI among 19 page identities | PROPOSAL / UNVERIFIED: content source, entitlement, API, news licensing and security require discovery; keep placeholder and formal review if new contract |
| Trading horizon / asset / strategy classification filters | UI08 group & market metadata concepts | PROPOSAL; verify typed DTO/filter semantics, cut/cursor behavior and classification authority |
| Strategy-specific ROI and capital figures on home page | UI01 dashboard and UI08 portfolio/research outputs | PROPOSAL; verify trusted producer, PnL definition, currency, denominator, measurement period, snapshot/cut/quality; unknown cannot be displayed as zero |
| Editable/reorderable/resizable cards, theme, preferences | MA10-U01 shared layout | PROPOSAL; current design tool is local-only. Any server/cloud sync, schema, persistence, multiple device semantics requires Source/DTO review |
| Right `≡` menu | UI17 Settings, UI18 Audit; shared shell | PROPOSAL. Options: layout/edit, density/theme, export draft, reset, Settings, Audit, help, shortcut, version. Each option needs future permission/route binding |
| Account / LAB/PAPER/LIVE switch | MA10 source permission + environment context | SOURCE_CONFIRMED requirements; prototype uses only hardcoded DEMO and cannot change authoritative account |
| Data quality strip / Unknown/Stale/Partial | MA10 read-model contract | SOURCE_CONFIRMED safety semantics. Prototype uses simulated toggles, not real data evidence |
| Fullscreen / module enlargement | visual review only | PROPOSAL; local HTML supports fullscreen request subject to browser restrictions, F11 fallback |
| Drag/drop, +/- width, edit/replace card type, add/remove, JSON export | design prototype interactions only | PROPOSAL; UI arrangement edits are not automatically written to Git; User submits JSON/feedback, assistant will reconcile and commit candidate design revision |

## D1 proposed layout v0.2

Top row: B3 platform name | current portfolio / market / lab / news (news provisional) | LAB/PAPER/LIVE text | account | hamburger settings menu.

Trust row (unhideable): `DEMO/Snapshot/Source/Cut/Quality` and independently shown `FRESH/PARTIAL/STALE/UNKNOWN`; browser connection is not authority.

Main: 12-column modules + asset/horizon/strategy/time filters, sidebar linking UI01, UI08, UI12, UI11 plus shortcuts; right inspector; optional Bottom Dock.

Initial candidate cards: 1) investment summary (8 columns); 2) capital (4); 3) strategy performance (8); 4) allocation (4); 5) performance chart (8); 6) risk and data quality (4). All numbers in prototype are synthetic and **must never** be represented as actual holdings, balances, orders or investment advice. Responsive layout stacks on narrow viewports.

Design-only interaction in standalone HTML: draggable reordering, toolbar move arrows, width increase/decrease, card edit (title/type/width/height/notes), add/remove, per-card zoom, global fullscreen, top navigation/demo selector, provisional hamburger menu, JSON export. JS/CSS/HTML prototype is not product coding, not committed as application runtime. Exact local artifact name `B3_V1_D1_AppShell_Interactive_v0_2.html`; SHA256 `a41a9f5a9f91a2736c4230ce1a75511b2f78d6472f9ae0d04c21852b84294dce`.

## Safety and counterexamples

- `LAB→PAPER/LIVE` cannot be color-only; re-query resource authorization, reset stale order drafts and rebind scoped subjects. No trading permission from frontend state.
- `STALE/PARTIAL/UNKNOWN` prevents unsupported aggregate return and cash assertions. Mock values and FRESH toggle are purely presentation fixtures; not genuine provenance.
- Cross-market ambiguous symbol search must resolve instrument/listing; no alias-only order context.
- Switching UI shell/workspace must not discard pending command receipts or mark an unknown order as rejected/no effect.
- Dashboard is a summary, Portfolio manages groups/holdings. UI01 does not receive UI08's authoritative mutation API merely due to shared visual cards.

## Feature-review queue (not approved)

| ID | Feature / gap | Initial recommendation | Review |
|---|---|---|---|
| D1-F01 | News global tab with trusted source/cut/link | Placeholder in D1; trace actual external/news API before detailed UX | UNVERIFIED; FORMAL_REVIEW_REQUIRED if new API/rights |
| D1-F02 | Cross-workspace persistent module positions, custom layouts | Browser-only discussion prototype first; design durable preference DTO separately | OWNER_DECISION_REQUIRED; FORMAL_REVIEW_REQUIRED if new persistence |
| D1-F03 | Asset/horizon/strategy filter authority and pagination | Determine producer and typed filter fields before designing Query semantics | UNVERIFIED |
| D1-F04 | Performance definitions, long/short strategy accounting and portfolio cash display | Use separate cards with Source/Cut/Quality and no invented sums | UNVERIFIED, potential capital/authority FORMAL_REVIEW_REQUIRED |
| D1-F05 | Hamburger account/preferences/accessibility/shortcut roles | Scope menu per permission rather than global admin boolean | PROPOSAL |
| D1-F06 | Fullscreen/card resize/drag/edit with export JSON | Design-only interactions; explicit export→Human feedback→Git record | PROPOSAL |

## Design review gate & history

- `D1-V0.1`: two proposed layouts from prior conversation; **not Human-accepted**.
- `D1-V0.2`: incorporates feedback in this record. `AWAITING_HUMAN_FEEDBACK` (review label).
- Candidate recommendation: start `UI01` with overview, link to `UI08` management. Keep all 19 official IDs unchanged; use TradingView-like flexible chart focus only when chart is discussed.
- Human review checkpoint: changes to top tab hierarchy, account menu, initial cards, filters, resizing/dragging ergonomics and full-screen. **Do not mark accepted or proceed to D2 detailed visual design until Human explicitly confirms that D1 needs no further changes.**
- After each round, append a dated delta and change records in Git design branch; no source contract writes, no branch merge into authoritative baseline, no runtime authorization.
- Before implementation, consolidate `B3_V1_UI_UX_DESIGN_REVIEW_PACKAGE` and formal crosswalk for UI01–UI19, MA10-U01–U06, API/DTO, outstanding findings; Human design approval is not Coding Grant.
