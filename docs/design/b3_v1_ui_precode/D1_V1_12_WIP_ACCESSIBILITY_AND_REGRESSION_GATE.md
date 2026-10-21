# B3 V1 — D1 v1.12 WIP / Responsive 200% and Historical Function Recovery

- **Date** 2026-10-21, Asia/Taipei.
- **Review status**: PRECODE_WIP / OWNER_NOT_READY. These are documentation labels, **not** formal B3 statuses.
- **Accepted B3 pin**: `9643bfc93a1631154be877536a1c91fc58df84be` (unchanged).
- **Design branch**: `design/b3-v1-ui-precode-review-20261017`. Product code, broker data, rights, orders, migrations, API/DTO, master, formal WO/Grant **unchanged**.
- **Candidate**: `prototypes/B3_V1_D1_FullDashboard_v1_12_WIP.html` at Git commit `0398a953fefe8855838e178223484efe58a2eb63`; locally tested exact UTF-8 SHA256 `272d5356ad614dabde2f0db01c2b58baa0703353921a25b8aabd3ade25ac29c1`.
- **Human instruction**: Do not ask them to inspect incomplete UI; continue independently until ALL prior D1 requested corrections are satisfied. If unfinished, only request 「繼續」.

## Verified v1.11 → v1.12 changes

1. **Responsive content-capacity rule, not clipping**. `.main` is an inline-size container. When actual available CSS content width ≤700px, each dashboard row has a stable 305px height for that density/width profile. Stable six-slot asset/holdings pagers are unchanged. This is responsive **by usable width**, not by changing number of records. It fixes prior observed card overflow at simulated 200% zoom.
2. **Preserve global navigation**: when six main tabs, search, account and Settings cannot fit, the top-level header scrolls **internally**; it does not cause document horizontal overflow or silently remove menus.
3. **Zoom-sensitive modals**: when an embedding host sets CSS `body.zoom` ≥1.7 (distinct from genuine browser zoom), modal width/height is constrained to visible viewport and content sections may scroll. Native browser zoom is left to responsive `vw/dvh`. This avoids cutting off Save/Cancel in visual QA simulations; it does not claim all accessibility standards are met.
4. **Previous accepted functions retained**: original eight homepage cards; all/5 portfolio modes, pins, category tabs, six-slot layouts, charts, quick-edit/icon import, palette/HEX/RGB, workbench three-layer editor, startup modes, LAB/PAPER/LIVE trust labels. No new financial data producers or executable SQL.

## Bound tests and evidence (final exact artifact)

| Suite | Measured inputs | Result | Boundaries |
|---|---|---|---|
| Responsive visual matrix | 2560, 1920, 1500, 1100, 780 CSS viewport widths; 100%; for 1500/1100/780 also 125%, 150%, **200%** simulated CSS body zoom | **14/14 PASS**: eight original cards, zero nontrivial card-body vertical overflow, zero document horizontal overflow, zero JS errors | CSS body zoom is a visual stress proxy, NOT proof of native 200% browser UI/keyboard accessibility |
| Three-layer regression | 1500 & 1100 editor viewport, module edit, query-spec, category restrictions, launch scenario, Cancel | **18/18 PASS** | Rendered mock-only, no producer/DTO/API execution |
| Five-swatch palette | Wheel five handles/lines, HEX/RGB popup, color apply/cancel, harmony, exception checks | **13/13 PASS** | Not exhaustive for every user-provided palette and contrast |
| Portfolio/asset/shortcut regression | All/p2, all/stock/bond ETF; six-slot invariant; holdings pagination; sorting, UNKNOWN masking, toolbar, import position, separated settings | **26/26 PASS** | Browser interactive mock; synthetic fixture, no persistence/acct isolation |
| Large zoom dialog check | 1500, 1100, 780 simulated body zoom200; global Settings → Workbench | **3 targeted width checks PASS**, both dialogs within viewport, no JS exception | Modal inner controls may require their own local scrolling; native zoom and complete focus navigation remain untested |

The first, second and fourth suite reports were generated from the same local SHA256 `272d5356...`. The palette suite reran successfully after the final change; its current JSON did not encode source SHA, so the combined **test runner must bind the SHA** on future revisions. Do **not** quote 71/71 as a comprehensive D1 approval: these are four limited suites only.

## Open work before D1 is Human-ready

- Run full, negative and property-based acceptance against ALL **D1-M01…17, D1-R14-01…10, KEEP-01…15** instead of spot screenshots.
- Complete module/workbench rectangular occupancy dragging at edges, collisions, nearest-slot snapping, resize, delete/copy/replacement of active templates, draft rollback and shared geometry without copying permissions/data.
- Cover every asset tab and 1/6/8 records, 7 chart periods, all 5 portfolio subjects, account/cut/currency boundaries and UNKNOWN/PARTIAL/STALE. Ensure bars equal *each strategy's value at each time*, tooltips show value, prior delta amount and percentage; never silently infer reliable return or cash data from mock.
- Verify 2560px ultrawide and **native** browser 200% zoom, grouped font preferences 200%, keyboard Tab/Enter/Esc, visible focus, ARIA, tooltips and modal focus trap, Chinese long labels and WCAG color contrast across custom/semantic color roles. Color state must stage Save/Cancel and not leave warm theme with stray blue controls.
- Demonstrate preview/selection/duplicate/cancel handling for imported icon data (PNG/WebP MIME + magic-byte checks; SVG disabled until security review). Ensure icon picker never accidentally opens a secondary editor.
- Validate default/start-custom/restore workspace scopes, multi-window and account isolation; real window startup/auth and persistence remain NOT AUTHORIZED/UNVERIFIED.
- Complete source-bound **UI01–UI19 × six MA10 Units**, 64 historical Findings → 19 UI crosswalk, UI18 precise binding, exact API/DTO QuerySpec data producer and renderer licensing choices. **No formal UI design acceptance** prior to Human approval.
- Visual reviewer strictly checks grid, alignment, hierarchy, density, palette, readability; cannot delete prior agreed features or alter Order/Risk/Capital/Broker authority.
- No new public preview in an incomplete stage; prior v1.11 and earlier sources must remain versioned.

## Continuation protocol

After each revision: rerun all applicable browser suites with test input and Git blob SHA, archive failures and fixes without overwriting historical artifacts, keep only exact PASS claims. Deliver one consolidated full dashboard + regression package **only after** complete design interaction review (with formal contract gaps explicitly labelled).
