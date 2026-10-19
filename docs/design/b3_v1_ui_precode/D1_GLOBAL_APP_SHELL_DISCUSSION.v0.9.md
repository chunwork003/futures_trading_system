# B3 V1 — D1 Global App Shell / Investment Overview: Owner Feedback Review v0.9

- **Date**: 2026-10-19 (Asia/Taipei).
- **Classification**: `PRECODE_UI_DESIGN_CANDIDATE`, `OWNER_FEEDBACK_PENDING`; not an official machine state, not Human Design Acceptance, and not a Coding Grant.
- **Accepted B3 source pinned**: `9643bfc93a1631154be877536a1c91fc58df84be`. Preserve all 19 official UI IDs, their API/DTO boundaries and MA10-U01..U06 dependencies.
- **Source documents**: `docs/architecture/multi_asset/10_WEB_UI_API.md`, PK11 engineering README, `docs/program/publication/B3-V1-ACCEPTED-BASELINE-PUBLICATION/engineering/contracts/ui/UI01.json` and `UI08.json`.
- **Prior discussion record**: `docs/design/b3_v1_ui_precode/D1_GLOBAL_APP_SHELL_DISCUSSION.v0.8.md`; prior records retained.
- **Versioned standalone HTML prototype (design-only)**: `docs/design/b3_v1_ui_precode/prototypes/B3_V1_D1_AppShell_Interactive_v0_9.html`.
- **Container-tested prototype SHA256 (raw UTF-8)**: `519a4b7ef2222f91dd375538e8b7df63c38410453747bc51fb0ffb7930513286`; server-side file-read representation may normalize two characters of newlines before Git upload. Pin to Git blob SHA for exact repository bytes.
- **Human reference**: three annotated screenshots from 2026-10-19 showing scrollbar in cash, crowded top toolbar, overlarge shortcut editor and FinLab-like desired compact sidebar. Only design references, not copies of external source/code.
- **No** product React/ASP.NET/Python implementation, broker I/O, migration, PR merge, WO/Grant or formal Architecture amendment.

## Six numbered Human requests, source mapping and implementation dispositions

| ID | Human correction | D1 v0.9 visual design resolution | Source / decision classification |
|---|---|---|---|
| D1-09-01 | Fixed module means all standard records fully visible with no interior vertical scrollbar, e.g. six records fill same standard area; fewer retain size, more paginate with ‹ › | Layout now has distinct per-type fixed presentation capacity; asset card grid **6 cards (3×2)** in stable-height module; holdings list **6 table rows**, + two synthetic extra records demonstrate second page and **4 reserved blank rows**; one-stock category shows 1 card and 5 placeholders; changes/page turns preserve outer height. All 8 tested desktop widgets have zero body vertical overflow. Complex chart/donut need a larger stable baseline height, not a 150px card with hidden content. | PROPOSAL; verified visual test only. Actual paged query must respect snapshot/cursor/cut + permissions; FULL responsive and custom-font density checks remain |
| D1-09-02 | Remove "更多". Separate formal 交易 only if useful; nonessential entries shouldn't clutter top. News is last primary top category; search nearest account | Top order `投資組合 → 市場 → 實驗室 → 工具 → 交易 → 新聞（候選）`; no More. Search moved into right-side header near DEMO account; Settings menu contains secondary Engineering links; all 19 pages still searchable in global Feature Registry. Trading includes UI07 PAPER Simulation, UI09 Orders, UI10 Positions, UI11 Risk, but **navigation does not grant transaction authority**. | PROPOSAL. SOURCE_CONFIRMED UI IDs, Risk/Order authority boundaries |
| D1-09-03 | Left nav category themed icons, compact translucent selected-shortcut flyout proportional to number of selected links; no inline editing; search only in editing modal, Settings button at bottom; sidebar sticks when main scrolls | SVG icons drawn for Portfolio, Market, Lab, Trading and Engineering. Render **only categories with selected shortcuts**, not blank navigation groups. Selected items alone appear in semi-transparent blur flyout; two items render approx **157px**, no editor there. No duplicate search icon. Only ⚙ settings at footer opens existing Settings hub/shortcut manager, with search inside modal. Rail stays sticky at actual measured header height, and can internally scroll if icons eventually overflow; expanded mode remains an optional preference. | PROPOSAL. Full keyboard/focus/contrast/mobile/long label checks UNVERIFIED |
| D1-09-04 | Default module sync follows main portfolio, allow individually pinned asset data | Preserve `follow` as default and per-card `📌` override, clearly labelled in each card; no silent cross-account cash/risk aggregation. | OWNER design direction recorded, **not** final D1 acceptance. Detailed resource permissions/cut formal review if contract changes |
| D1-09-05 | Multiple monitors and research scheduling as recommended; defer to related page discussion | Keep candidate account/window context isolation in MA10-U01/U06 + UI01/UI08 and Auth policy review, and research scheduler in UI05 Research with UI16 governance boundary; not built into D1 beyond concept launcher/settings. | FORMAL_REVIEW_REQUIRED for new account/session/window-persistence/scheduler APIs, dispatch/risk/execution semantics |
| D1-09-06 | Adjust then check other D1 issues worth discussing | See focused checklist below. D1 continues, no new unrelated architecture survey. | OWNER_DECISION_REQUIRED only at meaningful interface gates |

## Effective module behavior and safety

- `UI01` remains source-owned Dashboard: `getDashboard`, `getAccountCapital`, `getHealth`. `UI08` remains Portfolio ownership for groups/positions/attribution; an UI01 card linking UI08 does not transfer mutation authority.
- Demo holdings fixture has 8 synthetic records (including two extra purely to visually prove pagination). First page shows six, second page has two actual mock records and four blank reserved slots.
- Asset grid has six categories. Tab/filter may leave fewer categories; blank slots preserve module dimensions; **display filtering does not change authoritative total equity**.
- Unknown / Stale / Partial are preserved as distinct visible B3 semantics; no demo screen is genuine market / cash / broker evidence.
- Layout card size edits are available in Settings `調整版型` only. When user intentionally reduces a module below the validated standard capacity, prototype may clip: formal design needs min-height and density validation before approval. This is **UNVERIFIED** in the arbitrary customizable case.
- Fixed-height strategy is a **presentation capacity** with consistent line-height/readability, not permanent hard-coded pixel heights for all viewport dimensions or text scales. Responsive breakpoints need a separate tested profile.
- Sidebar flyout and top navigation are not granted authentication or order privileges. Permission scope is server authoritative and should hide/disable commands appropriately; state/cut/unknown semantics are unavoidable.
- The Tools and News entries retain proposed contract gaps (provider/entitlement/licensing), do not create UI20.
- Legacy app Shell HTML in this branch is a standalone visual review prototype only; not a formal app runtime.

## Browser verification (local HTML, Chromium headless at 1510×980)

- All 8 modules rendered. `#designerLegacyToolbar` hidden in ordinary view.
- Top nav order exactly `投資組合 / 市場 / 實驗室 / 工具 / 交易 / 新聞`, `更多` removed; Trading and News dropdowns open. Global search adjacent to account.
- Portfolio shortcut flyout has **2 entries**, height **157px**, no editor / no secondary search icon. Settings is at bottom.
- Module vertical content scroll overflow (scrollHeight - clientHeight) is **zero for all eight** at tested desktop viewport; rendering preview is not evidence for untested devices or density.
- Assets initial visible count **6**, STOCK category **1** visible + **5** placeholders, outer card stays **520px** when changing tabs.
- Holdings fixture total **8**, page 1 **6**, page 2 **2 + 4 reserved blank rows**, outer height **490px** unchanged; pager ‹ › works.
- UNKNOWN scenario preserves unverified placeholder rather than falsely showing computed monetary values.
- No JavaScript page errors in these checks. Manual multi-account, cross-window persistence, actual source data, production News, and formal E2E were not exercised.
- Preview files in ChatGPT working environment are reference attachments, not part of B3 accepted baseline.

## Focused open D1 issues / proposed next review gate

1. **Fixed capacity vs user font/width changes**: choose minimum module heights per display density and viewport breakpoint. Recommend auto-detect design overflow, propose safe enlarge/reflow in layout editor; never silently clip or scroll finance values. `UNVERIFIED`.
2. **Shortcut flyout behavior**: single-click to open/click again to close, Esc/focus restoration, pointer outside closes, keyboard/tab accessibility and screen-reader labels; fixed-height only for rail, variable height for submenu. `PROPOSAL`.
3. **Navigation role policy**: should trading group appear as read-only/locked if user lacks OPERATOR permission, or hide entirely? Recommended show read-only monitoring page links but hide/disable prohibited actions, with scoped resource permissions. Actual Auth contract needed. `OWNER_DECISION_REQUIRED / FORMAL_REVIEW_REQUIRED` if new semantics.
4. **Card follows current Portfolio**: chosen default follow main with pin option; specify pinned label, behavior when switching Account/Environment, and prohibit persistence of unauthorized pin. `PROPOSAL`.
5. **Saved layouts and workspace startup**: distinguish user-global vs device vs window vs account scope and revision conflicts, review before formal design handoff. `FORMAL_REVIEW_REQUIRED` for new persistence API.
6. **Precise financial units, cut and refresh**: typography may mute optional currency but essential monetary scale / cross-currency / trade confirmation cannot be ambiguous or hidden. No real-time claim from demo. `SOURCE_CONFIRMED` principle, detailed DTO mapping outstanding.
7. **Small viewport and ultrawide acceptance**: test 1920/2560, 1366, tablet and minimum 1024 and enlarged fonts; stable card capacities might change by responsive profile, not per-record count. `UNVERIFIED`.

## Gate

- `D1 v0.9`: DESIGN CANDIDATE ONLY, AWAITING_HUMAN_FEEDBACK.
- Human should review file visually, provide screenshots/desired corrections. No D1 Human Design Acceptance until explicit confirmation of no more revisions.
- Any architecture, API, DTO, capital/risk/trading rights or cross-window isolation change requires separate accepted-source/Reviewer decision. Design saved in Git is not formal approval or Coding Authorization.
- Later `B3_V1_UI_UX_DESIGN_REVIEW_PACKAGE` must consolidate all v0.x D1 decisions with permanent UI01–UI19 and MA10 U01–U06 crosswalk, 64 findings and outstanding contracts.
