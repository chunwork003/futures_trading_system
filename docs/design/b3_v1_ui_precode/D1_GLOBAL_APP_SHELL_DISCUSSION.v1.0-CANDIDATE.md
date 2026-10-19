# B3 V1 — D1 Global App Shell / Investment Overview v1.0 Candidate — Review Continuity Record

**Date:** 2026-10-19 (Asia/Taipei)  
**User instruction:** Continue prior task. Earlier assistant committed to creating `D1 v1.0 Candidate 設計清單` (template table, necessary/optional modules, navigation/settings trees, display toggle table, remaining D1 issues).  
**Record status:** `PROPOSAL / OWNER_REVIEW_PENDING` (human-friendly review labels, not formal governance machine states).  
**Accepted design source commit:** `9643bfc93a1631154be877536a1c91fc58df84be`.  
**Preserved previous discussion records:** `D1_GLOBAL_APP_SHELL_DISCUSSION.v0.2.md` .. `v0.9.md`. No overwriting or Human Acceptance assertion.

## v0.9 → v1.0 design delta

| Source of change | v1.0 handoff rule | Status |
|---|---|---|
| v0.9 / Human feedback: all modules must align, no hidden vertical scroll, card data count stable | Adopt proposed typed `Template Registry` with legal S/M/L/XL size choices. Each `(template,size)` defines 12-col span, fixed height, capacity, mandatory fields, optional details and source UI ID. Unsupported sizes disabled. Cap does not mean actual API pageSize. | PROPOSAL |
| Human: min unit horizontal 6, but not unsafe shrunk finance UI | Proposed grid minimum 2/12 (6 theoretical S modules across desktop), also minimum readable width 190 CSS px. Adaptive fallback/stack at smaller view; safe warnings always visible. | PROPOSAL; narrow layout & font full visual acceptance pending |
| Human: portfolio trend needs meaningful metrics | Trend minimum L/XL; synthetic period-end portfolio value plus prior-period delta amount and percentage; source/cut/currency label; no fake ROI denominators. | PROPOSAL, actual producer/metric contract UNVERIFIED |
| Human: left settings/right settings separated, scheduling optional but initially shortcut-selected | Left bottom ⚙ manages only shortcut selection/order/category/icon. Right ≡ controls Panel/Workspace/Startup/Display & Updates/Account Env/System. Scheduling belongs future UI05 Research vs UI16 governance, not browser-side timer. | PROPOSAL, scheduler FORMAL_REVIEW_REQUIRED |
| Human: title region filtering, development captions hidden, essential source status remains | Filter collapses into UI01 title right; design/debug badges and optional notes hidden by default. Keep meaningful Source/Cut/Quality and LAB/PAPER/LIVE visible when required; financial currency ambiguity cannot be hidden. | PROPOSAL, safety SOURCE_CONFIRMED |
| Human: user icon library 20+ and downloadable/importable | Source-indexed shortcuts, custom icons >=20, import/export design; dangerous external SVG/XSS/resource permission require security review. | PROPOSAL; upload/security FORMAL_REVIEW_REQUIRED if new contract |
| Human: card independent pin should remain possible | Follow main portfolio by default; single-card pin allowed with explicit pinned portfolio label; rebind on account/env changes, no mixed account authority. | OWNER direction, final design review pending |

## Delivered Git design artifacts

1. `docs/design/b3_v1_ui_precode/D1_V1_0_CANDIDATE_DESIGN_SPEC.md`
   - Formal-looking *design-only* list of 11 proposed `T-*` template families, capacities, legal sizes, mandatory data semantics, necessary vs optional home modules, navigation/settings trees, display toggles, risks and gates.
   - It is not a replacement for the source-accepted MA10/PK11/API/DTO documents.
2. `docs/design/b3_v1_ui_precode/prototypes/B3_V1_D1_Template_Studio_v1_0.html`
   - Interactive offline-only candidate template comparison: template type, legal size selectors, 1/6/8/14 mock records, fixed-header pagination, fontsize 100/125/150%, source state FRESH/PARTIAL/STALE/UNKNOWN (visual only), fullscreen, draft JSON export.
   - Synthetic/mock, no backend API, broker I/O, risk or order permission, nor auto Git writes.
3. Previous complete UI01 App Shell continues at `prototypes/B3_V1_D1_AppShell_Interactive_v0_9.html`. The Studio is a *separate review companion*, intentionally not yet merged back into the full dashboard before Human validates size choices.

**Local source artifact SHA256**:
- spec markdown `73b2342bfa63966b6c97dd09008e451865dfac4c2f53fd88926a367d872268e3`
- template studio html `082614cdbb0c174a7a8b71a69a42e6a32fdcf01ac020e31668855374ea7998b4`

## Browser design checks

- Chromium set_content (this sandbox blocks direct file:// navigation) at 1500×940:
  - grid 6 visible of 8, page 2 changes to 2 records + 4 blank slots, fixed outer card height across pages.
  - changing to 1 record shows 1 + 5 blank slots; legal M template shows capacity 3.
  - UNKNOWN masks numeric amount; switching back FRESH shows synthetic values.
  - T-CHART-PORT: S and M disabled, L trend draws.
  - T-TABLE-HOLDING: M=3 rows with 8 entries across 3 pages, switch to L=6 rows; no JavaScript page errors.
- Added spot checks at widths 1440/1100/820/600 with fontsize 150%: browser reported 0 body vertical overflow for the selected asset-card L template. **This is not proof all template types, data labels, breakpoints, min 2/12 layout or accessibility are valid.**
- Full page screenshot `B3_V1_D1_v1_0_template_preview.png` stored as conversation artifact. No formal B3 E2E/Runtime/Permission proof.

## Pending owner decisions and independent review gates

1. Do S/M/L/XL column spans and capacities in spec align with your desired standard module size? Template M can be 3 or 4 columns depending on data.
2. Are both asset grid and holdings list shown by default, or should one start hidden? Proposed both initially present, asset grid optional to hide.
3. Which authority-defined denominator/value should portfolio trend default to (Equity vs Portfolio Market Value)? Until source verification, preview labels all totals DEMO and no real comparison is asserted.
4. Source-bind actual UI01/UI08 measures, strategy return, FX/currency, resource scope, snapshot, cut, coverages and UI16/05 scheduling. `UNVERIFIED` and `FORMAL_REVIEW_REQUIRED` if creating/changing contracts.
5. Design review of full 19 UI Source/Contract/Unit alignment and missing 64 Findings remains in D1/D9 crosswalk handoff.
6. Complete visual QA for RTL/keyboard/focus, WCAG contrast, small screens with 150% fonts, long i18n labels, server cursor pagination; no Codex coding or formal acceptance of prototypes.

**D1 is not closed.** The next eligible step is Human visually reviewing the template registry and giving changes; approved rules can be merged into the next fully interactive UI01 dashboard revision. Human UI Design Acceptance ≠ Coding Authorization.
