# D1 v1.1 — Owner Composite Module Builder Feedback / Discussion Intake

**Date:** 2026-10-19 Asia/Taipei  
**Status:** `DESIGN_PROPOSAL / HUMAN_REVIEW_PENDING`, not a B3 machine state. No Human Design Acceptance, no PK11 implementation authorization, no runtime/API/DTO changes.  
**Adopted source pin:** `9643bfc93a1631154be877536a1c91fc58df84be`.  
**Prior design continuity:** `D1_GLOBAL_APP_SHELL_DISCUSSION.v0.2.md` – `v0.9.md`, `D1_GLOBAL_APP_SHELL_DISCUSSION.v1.0-CANDIDATE.md`.  
**Companion existing source:** v0.9 complete UI01 investment Dashboard; v1.0 standalone Template Studio (only sample; **not** integrated home page).

## Owner request and disposition

| Ref | Owner input | v1.1 response | Gate |
|---|---|---|---|
| D1-11-01 | Each feature gets a base module; in search/settings unsupported sizes disabled | Formal candidate registry: KPI/list/chart/allocation/research/composite classes, S/M/L/XL with class-specific legal size and A/B/C compatibility, incompatible choices disabled; each must comply with min-readable fields and fixed-capacity layout profile. | PROPOSAL; final per-widget source/DTO/visibility verification pending |
| D1-11-02 | A Settings → layout 'create module' tool; category/size → choose A/B/C → click '+' placeholder to insert content → save; later reusable from panel library; avoid ongoing application code edits | Integrated non-product HTML designer in **full** dashboard: choose name/category/size/A-B-C, click each content zone, set typed block kind, title, bounded mock binding and official page/subfeature; validate at least one slot; save to user design library; add a new card to the existing UI01. Saved templates support edit, and refuse delete while placed. JSON export/import for design handoff, memory and optional localStorage (browser-dependent). | PROPOSAL. Persisted UI preference API/revision/access control/compilation authority requires formal review before product coding |
| D1-11-03 | Clarify A/B/C composition relative to sketch and module templates | A = one frame; B = left large + two right stacked; C = left large + upper-right wide + bottom-right two (four independent slots), matching Owner sketch. Supports multiple class/size families with rule-based disabling. Composition is visual layout only; not executable scripts or arbitrary cross-dataset arithmetic. | PROPOSAL |
| D1-11-04 | D1 v1.0 only shows component; previously confirmed full page apparently disappeared | Confirmed deliverable issue: v1.0 was shipped only as independent Studio and did **not** incorporate the v0.9 dashboard. Corrected v1.1: copy v0.9 full page with original 8 cards and existing navigation, add designer to Settings; custom save/add yields a 9th card without removing original components. Original sources retained in Git. | SOURCE_CONFIRMED prior artifact structure, corrected as design delivery |

## Source / architecture limits

- Official `UI01` Dashboard (`getDashboard`, `getAccountCapital`, `getHealth`), `UI08` Portfolio and 19 UI ID registry remain unchanged. MA10 Desktop layout / Source/Cut/Quality/LAB-PAPER-LIVE boundaries are mandatory.
- User composing a view from existing UI refs is a **visual grouping**, not a new quant strategy, data producer, API operation, broker/admission command or capital calculation authority.
- Slots with no real verified source show `DATA SOURCE UNVERIFIED`; local mock numbers cannot imply real account values. `UNKNOWN` masks mock numeric display in both standard and composed cards.
- Candidate of browser-local template storage is not Git and not multi-device persisted server state. Owner needs to export JSON / provide feedback for exact Git inclusion. Account/workspace resource-scope and Revision/CAS conflict checks must be designed separately.
- Templates sharing an ID are shared definitions. Editing a saved definition currently updates all its instances after redraw; recommend future version/revision and fork-this-instance control before acceptance. Deleting a referenced template is blocked.
- Fixed-capacity/non-scrolling policy applies to composed zones also; full responsive and 150% font regression on every layout/slot combination remains unverified. C layout should be disallowed at insufficient width, not hide key finance data.

## Visual prototype / QA

- Interactive **full home page**: `docs/design/b3_v1_ui_precode/prototypes/B3_V1_D1_FullDashboard_ModuleStudio_v1_1.html`.
- Source-bound design spec with schema proposal, reviewed tradeoffs and pending gates: `docs/design/b3_v1_ui_precode/D1_v1_1_CUSTOM_MODULE_DESIGN_SPEC.md`.
- Chromium desktop Playwright set_content: original 8 cards present; Settings → Workbench → Template Studio opens C 4-slot skeleton; incompatible sizes disabled; adding editable slot content and saving generates library item; adding saved template creates 9th card; previous 8 cards preserved; editing existing template does not duplicate; deletion blocked if referenced; UNKNOWN hides synthetic numeric value; no JS pageerrors in tested flow. Direct file URI not used due environment sandbox.
- Untested: full range of font/viewport/palette combinations, real BFF/REST binding, actual permissions, multi-session/account synchronization, localStorage across every browser privacy mode, Content Security Policy, formal accessibility/keyboard evaluation and server-side validation.

## D1 follow-ups

1. Human visually check whether A/B/C grouping is appropriate, if template editing should update all placed cards by default, and whether more fixed patterns (D) are warranted. No need for a large questionnaire yet.
2. During final UI01 design/WORK handoff, verify each user module binding against real UI01/UI08/read API DTO and source/cut; no unverified custom computation.
3. Preserve `D1` as **open**. Final Design Acceptance is separate from formal Reviewer acceptance and Coding Grant.
