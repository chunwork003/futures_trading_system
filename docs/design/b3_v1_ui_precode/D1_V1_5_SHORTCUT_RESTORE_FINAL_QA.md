# B3 D1 v1.5 — Shortcut Restoration / Final-Build QA Supplement

**Date:** 2026-10-21 Asia/Taipei.  
**Classification:** PRECODE DESIGN CANDIDATE, **not Human-accepted**; not a formal machine state, Coding authorization, Architecture change or product-runtime certification.  
**Accepted source pin:** `9643bfc93a1631154be877536a1c91fc58df84be`.  
**Design branch:** `design/b3-v1-ui-precode-review-20261017`.  
**Full HTML prototype:** `docs/design/b3_v1_ui_precode/prototypes/B3_V1_D1_FullDashboard_v1_5_CANDIDATE.html`. Updated Git commit `27aa1221ce93896ff7e5195de1505134ac74abc8` (source latest blob `7a6676dc63888a7bd2487787ffdbe29be71366bc`).  
**Latest exact-byte local file SHA256:** `8cfd2adfcb5045fc682df1604f4ff1279f8e45851f5f044645ea8fc3fb4415bd` (UTF-8 container bytes, Git content should be checked via Git blob for exact identity).  
**Previous record:** `D1_V1_5_CORRECTION_AND_VISUAL_REVIEW.md`. This supplement preserves that record rather than overwriting the original history.

## Additional regression discovered and fixed (D1-15-F10)

The earlier v1.4 / initial v1.5 shortcut manager preserved ICON replacement but had **regressed the existing selected shortcut / subfeature selection, ordering and removal**. Owner had repeatedly requested feature management and an import icon inside the icon picker, **not replacing the whole Shortcut Editor with an icon-only settings dialog**.

Latest v1.5 restores the following combined workflow:

1. Left-bottom gear opens **Quick Editor only**, separate from right-top Global Settings.
2. Per-category selected list supports move up/down and remove. Available official UI01–UI19 page and typed subfeature choices are shown and searchable, with selected choices highlighted.
3. The **24 built-in pictograms + last tile ＋** remain in the same shortcut dialog, with PNG/WebP local preview. The picker does not itself grant a backend upload path.
4. Explicit Save commits the **combined selected shortcuts plus icon changes** to this in-memory prototype; Cancel discards the edits. Compact rail popup remains themed, 50% transparent, untitled, and dismisses on pointer departure ~1.9s.
5. Shortcut selection links remain **official UI ID-based design navigation**, not real backend page routing. UI19 and other pages retain their identities. Research Scheduler remains a PROPOSAL, not accepted execution API.

## New tests run on final submitted local bytes (not on early v1.5 Git snapshot)

```
START selected shortcuts 2; currently available features 7
AFTER_ADD selected shortcuts 3
AFTER_CANCEL selected shortcuts 2 after reopen
SEARCH query '策略': 1 matching candidate
UPLOAD_PREVIEW: 1 rendered local PNG image
ICON_SAVED: imported image appears in Market rail category
ERRORS: []
```

Existing interactive tests on latest HTML or immediately preceding byte-equivalent variant also verified: 8 default home cards; main-nav Market dropdown 4 items; left flyout computed alpha 0.5; palette wheel 8 roles; custom startup options; 36 initial empty Workbench grid cells; NxM module slot #01 with live mock inspector; period chart tooltip provides total+strategy amount and percent changes, first point prior values intentionally UNKNOWN; Cancel startup/theme restores original; 3-column capital module drag releases at row 6; no uncaught JS errors.

**Latest exact local-final screenshot/geometry rerun** at 1500px, 1100px and 780px (viewport height 950px): **8 original cards**, horizontal overflow **0px**, card-body overflow **0px** for all eight in all three widths, and JavaScript errors **none**.

Pre-restoration font geometry audit on unchanged responsive CSS at 1920/1500/1100/780px × 100/125/150% = 12 cases showed no card content overflow, but the **final post-shortcut-update 12-case audit was interrupted by a browser test-process pipe failure**. Therefore the final artifact is **not certified for all twelve cases**; only the specifically rerun three widths are final-byte evidence. An automation timeout is NOT a passing test.

## Role and governance boundaries

The `VISUAL_UI_REVIEWER` may review only typography, spacing, balance, chart readability, responsive layout, colors and accessible presentation. **It cannot change official UI01–UI19 identity, routes, business features, API/DTO contracts, Source/Cut/Quality, capital/order/risk/permission semantics, or add/remove functionality by aesthetic preference.** A requested functional change goes to the functional/source review and Human confirmation.

Current D1 still needs complete qualification before design acceptance:
- True account/window-scoped authority, cross-session/cross-device preference storage and startup restore are not implemented.
- User-icon upload requires binary signature verification, decoding and size limits, CSP/sanitization/persistent asset review before production.
- The standalone chart and financial sample values are entirely synthetic; no actual producer/strategy-level PnL attribution can be asserted.
- Keyboard/focus, collision negative matrix, real data cursor paging, 19 UI/64 Finding crosswalk, high-contrast user palettes and 12-case final zoom audit not completed.
- Menu choice updates a design-only hash and toast; it is not a deployed UI Router or function being available on B3.

**Decision gate:** D1 v1.5 is `PROPOSAL / AWAITING_HUMAN_REVIEW`, not a full D1-R14-01...10 PASS. Continue D1 with bounded regression review, then formal design handoff only after Owner visual acceptance. No source-architecture amendment, product coding, WO/Grant or independent governance review is authorized by this prototype.
