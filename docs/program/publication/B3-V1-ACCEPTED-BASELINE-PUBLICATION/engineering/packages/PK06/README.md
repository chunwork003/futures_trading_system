# PK06 — 完整 Strategy Lab 研究閉環

狀態：SPEC_READY（文件可讀）／PLANNING_COMPLETE／QUALIFICATION_PENDING／IMPLEMENTATION_NOT_AUTHORIZED。EXECUTION_READY=false。

AST Inbox→人工 Archive→Builder→不可變 Graph／Code／Snapshot→Research／六比較→Library／AI Analyst。

## 開始閱讀

先讀本包 `ENGINEERING_SPECIFICATION.json`，再依下列 Unit 的 exact source／base plan／v9 companion／model closure／operation spec／fixture／negative oracle；不載無關整體架構。此處每個連結都是規劃文件，不是 Grant。

| Unit | UUID | 實作目的 | 原上游 |
|---|---|---|---|
| [MA04-U01](units/MA04-U01.md) | 332a4057-004a-48e0-8f8c-199d8126c497 | AST-only Inbox與人工Capture | MA02-U01, MA03-U01 |
| [MA04-U02](units/MA04-U02.md) | e0279c82-8eec-4de5-80c9-7e1b7d78a48f | Feature Library／Builder graph | MA04-U01, MA02-U01, MA03-U01 |
| [MA04-U03](units/MA04-U03.md) | 9e7f20fa-f68c-45a0-8ed0-e841d9a543da | Code／Branch／ImmutableSnapshot | MA04-U01, MA02-U01, MA03-U01, MA04-U02, MA03-U04 |
| [MA04-U04](units/MA04-U04.md) | cabd3d4c-e10a-4a60-a1c2-8e85cd44684f | 研究Methods與resultmetrics | MA04-U01, MA02-U01, MA03-U01, MA04-U03, MA03-U03, MA03-U04 |
| [MA04-U05](units/MA04-U05.md) | 5fec1579-d8c0-45a9-b658-3eb47efb5a31 | 六比較／Library manual approval | MA04-U01, MA02-U01, MA03-U01, MA04-U04 |
| [MA04-U06](units/MA04-U06.md) | 430b85dc-75e0-4811-b798-3fcc76f1f34e | AI Analyst／沙箱權限與部署adapter | MA04-U01, MA02-U01, MA03-U01, MA04-U02, MA04-U03, MA04-U04, MA04-U05 |

## 精確操作及驗收

各 Unit JSON 已保留原完整 row/base plan、Feature／Requirement revisions、input/output、API DTO欄位、唯一 Producer／Consumer mode、Mock 原文、negative cases、proposed path/preimage、protected blobs、qualification、具體 postcondition 與 Actual evidence要求。

本包直接負責的 API：analyzeInboxSource, applyAnalystSuggestion, applyBuilderEdit, approveLibraryException, approveLibraryRelease, archiveResearchBranch, cancelAnalystRun, cancelResearchRun, captureInbox, cloneResearchBranch, createArchivePlan, createLabSimulation, createResearchBranch, createResearchRun, dispositionInbox, executeArchivePlan, generateCode, getAnalystRun, getArchiveOperation, getGraphDraft, getLabSimulation, getLabSimulationCounters, getResearchBranch, getResearchBranchHistory, getResearchRun, getSourceAnalysis, listComparisons, listFeatures, listGraphDrafts, listLabSimulationObservations, listLibraryReleases, listResearchBranches, listResearchRuns, recoverLabSimulation, saveComparison, saveFeatureDraft, saveGraphDraft, saveManualCodeRevision, sealResearchSnapshot, startAnalystRun

Frontend／BFF／Core／Persistence責任沿唯一Producer。Pure UI/UX可在合法範圍集中修正；API/DTO、資料完整性、Capital/Order/Fill或Authority漂移立即HOLD受影響路徑。

Finding Regression候選：按變更觸發器查既有64筆backlog，不創造無關新任務。

所有測試是規格，尚未實作或執行；原強制Full／Wave-final／Independent Review不能由影響選取免除。

取得有效授權後：Contract → Authorized Coding → Targeted Tests → Integration → Regression → 原Review/Intake/Acceptance → Re-entry。尚缺source assembly、Profile/Adapter、WO/Grant/Budget/Writer等，不能執行。
