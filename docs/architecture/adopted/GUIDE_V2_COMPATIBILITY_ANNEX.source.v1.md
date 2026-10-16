# Guide v2 必要相容性附件 — candidate v1

狀態：`CANDIDATE / PENDING_HUMAN_EXACT_ADOPTION`。本附件與原 Guide v2 必須共同批准、共同引用；不是獨立授權，也不修改正式來源。

原文：`B3_V1_PROJECT_OPERATING_GUIDE.candidate.v2.md`。原始 SHA256：`dae411b42acba4471307d6291b93c3df7e5f5bb5293ee8b202328e72661803ba`。原 10,498 bytes／102 行完整保留，正文差異為零；本文件是獨立、具名的解釋附件，不沿用原文 Hash 代表附件內容。

## C01 — Human 採納與角色責任

Guide 前言、§1 的 Human Adoption 次序及既有權威優先。§2 Architecture Owner 的「採納」、§6.1「Ultra 完成正式 B3 Architecture Adoption」，均指完成審查、提出具證據的採納建議、準備精確決策包；最終 Architecture Acceptance 必須是具有決策權限的 Human Owner 對 Exact Subject 的明確決定。WORK 的 Gate Owner 是既有流程的檢核、路由及連續性責任，不新建 Acceptance Owner、不自行生成 Grant。

Human 未核准前，本附件、原 Guide、原 B3 決策包均不會自行變成 Accepted。Human 的 B3 設計採納也不代替 P00 Closure、Source Integration、工作單授權、Dispatch 或 Runtime Qualification。

## C02 — 雙軌設計與當前單 Writer

Guide §1／§2／§6 的分軌、同步及並行描述是可支援的開發目標，不能解讀為現行正式並行執行已獲授權。現行 WORK 的 `NO_PARALLEL_EXECUTION`、全局 Runtime Writer Lock、Program V2 `one_runtime_writer=true`、`same_execution_multi_executor=DENIED` 繼續生效。

唯讀分析、接口及 Mock 設計準備可在本次允許範圍並行；實際 Mock／產品寫入另需合法範圍。獨立 Branch／Worktree、不同工具或檔案表面不重疊，都不豁免全局鎖。沒有已接受且已驗證的 Scoped Writer Successor 時，由唯一既有 WORK 序列施工，仍可交付同一 Cohesive Package。

未來正式多 Writer 必須由原治理 Owner 先固定授權範圍、互斥路徑、共享 Contract／Migration／Integration 的序列責任、Lease／CAS／撤權／Crash／Unknown Outcome／Resume 邊界，完成必要獨立 Qualification，並走既有受控 policy successor 流程。本附件不啟用該功能、不建立第二套 Scheduler／Controller。

## C03 — Executor 可替換，Authority 不繼承

Architecture、Contract Ownership、WORK、Implementation、Integration、Independent Review、Human Acceptance 是固定責任；工具配置是偏好。CODEX 主要路線與 UI／UX 初始工具配置不構成永久 Domain 專屬權，也不更改既有固定政策原文。

同契約、風險及權威下的合格工具切換，不需重做整體 Architecture Adoption；但必須重驗同一 Unit／Feature／Architecture Revision／Source Head／DTO／Oracle／Allowed Scope、依賴結果、實際 Executor Capability／Result Adapter、Current Authority、Capacity／Budget／Context／Review。Local LM 的研究建議權限不自動轉為 Coding Writer 權限。

切換前保存 Durable Checkpoint、Diff、測試、成本與 UNKNOWN 原因及 STOP 狀態；依既有規則結束原 Writer、檢查 CAS／Head，取得合法後續 Invocation。若 Grant 綁定 Actor／Profile，先取得必要的合法修訂。禁止重用 CONSUMED Grant、冒用 Invocation、同 Execution 多 Executor、重置 Unit 身份／進度／Budget。已 invoked execution 的 SAME_EXECUTION Resume 依原規則，不能藉「換工具」重建授權。

## C04 — 風險標籤與必要 Regression

Guide L1～L4 使用 `B3_CHANGE_RISK.L1`～`L4` 作顯示及測試選取標籤，不改寫 AGENTS 的 LEVEL 1～3、Automation 等級或 closed schema 的既有 enum。風險由實際改動及完整影響閉包決定；Source／Registry／權威／資金／Order／Fill 等變更及其直接 Consumer 最低按相關 L3 要求，不能因檔案是 UI 或稱 MVP 而降級。真正 SQL／Migration／Restore／Broker／Controller／Release 操作保留相應 L4 授權及環境資格。

影響選取不能刪除既有授權指定、Wave-final 或相關契約明定的 Full Regression／Independent Review。L1／L2 標籤不自動豁免原工作單要求。重要 Finding 的 Regression 使用原 ID、原反例、修訂、Trigger、Gate、Run／Evidence；未執行維持 NOT_RUN／UNVERIFIED，Manual／Environment／Independent Gate 不冒充自動測試 PASS。歷史 Source Pair PASS 不等 Trusted Reading、Fresh Current Compile、SQL Durability 或實作結果。

## C05 — Code Complete 與事前 Rollback

完整 B3 Code Complete 才觸發 Guide §5 的全面重整規劃，不是 MVP 完成或架構採納。觸發仍不等於已授權移動檔案、資料或 Git 歷史；重整需獨立 exact scope／grant、單 Writer、必要保全與回退能力。

§5 流程末端的「Rollback 計畫驗收」指重整後再驗證回退證據，不是允許先搬移、之後才準備 Rollback。第一個實體異動前，必須已有經檢查的 Inventory、Dry-run Map、來源及歷史保全、可執行 Rollback Plan、必要復原驗證及操作授權；結束再核對全套 Regression／Build／E2E／Fresh Review／Rollback 結果。

Code Complete 不等 Release Ready 或 Runtime Qualified；原有 V1／B3 義務與尚未取得的資格逐項保留。

## C06 — 暫存清理、歷史 Hash 與 Git 保護

「未被引用」不等於可刪除。只可在明確分類、審核與授權清單內處理真正可再生、非受保護的生成物／暫存副本。原始內容、不可再生資料、Private Artifact、Git Blob、Receipt、Review／Execution Evidence 及必要歷史不得因此刪除或改寫。

移位後修復的是新版本 Import／Reference／Consumer Binding／Successor Manifest；原歷史 Path／Hash／Receipt 不改寫，由不可變的舊新映射承接。SQL／Artifact Store 實體移動及 Git main/master/P00 歷史整合另取精確授權；不因 Code Complete 或整理而自動 Merge／Push／刪分支。當前正式來源仍為 master，最終 main 政策不表示遷移完成。

## C07 — 唯一 SOP 入口與採納範圍

未來 `docs/PROJECT_OPERATING_GUIDE.md` 只作穩定 SOP 入口，引用本 Guide 的原始內容、此必要附件、Human 精確決策／Accepted Architecture Manifest 與既有治理程序；動態 Current／NEXT／Writer／Quota 仍由 CURRENT_STATE、Program V2、Machine Policies 與 Work Order Lifecycle 取得，不複製第二套狀態機。

原 `B3-V1-ADOPTION-20261015-v1`／Scope SHA256 `ff5fbb4b378dcb9aac91d4a0b55474a8ed9de944121593f7baa441c6f4bd1b01` 保持原文、原範圍，仍排除當時未讀 Guide。這次 Guide 全文與本附件由另一個具名政策 Scope 批准，再以一次雙項決策請求連接；不把 Guide 靜默加入原 Scope。

本附件只澄清既有權威與安全邊界，不解除原 R02／R06／R08、C3→C5→C6、P00、Implementation、Git、SQL、Runtime 或 Release Gate。必要的真正語義／Authority 變更仍走原 Owner 的明確 Amendment，不由本附件代理。
