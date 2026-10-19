# B3 V1 — D1 v1.1 Full Dashboard + Composable Module Studio — Pre-Code Design Candidate

- Date: 2026-10-19, Asia/Taipei.
- Type/status: `PRECODE_VISUAL_DESIGN_CANDIDATE / OWNER_FEEDBACK_PENDING` (design labels, **not** B3 machine status, Human Acceptance, formal source amendment, or implementation authorization).
- Accepted B3 baseline: `9643bfc93a1631154be877536a1c91fc58df84be`.
- Design Git branch: `design/b3-v1-ui-precode-review-20261017`.
- Continuity: D1 v0.2–v0.9 discussion and UI01 full-screen preview; D1 v1.0 Candidate Template Registry and isolated Template Studio are *retained*. **v1.0 did not integrate the standalone studio into the v0.9 overview, causing the Owner to see only a module sample**. This is the deliverable gap corrected in v1.1.
- New full-page interactive design artifact: `docs/design/b3_v1_ui_precode/prototypes/B3_V1_D1_FullDashboard_ModuleStudio_v1_1.html`.
- Human source sketch (2026-10-19): top controls `類別／大小／模板A`; bottom dashed zones arranged large-left, top-right-wide, bottom-right two slots, each with '+' insertion. The screenshot is owner-authored concept input, not a formal UI source or rendered output.

## 1. Bounded source/identity mapping

| Entity | Source-bound ID / operation | Design scope |
|---|---|---|
| Dashboard | UI01 `/dashboard`; `getDashboard`, `getAccountCapital`, `getHealth` | Main startup overview, mock cards and proposed personal presentation modules |
| Portfolio | UI08 `/portfolio`; `getPortfolios`, `listGroups`, `queryAttribution`, budget APIs | Real portfolio group/drilldown and planned portfolio read-model bindings; **UI01 cannot assume UI08 capital mutation authority** |
| Chart/Market | UI02 `/chart`, UI03 `/market` | Related chart / watchlist / symbol tools represented only as source-bound feature references |
| Research/Engineering | UI04, UI05, UI06, UI16 | Module links may point to source-verified identities; time-triggered research scheduling **unverified**, new contract and authority review required |
| Settings | UI17 `/settings`, MA10-U01 | Shared visual settings and personal layout in a **design-only local library**, not evidence of persisted production API |
| Common | MA10 12-column Shell / PK11 U01..U06; 19 UI fixed IDs | Account/environment/snapshot/coverage/Source/Cut/Quality, Read DTO, permission, mock/unknown separation remain authoritative |

**UI design registration is not a B3 API registration.** User-composed modules can reference verified UI/page/subfeature identities but cannot make new producer operations, strategy math, capital/risk calculations, order authorization or broker I/O.

## 2. Design structure: registry → composition → instance (three tiers)

1. **Component / Data Binding Catalog**: preapproved *display building blocks* (`metric`, `spark`, `list`, `status`, `link`, `text`, and explicit empty slot) with source-key candidates (`portfolio`, `capital`, `strategy`, `assets`, `holdings`, `research`, `quality`, `custom=UNVERIFIED`). Each supports a typed conceptual input and clear fallback/unknown display. This is not user-programmable JavaScript.
2. **Reusable Template Definition**: `template_id`, `name`, `category`, `size`, `layout A|B|C`, `slots[]` each with `kind`, `title`, `binding`, `feature`, `notes`, plus draft schema/version. Layout A = one zone; B = left big + right top/bottom; C = left big, right-top wide, right-bottom 2 zones. The screenshot's four-zone design corresponds to C.
3. **Module Instance / Workspace Placement**: `instance_id`, `template_id`, 12-col grid span, fixed minimum height, optional viewport/display/context scope and per-instance label. Adding a template adds another card to UI01, **without removing the original eight source-bound visual cards**. Multiple instances may reuse the same template. Production per-window persistence/copy-vs-link semantics still need separate decisions.

Suggested future shape (not adopted DTO):

```json
{
  "schema": "D1_CUSTOM_MODULE_SCHEMA_V1_PROPOSAL",
  "template_id": "user-template-001",
  "name": "自訂投資模組",
  "category": "composite",
  "size": "XL",
  "layout": "C",
  "slots": [
    {"kind": "metric", "title": "投資總值", "binding": "portfolio", "feature": "UI01"},
    {"kind": "spark", "title": "走勢", "binding": "portfolio", "feature": "UI01"},
    {"kind": "list", "title": "策略摘要", "binding": "strategy", "feature": "UI05"},
    {"kind": "status", "title": "品質狀態", "binding": "quality", "feature": "UI01"}
  ]
}
```

The model/field names above are **proposal**, never claim already supported by PK11/API catalog.

## 3. Legal size and geometry decisions

| Category | S (2/12; 195px) | M (4/12; 330px) | L (8/12; 475px) | XL (12/12; 570px) |
|---|---|---|---|---|
| KPI / cash | ✓ A | ✓ A | ✓ A/B/C | disabled |
| List / strategy | disabled | ✓ A | ✓ A/B/C | ✓ A/B/C |
| Chart / trend | disabled | disabled | ✓ A/B/C | ✓ A/B/C |
| Allocation | disabled | ✓ A | ✓ A/B/C | ✓ A/B/C |
| Research / schedule status | disabled | ✓ A | ✓ A/B/C | disabled |
| Free composite | disabled | ✓ A | ✓ A/B/C | ✓ A/B/C |

The demonstrated `B` and `C` layouts require **L or XL**, while `A` is available at smaller legal dimensions. This is only the design profile for review; the v1.0 registry's detailed per-widget min capacities remain source of further candidate refinement and override generic category allowances at formal handoff.

- Display slots should have minimum readable boundaries and a fixed body profile; no internal scroll required to access standard capacity.
- Fewer than supported entries = preserve whitespace; more = header pager `< >` with fixed number of records per page. No mock 'empty' means formally verified empty without coverage proof.
- Large typefaces and responsive profiles must choose a safe registered layout; **cannot silently clip risk/capital/state**.
- For current v1.1, custom modules render bounded mock placeholders and a small synthetic static demo; actual data sets, Query Snapshot/Cursor, money calculations and synchronized multi-portfolio context are not implemented.

## 4. Exact interactive user workflow in this concept HTML

1. Open **existing v0.9 full portfolio Dashboard**. Existing eight modules and top header/shortcut behavior are retained.
2. `≡ → 設定 → 工作台／快捷 → ▦ 建立自訂模組／模板 A·B·C`.
3. Enter **name**, select **category**, legal **size** (unsupported sizes disabled), and **A/B/C layout** (unsupported combinations disabled).
4. Click a dashed zone `+`. Right inspector defines visual component kind, title, conceptual source binding, exact formal page/subfeature and explanatory note. Repeat for other zones; at least one nonempty slot is required to save.
5. Save to **我的模組庫**. Local-browser storage is attempted with exception-safe fallback to current-session memory; can export JSON. File-based browser origins may block durable storage. **No automatic Git write, server persistence or multi-device sync**.
6. Back under `工作台／快捷`, select saved template and `＋ 加入目前投資總覽`, verify card added as 9th and original 8 cards unchanged. User can create many instances by repeating.
7. Existing saved templates can be **edited**, and may be deleted only if no homepage instance currently references them (to avoid orphan references); JSON export and import have a bounded schema/size check.
8. Current custom templates follow the main portfolio visual sample context by default; portfolio-specific authority, pinned contexts, reuse across accounts and exact cut need architecture review before Product Coding.

## 5. Front-end vs official persistence boundary

| Design capability | v1.1 prototype | Before real B3 implementation |
|---|---|---|
| Select size, layout, slot and linked feature | Supported in standalone design-only HTML | Typed registry / versioning / UI state and accessibility contracts |
| Grey incompatible sizes | Supported in class-level proposal matrix | Cross-verify actual widget required fields/min readable size, font/density profiles |
| Save/reuse template | In-memory and optional browser local storage | Resolve user/workspace/account-scope schema, serialization validation, CAS/version conflicts, migration and auth |
| Export / import JSON | Design schema only; bounded import | Constrained schema, XSS validation, no SVG/script execution, permissions, hash provenance, revisions |
| Bind to official API / display real cash/returns | **NOT IMPLEMENTED** | BFF DTO, resource-scoped permissions, snapshot/cut/quality, feature producer, capital authority |
| Use across monitor/window/device | **NOT IMPLEMENTED** | Window-scoped Context, authentication/session partitioning and persisted preferences; formal review |
| Schedule research or trade | **NOT IMPLEMENTED** | UI05 scheduler proposal vs UI16 governance, server audit/gates, must not create trading rights |
| Merge v1.1 with official work | Not merged; Git design-only branch | Human D1 Design Acceptance → full 19-page review package → formal CODE authorization separately |

## 6. UX / counterexample review

- **Template modified while multiple cards use it**: current candidate edits shared template definition, therefore all instances referencing it will reflect the revised design on re-render. Offer future `update all / duplicate and edit this instance` choice, revision record, undo and preview before acceptance.
- **Unknown data**: custom metric renders `—` when quality is not `FRESH`; mock synthetic figures can never be authoritative, even when demo toggle says `FRESH`. Source/Cut/Quality visible at the app level.
- **No producer**: `custom=UNVERIFIED` source shows explicit placeholder, not a false zero or invented PnL. Need assign real data owner & DTO or leave a note-only card.
- **Risk/order/permission**: embedding a `link` to UI09 does not grant order authority. No direct server/broker call, no JS local authoritative calculation.
- **Cross-source aggregation**: composing slots with different datasets does *not* permit summing values or comparing currencies/cuts without server-defined semantics.
- **Accessibility**: keyboard/escape focus, semantic editable slots, WCAG contrast, text 150%, responsive layouts and screen-reader announcements require full visual/UX review. Current prototype is functional design evidence only.
- **Complex user-designed arbitrary nested layout**: deferring freeform arbitrary CSS grids prevents brittle per-card-size reflow. ABC fixed safe patterns with typed slots are the bounded v1.1 choice. If Owner requires arbitrary nesting/drag-resize regions, budget a separate Visual Editor design phase and architecture/performance analysis.

## 7. Browser verification and known limits

- Chromium desktop using Playwright `page.set_content` (direct sandbox file URI blocked by test harness, not a browser claim).
- Full dashboard initially contains 8 modules. `Settings → Workspace → Custom Studio` opens with C (four slots); S/M and B/C are disabled when chart/family dimensions are unsupported; content per slot editable.
- After saving, `我的模組庫` selects new reusable candidate. Adding to workspace increases from 8 to 9. New module contains 4 typed zones and preserves original eight card IDs.
- Editing a previously saved template replaces the library entry with same ID, rather than creating a duplicate. Deletion blocked while a card references it. `UNKNOWN` masks the custom displayed metric, and no JavaScript page error observed.
- Further tests needed: large fonts + combined widgets across every breakpoint, all data quality states/producer bindings, multi-account/window, localStorage durability on varying browser privacy profiles, imported malformed JSON edge cases, CSS color contrast and XSS, formal end-to-end/API tests.

## 8. D1 follow-up decisions before acceptance

- Are A/B/C sufficient as initial safe compositions, or should another fixed D template be available? Existing sketch maps to C.
- Should editing a template update all its placed cards, or by default fork into a new revision? Recommend **fork for one instance, opt-in to update all** in the future formal architecture.
- Should personally created template slots follow main Portfolio Context or be independently pinned? Recommend default follow main with explicit per-card pin, retaining proper subject/cut display.
- Scope of saved visual preference: browser/user/workspace/screen/window/account and access controls; formal persisted DTO needed, do not equate local browser state to Git record.
- Source field exactness: UI01 read models vs UI08 portfolio/asset types; necessary currency, Source/Cut/Quality & UNKNOWN/STALE; 64-finding crosswalk still outstanding.
- `D1` stays OPEN until Owner explicitly says no changes and accepts. The v1.1 design package will be integrated with all 19 UI and MA10-U01..U06 only during final pre-Coding handoff.