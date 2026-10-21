# B3 V1 / D1 v1.14 — One Authoritative NxM Slot-Drag Handler

**Date:** 2026-10-21 Asia/Taipei  
**Design status:** `WIP / NOT_HUMAN_READY / NOT_CODING_AUTHORIZED`. These labels are only review notes.  
**B3 accepted source commit:** `9643bfc93a1631154be877536a1c91fc58df84be`.  
**Design branch:** `design/b3-v1-ui-precode-review-20261017`.  
**Published WIP:** `docs/design/b3_v1_ui_precode/prototypes/B3_V1_D1_FullDashboard_v1_14_WIP.html`; Git commit `6d7ec21ca5934cf15594500a0b4165035c1fc31a`, Git blob `4c2ea6c9b86b54198d0197fa35e95e0b847d2077`, exact Git blob SHA256 `7b7e0f69093510e30d1c06b4de7efef79ab1b808773a3901ce8bb209d7337283`.  
**No official React/ASP.NET/Python product coding, no live database/SQL, no API/DTO/Trading authority change, no formal WO/Grant or acceptance.**

## A new confirmed v1.13 root cause (important)

The v1.13 HTML had **two simultaneous pointer drag implementations** bound to each internal module slot:

1. `d19PaintModuleGrid` base rendered slots, initially with click selection only.
2. Later `d110OriginalPaintModuleGrid=d19PaintModuleGrid` and `d19PaintModuleGrid=function(){...}` wrapped the renderer, attaching additional independent `pointerdown/move/up` listeners with an old bounded geometry calculation and cached `start.target`.

During v1.14 initial implementation, the new robust slot handler was inserted into the base renderer while the old wrapper still ran. A reproduced negative case showed:

- Drag a 2×1 information region to second row: first handler moved it legally.
- Then drag far outside the NxM canvas and release.
- The new handler correctly detected `outside:true` and declined movement, **but the old listener still applied its last clamped cached position `(0,0)`**, silently reverting the region.
- This negative case failed **9/10** in the first test, despite zero JS exceptions.

**Correction:** Remove only the superseded wrapper `d110OriginalPaintModuleGrid...d19PaintModuleGrid=function()`, keeping its **separate** `d110SlotResize` and `d110OriginalRenderModule` resizing inspector controls. The v1.14 base renderer now has one authoritative pointer path and one geometry rule, with no duplicate active event listeners.

## v1.14 design interaction additions

- Whole-footprint legal checking for **every** slot rectangle `(x,y,w,h)`, not only the pointer's first cell.
- Nearest legal coordinate search excludes overlap with all other slots and checks NxM boundaries.
- Visual translucent ghost during pointer movement; only pointerup commits the draft; releasing outside or with no legal location preserves previous slot position.
- Click without real drag still selects a slot and opens the A–G inspector. The same third-layer information fields/producer restrictions remain.
- **Keyboard parity:** with focused slot, Shift+Left/Right/Up/Down moves one grid unit if and only if valid. Focus remains on the moved slot; overlap and border attempts are blocked with an inline status. This is a design choice pending final accessibility review.
- These changes concern mock design editing only. No module can acquire new data authority by being moved or resized.

## Exact-Git-blob rerun (not source-independent production testing)

The original locally edited file carried one LF separator between JS function blocks that the file-reader-based Git publication removed. That separator removal is syntax-neutral (`}` followed directly by `/*...*/`). A Git SHA-1 `git hash-object` equality check and UTF-16 content fingerprint established exact byte identity to the **published Git blob**. All seven suites were rerun against the exact published blob, **not** just against a preliminary container copy.

| Suite | PASS | FAIL | Scope |
|---|---:|---:|---|
| v1.9 inherited three-layer editor | 18 | 0 | Workspace/module/information flow and startup candidates |
| Asset and shortcut matrix | 26 | 0 | Home cards, category pager, mock authority states |
| Five-swatch palette | 13 | 0 | Wheel, HEX/RGB, Save/Cancel |
| Responsive | 14 | 0 | Up to simulated 200% CSS zoom and width matrix |
| Atomic in-use module retirement | 10 | 0 | Replacement, Cancel/Confirm, cross-page references |
| Workbench rectangle property suite | 5 | 0 | Nearest legal position; 600 generated geometry examples in one aggregate case |
| **New NxM internal information-slot drag + keyboard** | **13** | **0** | Pointer ghost, collision, outside rollback, Shift+Arrow parity, no JS exceptions |
| **Total bounded design checks** | **99** | **0** | The individual suites overlap and are NOT 99 exhaustive independent product tests |

Portable QA script in design Git: `qa/B3_D1_v1_14_MODULE_DRAG_REGRESSION.py`; use `B3_CHROMIUM_EXECUTABLE` if a local browser install is managed separately. The Python regression was checked in a relative-directory staging arrangement before publication. Reports are mock-only and must not be interpreted as broker/API/runtime claims.

## Keep-in-scope D1 unfinished gates (do NOT show WIP prototype to Human)

The user's consolidated priority remains **finish all past corrections before asking for another single UI test**. The next complete review must cover:

- `D1-M01..M17`, `D1-R14-01..10`, `KEEP-01..15` with reproducible exact-source binding, negative tests and no unchecked skips.
- 5 portfolio subjects + All view, 7 aggregation periods and correct per-strategy period bars / prior amount and percent, 1/6/8-asset category pagination, multi-currency/account/snapshot/freshness warnings.
- Global shell, flyout semantics (75% translucency, 2s hover), shortcut grouped tree, reset/import/delete icons with file security and draft undo.
- Semantic palette contrast and color role completeness; five swatches, separate HEX/RGB editor, named theme/preset saved draft vs Cancel and font groups at real zoom 200%.
- Workspace page-specific layout vs shared geometry; all legal collision/edge behaviors, module preview A/B/C, all category restrictions; split, resize and save/rollback across five workspace views.
- Stable Template/Module management: create/edit/copy/rename/replace/retire, *source subject binding preserved*, cancellation atomic.
- Tab/window startup presets/restore and true multi-monitor/session/account isolation remains **UNVERIFIED / FORMAL_REVIEW_REQUIRED**.
- **UI01–UI19 × six MA10 Units × 64 findings** source-bound crosswalk, exact UI18 contract and any non-existing fields/historical API marked UNVERIFIED.
- Visual Reviewer checks design only, never alters formal functional contracts or trading authority.

**Human delivery protocol while unfinished:** no interim preview links, no request for item-by-item confirmation, no assertion of design acceptance. If a response is necessary before completion, say only: 「任務尚未完成，請按『繼續』，接續完成後續任務」.
