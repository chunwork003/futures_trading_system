# B3 V1 — D1 Global App Shell v0.5
**Record:** PRECODE_DESIGN_CANDIDATE / NOT HUMAN ACCEPTED / NO CODING AUTHORIZATION
**Basis:** accepted B3 source commit `9643bfc93a1631154be877536a1c91fc58df84be`
**Design branch:** `design/b3-v1-ui-precode-review-20261017`
**Previous record:** `D1_GLOBAL_APP_SHELL_DISCUSSION.v0.4.md`
**Interactive prototype:** `prototypes/B3_V1_D1_AppShell_Interactive_v0_5.html`
**Prototype SHA256 (UTF-8):** `7e7b0175a74b9362589bbbe4e7acbafceaf5a113732cf44208116b4470d158f4`

## Human feedback intake / round v0.5
1. Settings to offer typography management, grouped by region and supporting font family and size. English default Arial; Traditional Chinese default Microsoft JhengHei.
2. Sidebar shortcut editing only after dedicated icon is clicked; open separate movable/resizable dialog. "+" opens full page & subfeature catalog, selection indicated with check/highlight; support +/- order, cancel and explicit save.
3. Compact the filter bar to a single expandable filter control.
4. All shell menus, modules and shortcuts should resolve a shared function catalog rather than hardcoding divergent destinations; page vs subfeature identity must remain explicit.
5. Settings should optionally hide helper/explanation text, retaining key titles and trusted source/quality visibility. Chart numeric axis should use concise currency/unit convention. Capital observations should vary across time horizon; not only a fixed balance label.
6. Ask if functions belong in top-level Portfolio/Market/Lab/News or secondary workspaces.

## Design response and source boundary
- SOURCE_CONFIRMED: 19 official UI identities and existing MA10-U01 shared layout, UI01 Dashboard (`/dashboard`), UI08 Portfolio (`/portfolio`). Top level categories are PROPOSAL and do not rename official pages.
- UI-only function registry: 19 official pages + tentative subfeature anchors for navigation, shell-card linking, and shortcut catalog. Subfeatures are not independent UI IDs and do not declare backend endpoints.
- Typography modal: global, top/side navigation, widget titles, financial amounts, chart labels, tables, small explanatory texts; editable family and sizes. Settings previews can be cancelled without applying.
- Shortcut editor: explicit modal editor with draft state, add/remove/reorder, selection state, drag/resize, save/cancel. Mere click on "+" never changes Git or backend state.
- Filter control: one collapsed global entry expanding only when needed. Filter/asset group definitions require later source/DTO verification.
- Helper text visibility option: may hide explanatory text only, never the environmental `LAB/PAPER/LIVE`, permission, `UNKNOWN/STALE/PARTIAL` or source/cut/quality markers required for safe interpretation.
- Capital card: period D/W/biweekly/M uses distinct synthetic observation series and per-period vertical scale; no inferred actual account balances or return metrics.
- UI labels and locales: English Arial / Chinese Microsoft JhengHei default design candidate, fallback availability varies by browser OS.
- News remains UNVERIFIED (no source-backed new UI identity or news data adapter).
- Layout/server preference sync requires independent DTO/persistence approval. Prototype only exports JSON; browser changes do not update Git automatically.

## Outstanding feature questions / gating
| ID | Issue | Initial action | Gate |
|---|---|---|---|
| D1-F07 | Typography persistence & font fallback rules | Declare token spec, no server settings API yet | PROPOSAL; REVIEW if new DTO |
| D1-F08 | Shortcut subfeature identity and permission-scoped commands | UI catalog only; verify anchor and authorization before coding | UNVERIFIED |
| D1-F09 | Hidden helper text must not hide mandatory safety/context information | Validate per-page state matrix | FORMAL_REVIEW_REQUIRED if authority presentation changes |
| D1-F10 | Period-scoped capital metrics/units and DTO/source/cut | Separate synthetic visuals from producer-backed cash/positions | UNVERIFIED; REVIEW if new aggregate contract |
| D1-F11 | Top vs secondary nav grouping | Portfolio for personal assets; Market for discovery; Lab for research; News placeholder | OWNER_DECISION_REQUIRED at D1 acceptance |

## Testing and currentness
- Review exercise covered font modal, preview/revert, shortcut edit/cancel/save, routing index, capital period selection, and filter collapse.
- Prototype is not a deployed B3 page or integrated API/BFF test; detailed contract and cross-page permission validation remain pending.
- D1 v0.5 remains **NOT ACCEPTED**; use future Human feedback to append versioned records, do not overwrite.
