# B3 V1 D54 — UI Design Checkpoint & Coding Rules

Status: DESIGN_CHECKPOINT / NOT_D1_ACCEPTED / NOT_RUNTIME_AUTHORIZED.
Source: interactive HTML prototype; mock data only, not React or C# product code.

## Role definitions
Five palette roles are fixed by identity: [0] Background, [1] Sidebar, [2] Module background, [3] Accent, [4] Text. Do not infer a module color from background, sidebar, accent, or chart-series colors. Chart category/strategy semantics stay independent.

## D54 fixes
- When opening global settings, reconcile the editor palette with the four currently applied theme identity roles; do not silently substitute an unrelated fallback palette based on legibility. Handle safe text contrast independently.
- Paint the radial saturation triangle only after the wheel's final layout dimensions are known, and repaint on resize. Its tip meets the active saturation boundary (R × percentage/100).
- Save both the original five color values and the saturation percentage; never reset to 100% on re-opening a saved 50% theme.
- D54 gives modules **75% color opacity / 25% transparency** to preserve selected module hue against a contrasting underlying background. Earlier D49 gave them 25% opacity and thus blue over yellow appeared green. Owner validation remains pending; this is NOT interchangeable with **75% transparency**. Other central editor overlay transparency is not changed by this checkpoint.
- Calculate module text, axes, form, and tooltip contrast against the effective composite. The local sample QA checks major text >=4.5:1; complete design-system audit remains open.
- Five palette cards use consistent sizes/corners. The color wheel is fixed when using Base color (small popover) or Image (file chooser). Text/icon controls remain high-contrast, without decorative copy.
- One page-wide grid: 5% left margin / 30% wheel / 10% gutter / 50% swatches / 5% right margin. Wheel and color cards align. Seven harmony controls have rounded square hitboxes.
- Color Wheel Tool is a *single line* no wider than the wheel; font/width may recalculate it, not hue/other color actions.
- Shortcut rail is fixed width 56px with 43×43px hitboxes. Icon, icon+label, and label-only are displayed inside these fixed cells.

## Typography, icon, interaction
Use five text roles (global heading/subheading/body; module heading/body) each with Chinese font, English font and one font-size selection. Browser Local Font Access is permission-gated. Imported fonts/icons in IndexedDB are prototype-only, not production asset management.
Monochrome line icon semantics and popup behavior are consistent: outside click, ESC, 2-second mouse-leave (where applicable). Cancel restores snapshots.

## Data and authority
DataFlow ID -> INFO ID -> MOD ID -> Workspace ID. One data source may back multiple visual INFO IDs; workspaces reference modules, modules reference INFO, INFO references data flows. Respect existing frozen B3 Unit/API/DTO identifiers. Frontend React/TypeScript -> ASP.NET Core BFF -> Python API -> Quant Core -> PostgreSQL. No BROKER I/O or production SQL in this prototype. No master merge or implementation grant inferred by Git snapshot.
