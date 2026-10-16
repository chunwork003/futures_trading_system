# B3 V1 統一開發與專案整理原則（候選 v2）

> **文件狀態：CANDIDATE / 待正式採納**  
> 用途：Architecture Adoption 後供架構、規劃／調度、施工、整合與審核角色共用的工程工作規則；實際開發工具可替換。  
> 本文件不授予 Architecture Acceptance、P00 Closure、Work Order Dispatch、Git Merge、SQL Migration、Broker、Runtime 或 LIVE 權限。  
> 動態狀態與實際權限仍由現有 `AGENTS.md` → `docs/CURRENT_STATE.md` 及既有權威治理機制解析；本文件不得成為第二套 Current State / Controller。

## 1. 固定目標與開發節奏

- **正式成果：完整 B3 V1**。MVP 是內部里程碑，不縮減已承諾的完整 B3 V1 功能。
- **採納／授權順序**：固定審核候選 → Human Architecture Adoption → 既有 P00 與依賴資格判定 → WORK 編製並取得各 Work Order 授權 → 分軌施工 → 契約整合／測試 → V1 Code Complete → 最終 Repository 實體重整 → 全面回歸／Release Qualification。
- 規劃、唯讀盤點可先進行；隔離 Mock 原型須獨立授權；正式 Coding、資料庫變更及 Broker/Runtime 行為不得依本文件自行放行。
- 三種交付里程碑：**MVP（完整垂直切片）→ 正常開發（完整功能擴展）→ 完整 V1（全功能與正式資格）**。
- 四級檢核：L1 普通 UI／展示、L2 API／研究與一般整合、L3 資金／訂單／身份／持久化／Registry、L4 高風險 Runtime／Restore／Broker／Release。依實際影響升級，不因稱作 MVP 而降低安全要求。

## 2. 前後端雙軌並行與單一契約

**固定的是責任與契約，不是工具名稱或永久分工**

- **Architecture Owner（目前以 Ultra 承擔）**：正式架構、重大跨模組衝突、採納與高風險判斷；不審查每個普通 UI 或小功能。
- **Planning／Orchestration／Gate Owner（目前由 WORK 流程承擔）**：以固定 Unit ID 建立 Cohesive Work Packages，維護依賴、來源、成本、檢核等級、權限與整合次序；不因 Intake PASS 自動給施工權限。未來可以替換其實作工具，但不能移除既有 authority/state-machine gates。
- **Implementation Executor（可由 VS Code + Human + GPT／LM、CODEX 或其他合格執行工具擔任）**：依已授權工作單實作 UI、API、Core、測試或隔離研究；每個工作包獨立選擇執行者，不把前端／後端永久綁定某一工具。
- **Integration Owner（現由 WORK 協調具名責任者）**：固定共用 Contract／Mock／測試基準，驗證不同 Executor 的輸出，處理受控合併、依賴與 E2E 覆蓋；整合 PASS 不替代正式採納。
- **Independent Reviewer**：依 L3／L4 或跨權威語義變更的要求獨立審核；必須與作者角色分離。
- **Human Owner／Operator**：重大架構／權限決策、必要的產品視覺驗收及正式釋出授權。

**當前偏好（非硬性政策）**：VS Code + Human + GPT／LM 偏重 UI／UX、視覺迭代、Mock MVP 及隔離資料庫測試；CODEX Sol High 偏重 API／Backend／Research／Core。未來可以由 LM、CODEX 全包或其他組合承擔，只需同等契約、能力、測試、成本、權限與獨立性證據。VS Code 是開發環境，不是另設的治理主體。

**工作包執行者選擇規則**：WORK 在 Dispatch 前依任務類型、執行者能力及可用性、預估／實際成本、契約隔離、風險等級、授權與分支 Writer Lock 決定。執行工具變更不得改動已接受 API／DTO、Source／Revision、驗收準則或繞過 Governance Gate；如需改變 Authority／Contract，先走正式修正路由。

**雙軌施工前必備 Contract-First Gate**

1. 對應已採納 Unit ID、API Operation ID、UI Identity、相依版本、正式 Source Manifest／Hash。
2. 固定且版本化的 BFF OpenAPI／Python OpenAPI、Request/Response DTO、驗證、錯誤、授權、重試／冪等語義；React 不直接繞過 BFF 存取 Python 或交易資料庫。
3. 同一版本契約產生或驗證 TypeScript 型別、Mock Fixtures、後端 DTO／Contract Tests；Mock 不能自訂與後端不同的業務語義。
4. 共用成功、空資料、載入、錯誤、衝突、拒絕等情境；契約不匹配則阻斷整合，不靠前端臨時欄位轉換掩蓋。
5. 分離 Git Worktree／Branch，避免同一 Writer 區域競爭；正式 Schema／Migration 由具名持久化責任者管理，不由任一 UI 執行者直接修改正式資料權威；隔離資料庫測試可由獲授權工具執行。

**工作包完成判準**

- UI 包：畫面可操作、契約版號一致、基本自動測試與人工視覺驗收證據。
- Backend 包：功能測試、負例、必要整合／持久化測試、資料來源與版本證據。
- Integration 包：UI Mock → 真實 BFF／API Adapter 切換、契約一致、端到端研究流程、異常情境與 Regression 全部通過。
- `CODE_COMPLETE`、`REVIEW_PASS`、`ACCEPTED`、`RUNTIME_QUALIFIED` 必須分開紀錄，不能互相代替。

## 3. 固定文件規則與單一入口

最少量共用導航：

| 文件／類別 | 唯一責任 |
|---|---|
| `AGENTS.md` | 角色重進入入口及閱讀順序；不自授權 |
| `docs/CURRENT_STATE.md` | 既有動態權威／工作狀態，依現行規則維護 |
| `docs/PROJECT_OPERATING_GUIDE.md` | 本文件獲採納後的穩定工程 SOP；不複製動態狀態 |
| 正式 Architecture Baseline Manifest | 已採納的 B3 Source／Revision／Hash、16 章、19 UI、95 API、96 Units 的精確索引 |
| 既有 Program／WORK／Authorization | 工作單資格、授權、實際執行與費用；不可另起第二套 Controller |
| Historical Review／Evidence Index | 只讀定位歷史候選、Finding、審核與執行證據 |

- 文件狀態至少能識別：Accepted/Active、Candidate、Review-Ready、Superseded、Historical、Blocked；映射既有正式機器狀態，不用新標籤取代現有權限判斷。
- 既有歷史版號、SHA、Receipt、Review、Execution 不得被覆寫或刪除。普通 CODEX 只取本次 Work Order 的有效 Source Closure，避免載入全部歷史。
- **現在只整理指標與入口、釐清來源；不執行大範圍檔案搬移。**

## 4. Findings → 永久回歸檢核 → 低成本持續優化

每一個重要新 Finding 需建立或連結一筆既有正式紀錄，不得重複建立平行帳本；至少包括：

`Finding ID / Root Cause / Source & Impact / Minimal Reproduction / Expected vs Actual / Fix Reference / Regression Test ID / Trigger / Risk Level / Owner / Evidence / Status / Cost`。

- **可確定性重現**：修復時建立會先失敗、修復後通過的測試；負例驗證不可省略。無法自動化則標記 `MANUAL_OR_ENVIRONMENT_GATE` 和理由，不能假報 PASS。
- 依受影響檔案、Unit、Source／Consumer 對應啟動 Regression，不每次一律執行全部架構檢查。關鍵版本／Hash／交易不變條件的最低 Gate 不得為省成本而移除。
- 必須區分 `PASS`、`FAIL`、`NOT_RUN`、`BLOCKED`、`UNVERIFIED`；狀態由實際證據得出，不由作者自述取代。
- WORK 週期性檢討同根因再發率、每包修正次數、測試時間、假陽性、CODEX 預估／實耗 Token、獨立審核成本。改善測試選取與 Context，不降低 L3／L4 的必要標準。
- 歷史問題只修復、無新回歸測試且無正式例外理由時，不可宣稱「已完成防重現閉環」。

## 5. V1 全部程式完成後：一次正式的 Repository 全面重整

**觸發條件**：完整 B3 V1 產品程式、相關工作包與必要整合已達 `V1_CODE_COMPLETE`；此時啟動獨立的 `POST_V1_REPOSITORY_RESTRUCTURE` 工作流。重整位於最後 Release Qualification 前，不與一般功能 Coding 混在同一工作包。

**重整目標**

1. 建立統一的程式、API、前端、資料庫、測試、文件、架構、治理、樣本、工具、發布及歷史證據位置。
2. 統一命名、來源身份、模組 Owner、依賴方向與索引；剔除未被引用的暫存副本與可安全移除的冗餘生成物（先分類、審核、留痕）。
3. 歷史審核、原始 Bytes、SHA、Git Commit、Receipt、版本及採納紀錄**保留不可變**；需要新路徑時使用有證據的搬移映射與必要的新版本引用，不改寫歷史證據。
4. 產出可供未來新投資／其他模組重用的**一般化專案目錄範本**，區分通用治理模板與此專案的交易領域契約，不直接複製產品私有權威。

**必要步驟與 Gate**

`全量 Inventory → 權威/歷史/生成/暫存分類 → 新目錄 RFC → 引用圖及影響評估 → Dry-run Migration Map → 授權及單 Writer 執行 → 移位/Import 修復/指標更新 → Hash 與歷史完整性驗證 → 全套測試/前後端 Build/隔離資料庫與端到端驗證 → Fresh Review → Rollback 計畫驗收 → Release Gate`。

- Git `main`／`master` 與 P00 原歷史要分別保護，採明確審查及安全整合；不 force-push、不覆寫不可變歷史。
- 不能直接大量 `git mv`、刪歷史、改掉被固定報告引用的來源，或在未測試情況下搬動 Python Package／Web 工作空間／DB Migration。
- 重整成功判準：**可追溯、單一最新入口、零失效的必要引用、全量回歸與端到端流程通過、具有可執行的回退方案、產出新專案可重用骨架**。

## 6. 近期推進順序

1. Ultra 完成正式 B3 Architecture Adoption，核對 P00 與既有 Gate；採納審核不自動授權施工。
2. 待採納決策後，確認本文件與既有政策相容；將獲接受的規則納入唯一工程入口。新增指標而不搬動歷史資料。
3. WORK 依真實 96 Units／95 API／19 UI 編出契約先行、前後端可平行的 Cohesive Work Packages 與 L1～L4 Gate，逐包指定可替換 Executor 並取得必要授權。
4. 預設由 VS Code + Human + GPT／LM 優先 UI／MVP／視覺與隔離驗證、CODEX 優先後端功能；必要時由 LM、全部 CODEX 或其他合格工具依固定 Contract 同步施工，角色可替換而權限／品質 Gate 不可省。
5. 整個 V1 期間積累 Finding／Regression／成本回饋；達 `V1_CODE_COMPLETE` 後才執行全面實體資料夾重整。

> **核心原則：現在固定規則和契約，開發期間持續累積回歸；等完整程式完成後，再做一次有控制的整體目錄與資料定位重整。**
