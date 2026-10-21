# B3 V1 — D1 v1.11 WIP / Visual Color Workbench & Honest QA Checkpoint

**Date:** 2026-10-21 (Asia/Taipei)  
**Status:** `DESIGN_CORRECTION_IN_PROGRESS / NOT_OWNER_READY`, not a B3 machine state, not Human Design Acceptance or Coding Authorization.  
**Baseline:** B3 accepted commit `9643bfc93a1631154be877536a1c91fc58df84be`, maintained read-only for product code.  
**Branch:** `design/b3-v1-ui-precode-review-20261017`.  
**WIP prototype:** `docs/design/b3_v1_ui_precode/prototypes/B3_V1_D1_FullDashboard_v1_11_WIP.html`; latest exact local UTF-8 SHA-256 `4356f63d7961d88bab0623f9714798903775f7194ee37bc343b809627ca4ebb1`; Git update commit `22146e5b4ef5e2bd9d30be0a1dcd59d87c912d3d`.

## Human instruction remains binding

**Do not send intermediate previews or ask for per-feature verification.** Keep iterating all prior owner changes and `D1-M01…M17`, `D1-R14-01…10`, `KEEP-01…15`, then present a single fully reviewed UI design version. If a turn must stop while incomplete, the final user-facing reply is only 「任務尚未完成，請按『繼續』，接續完成後續任務」.

## Implemented bounded delta (v1.10 → v1.11)

1. Adobe-inspired, **not pixel/source-code copying**: five harmony handles and connecting lines are shown on the color wheel, with modes analogous/complimentary/triadic/square/monochrome.
2. Five primary palette swatches render **distinct actual colors**. Detected CSS conflict in v1.10 universal `button background!important`, which caused the five colors to render identically; fixed with `--d111-swatch` role precedence.
3. Clicking a color swatch opens an **independent anchored color editor** for HEX, RGB and local color control. The original button is replaced by swatch redraw, so pointer anchoring must use the current replacement DOM node rather than a stale detached button; corrected after screenshot inspection.
4. Color codes hidden on the main palette except hover/focus, while HEX/RGB remain editable in the popover. Invalid code triggers validation; **Cancel** leaves the selected color unchanged.
5. Theme selector, custom palette name and small save/remove symbols now share one row, with visible label indicating the currently edited theme; built-in presets remain immutable. Unlike a production storage claim, custom presets live only in standalone design state.
6. Escape closes only the per-color popup if it is open, rather than accidentally discarding the entire Settings session.
7. Compact rail icon glyphs increased to approx. 76% of standard button frame (32px glyph in a 42px high rail button). Imported PNG/WebP similarly scales to 32px. Wide text mode stays separately sized.
8. No new UI ID, API, broker, SQL executor, runtime authority, or production React/Python/ASP.NET code.

## Browser verification actually executed

- `B3_D1_v1_11_palette_test.py`: **13/13 PASS**, including five wheel points and connecting lines, theme name, hidden inline HEX, per-color popup, RGB input, Save, Cancel, harmony selection and zero JS exceptions.
- Rerun inherited `B3_D1_v1_9_REGRESSION_TEST.py` against the v1.11 exact HTML: **18/18 PASS**, including three-layer editor navigation, category source isolation, query spec as design-only rather than executable SQL, default/custom startup modes and modal boundaries.
- Visual matrix `B3_D1_v1_11_VISUAL_TEST.py`: 2560/1920/1500/1100/780px at 100%; 1500/1100/780px at 125 and 150% simulated body zoom: **11/11 PASS** (zero card overflow, zero doc horizontal overflow). 
- **200% simulated body zoom is NOT PASS**: 1500px has approx 14px document horizontal overflow and 33px extra in a card, 1100px approx 41px card overflow, 780px approx 9px overflow. The `body.style.zoom` simulation differs from real browser zoom; test the actual preference and genuine browser zoom in a later pass, but do not mark 200% passed.
- A legacy quick audit `B3_D1_v1_10_INTEGRATION_AUDIT.py` contains intentionally false/obsolete predicates (e.g. checks `svg rect` on **All-portfolios** comparison page when per-strategy bars are on a **single** portfolio page; tests `[data-setting=font]` despite the integrated Panel typography; hardcodes `lambda:False`). Its `FAIL` counts cannot be treated as real failures or passes. Replace it with correct semantic user-journey cases rather than modifying functionality to satisfy incorrect selectors.

## Remaining gates — explicit NOT COMPLETE

- 200% font/custom zoom, long Chinese names, multiple account contexts, multi-screen/session isolation and full keyboard/ARIA focus management.
- ALL old D1 v0.2–v1.9 functions and cross-page links must be audited against KEEP-01…15 and D1-M01…17; a local 18-case test does not establish full parity.
- Workbench drag: exhaustive collision, nearest **whole rectangle** legal location, resize, Save/Cancel/Esc and shared template geometry independent from data authority.
- Module rename/overwrite/new-version/delete-with-usage and compatible replacement; internal per-slot resize/move constraints with undo/rollback.
- All asset category tabs, 1/6/8 records, donut amount/share and strategies bar/line tooltip aggregate over all seven periods, SNAPSHOT/CUT/QUALITY and UNKNOWN/PARTIAL/STALE.
- Custom palette gamut/contrast across every semantic role and its Save/Cancel, plus shortcut import MIME/decode/magic validation, persistence and icon semantic matching.
- Startup scenarios across tabs/windows/account/env permission not actually executed; data producer and API/DTO availability for historical metrics still **UNVERIFIED**.
- Final source-bound crosswalk of all 19 official UI contracts, 6 MA10 units and historic 64 findings, plus UI18 precise binding.
- Visual UI Reviewer remains advisory only: may advise on size, spacing, color, contrast, legibility; cannot remove earlier functionality, change authority, or amend B3.

**Do not present v1.11 WIP to Human as a completed UI.** Review again and continue development on subsequent 「繼續」 turns.
## Follow-up correction — palette draft rollback

- WIP prototype commit `969c79c45bdc3cf52af2093b56e60a13414981a9` additionally captures `d18CustomThemes` and `d18ThemeDraft` at Settings-entry, restores both on Cancel/Esc, and only retains on explicit main Settings Save. Previously, a newly named swatch palette remained visible after Cancel even when theme role colors rolled back.
- Chromium negative test: create `臨時測試` named palette → observe fourth option → main Settings Cancel → reopen Settings → option absent. **PASS**, no uncaught JS error. Pure design-only state, not server persistence.
- Work remains incomplete; do not present this WIP as Human-ready UI or claim D1 acceptance.
