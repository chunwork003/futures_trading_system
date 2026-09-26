# GOV-01 CURRENT RE-ENTRY GUARD

**CANONICAL CURRENT AUTHORITY：`docs/CURRENT_STATE.md`**

This file is the agent re-entry guard and navigation surface。

It does NOT independently establish Runtime Authorization。

Architecture Decision Baseline：`22ceaa729ab6e9da9c00ae52e09ae7116be5a743`。

Governance Planning Baseline：`f45742d9d16165f87f145f0d2bdc8d530772e5ee`。Correction-Freeze Baseline：`93fb846a9c9cd61eea44427a86a542fc95f9ac28`。Latest completed bounded execution：`docs/work/GAP08_C25_CLOSURE.md`。

Runtime Candidate：`6b62239bca1d11543944f9f078e577e16010bcbf`。

Architecture Acceptance：HOLD。

Runtime Conformance：NOT ASSERTED。

Production Readiness：NOT ASSERTED。

Runtime Authorization：NOT_AUTHORIZED。

Post-5E K520 / BG-01～BG-07 / Expanded Correction-Scope Map / Delta-to-Contract conclusions are recorded in the Correction-Freeze planning package；they remain planning inputs and are not a new Architecture Decision Baseline。

Current execution action：create the explicit Wave-1 Runtime Source Modification Authorization checkpoint from `docs/work/GAP08_WAVE1_EXECUTION_PACKAGE.md`；C02 and Wave execution remain NOT_AUTHORIZED until that separate checkpoint is committed。

C25 is COMPLETE / VERIFIED and its bounded authorization is consumed。Migration 0004 exists but is NOT_EXECUTED；actual PostgreSQL、C02/C04/C05/C18/C21/V05/V07 and Wave execution remain NOT_AUTHORIZED。

Historical authority/checkpoint sections below are preserved for audit and are not current runtime authorization。

## HISTORICAL AUTHORITY RECORD — RECOVERY DECISION CHECKPOINT 4 — SUPERSEDED

Decision baseline：`11ead24d4f09ead611243c19aab982f09756f172`。

ADR-002 R-01、R-02、R-03A/B/C/D and R-04A/B/C/D/E/F/G/H are architecture-decided。

R-03 overall：DECIDED。

R-04 overall：DECIDED / IMPLEMENTATION_CORRECTION_REQUIRED。

Architecture acceptance remains HOLD；GAP-08EFGHI original 35 leaves / weight 151 remains IMPLEMENTED CANDIDATE / NOT ACCEPTED。

Do not rerun runtime and do not mark GAP-08EFGHI ACCEPTED。

Next action：map、bound and reweight the expanded correction Work Package，including R-03/R-04 correction scope and explicit classification of R-12/R-13/R-14/K520 + broker capability gates。

Runtime Authorization：NOT_AUTHORIZED。

This CURRENT AUTHORITY supersedes older R-04 OPEN wording elsewhere in historical sections。

# futures_trading_system — Agent Guide

## 專案與導航

台灣期貨量化研究、回測與未來交易平台。primary branch 為 `master`。

目前唯一 canonical CURRENT governance projection 位於 `docs/CURRENT_STATE.md`。

Original runtime candidate remains NOT ACCEPTED；latest completed correction runtime commit is 940f54c6d9b4ed7bf0e1d3c8627b49be3fdae495；Architecture Acceptance = HOLD；Runtime Authorization = NOT_AUTHORIZED。

R-01～R-14 已 closed/classified；K520 defer confirmation、BG-01～BG-07 classification、Expanded Correction-Scope Map、Delta-to-Contract、materialized correction leaves、DAG 與 reweight 已記錄於 `docs/work/GAP08_CORRECTION_FREEZE.md`。

V06 + C01 + C22 + C11 + C23 + C24 + C25 已完成；frozen P1 COMPLETE，P2 COMPLETE。目前沒有 runtime leaf 取得授權；C02 只是 next runtime candidate。

Primary source of truth 與必讀順序：

1. `docs/CURRENT_STATE.md`：唯一 canonical CURRENT governance projection。
2. `AGENTS.md`：agent re-entry guard、執行規則與 current-state pointer。
3. `docs/CURRENT_WORK.md`：目前工作、阻塞、佇列。
4. `docs/CODEX_EXECUTION_WORKFLOW.md`：CODEX/VIBE detailed execution workflow owner。

Correction-Freeze execution planning source：`docs/work/GAP08_CORRECTION_FREEZE.md`。

Historical bounded authorization source：`docs/work/GAP08_AUTHORIZATION_V06_C01.md`。

Previous bounded execution closure：`docs/work/GAP08_C01_CLOSURE.md`。

Latest bounded execution closure：`docs/work/GAP08_C25_CLOSURE.md`。Last consumed authorization：`docs/work/GAP08_AUTHORIZATION_C25.md` + `docs/work/GAP08_AUTHORIZATION_C25_AMENDMENT_01.md`。Current bounded runtime authorization：NONE。
4. `docs/GAP_REGISTER.md`：有序 GAP。
5. `docs/AI_HANDOFF.md`：架構決策與交接。
6. `docs/V1_SYSTEM_BLUEPRINT.md`：V1 工程施工圖 master index；正式 baseline 後由 ACTIVE 引用相關 Blueprint IDs。
7. `docs/DEVELOPMENT_LOG.md`：歷程與進度。

Historical / supplemental documents：`docs/PROJECT_STATE.md`、`docs/DEVELOPMENT.md`、`docs/BACKTEST_ENGINE.md`、`docs/DATA_ARCHITECTURE.md`。`docs/ARCHITECTURE.md` 與 `docs/ROADMAP.md` 為 authoritative documents，不得降級為 supplemental。

不得刪除舊文件。若 legacy / supplemental 文件與 primary source 衝突，不得自行猜測；以 primary source 的已確認決策為準，登錄或更新 GAP-DOC-001。若為重大 architecture semantics conflict，升級為 LEVEL 3。

## 執行規則

- 每個 Work Package：precheck → 修改 → targeted tests → full regression → `git diff --check` → scope validation → commit → push → verify → final report。若 ACTIVE 明確指定 deterministic docs closure 由人工處理，runtime executor 完成 runtime commit/push/report 後必須 STOP；CURRENT_STATE / CURRENT_WORK / GAP_REGISTER / DEVELOPMENT_LOG 由人工 closure。
- 禁止 silent unrelated fix、silent architecture change、scope 外修改、rewrite history、force push。
- 不得修改 `data/`，除非 Work Package 明確授權；不得提交本機資料、資料庫或 generated assets。
- identifiers 使用 English；重要 comment、docstring、C# XML comment 與文件使用繁體中文，說明用途、責任、上游/資料來源、下游/使用者與非顯而易見商業規則。未來 PostgreSQL 重要 TABLE / COLUMN / FUNCTION 必須加入繁體中文 COMMENT。
- 新問題先登錄 GAP，不以猜測取代設計決策。
- Broker / exchange / live-money semantics 優先使用 `docs/blueprint/SOURCE_REGISTRY.md` 的 S0 / S1 官方來源；來源不足時不得以二手文章猜測。
- Blueprint baseline 啟用後，ACTIVE 必須列出 Implements / Touches / Does Not Implement 的 Blueprint IDs。
- 若 CURRENT_WORK 或 ACTIVE 標示 `HOLD_FOR_BLUEPRINT_BASELINE`，不得開始 runtime Codex execution。

## 可執行工作佇列

- `docs/CURRENT_WORK.md` 是 queue source；先選最高優先且依賴已滿足的 READY mainline item。
- 不得從 queue 直接修改 runtime。必須依 `docs/work/WORK_PACKAGE_TEMPLATE.md` 完整填入 `docs/work/ACTIVE.md`，重新讀取後確認 baseline、dependencies、scope、allowed files、stop conditions 與 acceptance criteria，才可開始。
- ACTIVE 過度簡略、存在 unresolved HARD_BLOCK，或與已確認 architecture 衝突時，不得開始 runtime。
- 發現問題不等於立即實作。READY mainline 存在時，不得因 P2、P3 或 OBS 離開主線；只有 P0 + HARD_BLOCK 可阻止受影響主線。
- Level 3A：每次 autonomous execution 最多一個 mainline Work Package；完成後更新 queue 並停止。每個 failing test 最多兩個 scope-internal correction cycles，仍失敗則依分類 REVIEW 或 HARD_BLOCK。
- Work Package sizing 採效益動態校準：同一 architecture context、transaction boundary、repository family、test set 優先合併；只有 unresolved public semantics、authority/safety boundary、external verification dependency 或明確 debugging isolation 才拆分。不得以固定 leaf 數或固定 5HR% 作為切包目標。
- 不得 whole-repo rescan，除非 ACTIVE 明確要求；沒有 READY item 時不得自行找工作。

## Issue Classification 與模型建議

- Priority 與 Handling 為獨立維度：P0/P1/P2/P3/OBS；AUTO_FIX、RECORD_AND_CONTINUE、REVIEW_AT_CHECKPOINT、HARD_BLOCK。定義與逐項分類以 `GAP_REGISTER.md` 為準。
- Terra：routine implementation、tests、docs、Git operations。Sol：broker semantics、reconciliation、persistence/recovery、複雜跨模組與 live/money safety。Recommended Model 只是建議；Stop Conditions 優先。
- Automation 必須服務 development。runtime executor 只能執行 CURRENT_WORK / ACTIVE 已核准的 mainline Work Package；不得自行增加 automation 系列工作，除非 queue-driven execution 已證明 blocker。

## 人工介入與停止條件

- LEVEL 1：低風險命名、fixture、註解或明確實作細節，可自主執行並記錄。
- LEVEL 2：不阻塞其他工作者，登錄 Pending Decision，固定 checkpoint 集中審核。
- LEVEL 3：Live/money risk、破壞性 migration、架構語意衝突、核心 regression、broker ambiguity、secrets/security、business logic 猜測或重大 scope 擴張。停止該 Work Package，不要猜；互不依賴工作可繼續。
- Checkpoint：08:00、12:00、18:00、22:00（Asia/Taipei）。集中回報 Completed、Tests、Git commits、Current Work、New GAPs、Blocking decisions、Non-blocking decisions、Incidents、Next Queue、Overall progress 及 Estimated remaining effort；不要重複已確認內容。

## 品質原則

Quality > Deadline。7 天是 Dynamic Sprint 目標，不是硬截止。超過 7 天時建立 Delay Review：延遲原因、V1 影響、Post-V1 延後可能、scope creep、低價值過度優化、Work Package 拆分與模型選擇。

方向變更必須遵守 `EXIT → confirm FLAT → re-evaluate → ENTER`；不得 silent direct reversal。

## HISTORICAL AUTHORITY RECORD — DECISION CHECKPOINT 5A — SUPERSEDED

- Authoritative decision baseline before this checkpoint：`462a3d541cb6b0bccc9bb5e3e1a118cd1c2cf351`。
- R-01：DECIDED / AMENDED。
- R-02：DECIDED / AMENDED。
- R-03：DECIDED / UNCHANGED。
- R-04：DECIDED / AMENDED。
- R-05：DECIDED / IMPLEMENTATION_CORRECTION_REQUIRED。
- R-05 RecoveryCut is broader than AccountStateHead revision alone when recovery-critical evidence may change without account_revision advancement。
- No physical per-dependency high-water schema is prescribed。
- R-05 VALID is local restore consistency only；VALID != broker-current / READY / Strategy READY / trading authority。
- Runtime Authorization：NOT_AUTHORIZED。
- Architecture Acceptance：HOLD。
- Next：R-06 + R-07 Recovery Boundary Cluster。
- Do not begin runtime correction until the expanded correction Work Package is later frozen、reweighted and explicitly authorized。

## HISTORICAL AUTHORITY RECORD — DECISION CHECKPOINT 5B — SUPERSEDED

- Authoritative architecture baseline before this checkpoint：`c131d6bd04212d302259b0571bfef91084196f76`。
- R-01：DECIDED / AMENDED。
- R-02：DECIDED / AMENDED。
- R-03：DECIDED / UNCHANGED。
- R-04：DECIDED / AMENDED。
- R-05：DECIDED / IMPLEMENTATION_CORRECTION_REQUIRED。
- R-06：DECIDED。
- R-07：DECIDED。
- Strategy recovery unit = StrategyInstance；no global strategy watermark。
- Required strategy participation comes from exact authoritative policy/config version；runtime presence is not authority。
- ExecutionReady、StrategyRestoreValid、StrategyTradingReady and DecisionCohortTradingReady are distinct。
- ReconciliationCase primary scope = exactly one BrokerAccount。
- Open/unresolved ReconciliationCase alone is not readiness authority。
- Readiness-affecting reconciliation evidence participates in complete RecoveryCut currentness。
- R-09 remains OPEN and owns StrategyInstance/config lifecycle identity authority。
- Runtime Authorization：NOT_AUTHORIZED。
- Architecture Acceptance：HOLD。
- Next：R-08 + R-09 identity/config authority cluster。

## HISTORICAL AUTHORITY RECORD — DECISION CHECKPOINT 5C — SUPERSEDED

- Authoritative baseline before this checkpoint：`47822446fe1b5149780ddd537fd99b460882d66d`。
- R-08：DECIDED / IMPLEMENTATION_CORRECTION_REQUIRED。
- R-09：DECIDED / IMPLEMENTATION_CORRECTION_REQUIRED。
- StrategyInstance identity、instrument binding、config version、implementation revision and DecisionPolicyVersion are distinct authorities。
- Legacy symbol is not canonical execution authority。
- Governing-context transition supports PRE_TRANSITION / TRANSITION_IN_PROGRESS / POST_TRANSITION recovery classification。
- TRANSITION_IN_PROGRESS never grants normal strategy/cohort trading readiness。
- Runtime Authorization：NOT_AUTHORIZED。
- Architecture Acceptance：HOLD。
- Next：R-10 formal closure，then R-11 clock authority。

## HISTORICAL AUTHORITY RECORD — DECISION CHECKPOINT 5D — SUPERSEDED

- Authoritative baseline before this checkpoint：`d5ec87c00081b97340a59bb47521d65db46131c4`。
- R-10：DECIDED / IMPLEMENTATION_CORRECTION_REQUIRED。
- R-11：DECIDED / IMPLEMENTATION_CORRECTION_REQUIRED。
- Initial canonical expected snapshot must resolve through EXPECTED_STATE_INITIALIZED and one complete revision-1 provenance closure。
- EXPLICIT_FLAT never derives from missing state / empty broker observation / reconciliation MATCH。
- BROKER_SEED is initialization-time position genesis and requires complete approved material provenance。
- occurred_at / received_at / observed_at / recorded_at / captured_at / effective_at are distinct semantics。
- received_at is fixed by first successful durable canonical acceptance of immutable evidence identity。
- Unknown/unverified broker occurrence time is never silently fabricated。
- Timestamps never replace sequence/revision/frontier causal authority。
- Runtime Authorization：NOT_AUTHORIZED。
- Architecture Acceptance：HOLD。
- Next：R-12 ReconciliationRun audit contract。

## HISTORICAL AUTHORITY RECORD — DECISION CHECKPOINT 5E — ARCHITECTURE RECORD

- Authoritative baseline before this checkpoint：`a68ca31d969dd691cae4fe01e904ef81239de453`。
- Runtime candidate：`6b62239bca1d11543944f9f078e577e16010bcbf`。
- Runtime candidate != authorized runtime baseline。
- R-12：DECIDED / IMPLEMENTATION_CORRECTION_REQUIRED。
- R-13：DECIDED / BOUNDARY_CLASSIFIED / IMPLEMENTATION_CORRECTION_REQUIRED。
- R-14：DECIDED / BOUNDARY_CLASSIFIED / GAP-08_ENFORCEMENT_CORRECTION_REQUIRED / GAP-DATA-001_DEFERRED_PRODUCTION_DEPENDENCY。
- No R-12I / R-13I / R-14I。
- R-13 production auth runtime not implemented != authorization requirement waived。
- R-14 full completeness detector deferred != completeness requirement waived。
- R-13 core enforcement/default-deny seam belongs to GAP-08 correction；full production authN/authZ/approval remains L/N/GAP-LIVE。
- R-14 completeness dependency/fail-closed readiness seam belongs to GAP-08 correction；full detector remains GAP-DATA-001。
- GAP-DATA-001 remains Current Blocking = No for GAP-08 correction，but remains a later production dependency。
- Runtime Authorization：NOT_AUTHORIZED。
- Architecture Acceptance：HOLD。
- Recovery architecture free expansion stops absent concrete contradiction/new authoritative evidence。
- Next：K520 defer confirmation -> broker capability gate classification -> correction-scope map -> reweight -> explicit bounded runtime authorization decision。
