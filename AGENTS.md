## CURRENT AUTHORITY — RECOVERY DECISION CHECKPOINT 4

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

台灣期貨量化研究、回測與未來交易平台。primary branch 為 `master`。GAP-08ABCD 已完成/接受；GAP-08EFGHI 原始 35 leaves / weight 151 runtime 已於 `6b62239bca1d11543944f9f078e577e16010bcbf` 完成並通過 tests，但目前仍為 ARCHITECTURE_ACCEPTANCE_HOLD，禁止再次執行 runtime 或標記 ACCEPTED。ADR-002 已正式決定 R-01、R-02、R-03A/B/C/D 與 R-04A/B/C/D/E；R-03 整體 DECIDED，R-04 仍 IN_PROGRESS，尚餘 R-04F/G/H。R-03 與 R-04 已新增 operational recovery/evidence correction scope，明確位於原 35/151 之外，尚未重新計權/授權。R-14/GAP-DATA-001 記錄 market-data completeness/gap detection 後續需求。PostgreSQL 17/18 仍為 PENDING integration targets；K520 仍屬 GAP-09；Level 3B 仍 NOT_ENABLED。

Primary source of truth 與必讀順序：

1. `AGENTS.md`：agent 導航與執行規則。
2. `docs/CURRENT_STATE.md`：現況與基線。
3. `docs/CURRENT_WORK.md`：目前工作、阻塞、佇列。
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

## CURRENT AUTHORITY — DECISION CHECKPOINT 5A

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

## CURRENT AUTHORITY — DECISION CHECKPOINT 5B

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
