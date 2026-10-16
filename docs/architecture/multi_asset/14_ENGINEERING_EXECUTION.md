# MA14 — 唯一 WORK、可替換施工契約與持續工程

Revision `candidate.4`；Owner existing WORK／Compiler／R03／R07／Result Intake。`COHESIVE_CORRECTION_COMPLETED_PENDING_INDEPENDENT_RE_REVIEW` 是本章候選目標，未 formal accepted／qualified／authorized。

## Purpose／Source／Accepted Scope Preservation

沿用 `ENGINEERING_SYSTEM.md`、`OPERATING_MODEL.md`、WORK_ORCHESTRATOR_KERNEL、CODEX_EXECUTOR_KERNEL、MANUAL_EXECUTOR_FALLBACK、Capacity2.2、ProgramV2rev5與已接受 R03／R07成本/Compiler exact scope。URMS/ArchitectureIndex是同一WORK的索引／查詢投影；沒有第二個 Compiler／Scheduler／Controller／Progress／Acceptance Owner。

最新Human RCG修正已明確確認：**CODEX Sol 6.1 High是主要 Coding／Frontend／UI／Tests 執行端。GPT＋VS Code、本機LM是額度不足時的有界替代或輔助。** 舊candidate v1/v2 LM優先來源、已接受 R07與machine policy原bytes保留；最新 Source-Bound Policy Successor只準備設計，未因本章取得模型切換／writer／budget／dispatch資格。

Ultra是全局/高風險Architecture Owner；章節作者自檢不能充當Fresh Independent Review。正式 Authority由 `CURRENT_STATE` 與 machine policies重新取得，不由聊天、manifest舊compiledV1、定時器或quotareset推導。

## Data Model／Public Interfaces／責任

| 物件 | Producer／Consumer／作用 |
|---|---|
| ExecutionUnitPlan / ExecutionUnitPlanArtifact | 作者提出計畫reference／raw18-axis artifact；既有WORK驗 exact章節/source/typedIO/oracle/dependencies。 |
| CompilationProposal | 唯一WORK設計預览；可帶未解 adoption/grant/result/profile，沒有執行權。 |
| ExecutionUnit | 唯一WORK經合法 gates解綁的版本化 companion；不修改原closed package schema。 |
| RequiredEvidenceContract | 執行前證據需求；固定categories/fixture/test IDs/來源/Review Owner，不能補造實際結果。 |
| UnitExecutionResult + ExpectedEvidence | 合法executor提交 exact changed files/diff/source/invocation/testlogs/failed-skipped-untested/cost/RemainingIssues；Review／WORK Intake檢驗。 |
| ExecutorProfile／CostRecord | R07六因素/cohort/toolwriter/context/版本/producer；estimate／actual／quota proxy分開。 |

API `getEngineeringStatus` 唯讀 authority/eligibility/cost/STOP；`proposePlanning`只保存 plan refs、assumptions及未解 gates，不 cast rawplan到ExecutionUnit、不派發。UI Automation／Progress 不能透過 acceptedcheckbox、dispatchbutton、SQL欄位跳既有Owner。

## Execution Unit Contract／精確Schema與Revision

`EXECUTION_UNITS.json`保留96 unit/feature永久ID，每項有新 `candidate.4 plan_revision_id`及immutable predecessor binding。18必需軸：identity、chapter/source、deps、allowed/protected、IO、DBboundary、interface、positive/negative、requiredEvidence、acceptanceGate、risk/capability、estimate、STOP。

`EXECUTION_UNIT_PLAN_SCHEMA.json`是raw serialization；MODEL/TYPE catalog是typed/wire closure；`EXECUTION_UNIT_COMPILER_ADAPTER.md`是唯一WORK的versioned adapter規格。每個unit附3個具體合成正/負/並行或失敗scenario、exact fixture revision、IO schema和semantic oracle；288個設計情境**未執行**。具備精確fixture不是 actual test PASS或可直接Dispatch。

設計依賴固定 exact successor plan IDs。實际qualified result/reuse proof需在 executable compile取得；null結果不是設計圖遺漏，但不能當施工已可用。原接受receipt/schema exactGit source pins不等CURRENT/grant，WORK要重新讀 authority/sourcechangeset。

## Routing／Quota／Cost Decision Table

| Condition | 唯一WORK處理 |
|---|---|
| CODEX額度／能力／合法WO皆適合 | CODEX Sol6.1High主要施工；相同source/IO/fixture/evidence/Review標準。 |
| CODEX額度不足，GPT＋VS Code可合格完整完成 | 保持unit/plan ID，由GPT提供完整patch/commands，本機依合法WO執行，freshinvocation與可信result producer。 |
| CODEX額度不足，LM能合格處理完整穩定單元 | 六因素／qualified cohort／toolwriter profile／客觀測試/成本檢核後，合法LM route或Humanapply；不能改架構。 |
| 單元可安全拆分 | WORK按穩定接口/transaction/safety/qualification邊界編 companion children與integration proof；父acceptance/weight不變，不無限碎拆。 |
| 高風險不可替代、profile未知、來源/授權不足 | WAIT／STOP保存checkpoint；選其他已有授權 eligible工作；不得降tests／獨立Review。 |

模型名稱/可運行不證能力。CapabilityProfile綁executor/model/build/quantization/tooling/context/config版本＋相同risk/contract testcohort及限制。现closedmode僅 CODEX/HUMAN_DIALOGUE：LMdirectwriter另需合法profile+grant+typedresultadapter qualification，不能用本章自己擴權。

Estimate由WORK在 grant前按R07六因素產P50/P75/P90、producer/assumptions/confidence；未取得實測=null+reason。Actual input/output/cache/reasoning tokens、walltime/activeengineeringtime、billableamount/currency/pricingversion由可信producer回收。SharedQuota%=accountwindow狀態，不能換成task tokens/billing；UI不顯0假成本。

## Lifecycle／Concurrency／Error／STOP／Resume

復用既有package/authorization/claim/reservation/dispatch/invocation/completion/intake/review/materialization。newplan/samehash重送用原receipt；sameID/differentdigest conflict；generation/CAS stale拒絕，只有一個exactwriter。不能回填先前invocation或把consumedgrant重新dispatch。

executor切換先durablecheckpoint保存diff/hash/tests/source/cost/invocation/remaining，再合法釋放writer、freshbinding；`same_execution_multi_executor=DENIED`。同unit/feature/chapter/source/credit不重置。recovery/contextrestore不恢復舊lease/eligibility/forecast；freshreentry重證。

STOP：source/hash/drift；未採納核心語義；exact scope/protectedblob/grant衝突；不完整typedfixture；concurrentwriter/stalegen；SQL/Broker/LIVE/Secrets副作用未授；tests超授權correctionbudget；providerdenial；不可替代原始來源缺失。只阻受影響單元，其他合法獨立lane可規劃。

## CurrentContext／持續進度與Token效率

復用R06 TrustedReading：requested/resolved source/hash/revision/coverage/receipt；UNKNOWN不能變ABSENT。最小context=authority+unit+directdependencies/publicinterfaces+relevantclosure+protectedblobs+fixtures+latestSTOP。不得裁non-schema OpenAPI security/components或risk/invocationauthority；128KiB原qualification target仍需C3 contextsuccessor，不以短摘要宣稱合格。

Daily planning只由WORK顯 eligibility/dependency/source/model/cost/uncertainty；lane ordering與DAG各自版本。timer/quota reset觸發reentry而非CODEX啟動；AUTO003Rev2 NOT_AUTHORIZED、AUTO002/acceptedGAP08 closure不因本architecture program重開。R05 accepted progress只聚合唯一正式credit，96units/Ntasks不增分母。

## UI／API／DB／Security／Compatibility

URMS儲存Unit/Task候選、成本/events/ref；Git保正式採納Registry/contracts；SQL Draft不能自accept。RestrictedLM codingprofile無proddata/Secrets/Brokercredentials；MA04 LocalLM research role另scope，只建議/研究artifact，不能寫SQL/Git/交易。API transport從MA10 exacterror/cursor/stream契約，scope含environment/account/role。

新companion透過原Compiler支持的 extension／adapter或經授權 successor，closedpackageSchema不能任意field修改；unsupportedextension=`UNSUPPORTED/HOLD`。Parent package保持 source/context/transaction cohesion與來源追溯。普通routinecoding獨立Review按既有risk契約；Ultra集中章節/高風險跨模組架構，不重審每個普通task。

## Positive／Negative／Concurrency Examples／Acceptance

正：MA14-U01從raw ExecutionUnitPlanArtifact起驗18軸、exacttypedfixtures/dependencyplan，合法grant尚缺只產NON_EXECUTABLE CompilationProposal；MA13-U03從BackupCut起，U06從RestoreRequest三模式起；MA08-U03輸出PAPER SimulationSession。

反：rawplan直接castcompiledDTO；把requiredtest IDs寫成actualPASS；LM優先覆最新OwnerCODEXprimary；換executor重置weight/budget；本機GPTpatch自授Git發布；timer自dispatch；同execution兩writer；從AISuggestion直接Deployment；summary假原privatebytes。

Concurrency：兩compile同planID/d不同hash必conflict；同unit切writer必先停止原claim；source/relation變更後reviewsubject必重新固定；TestResult不在ExactReviewSubjector合法invocation內不得intake。

作者可驗：96永久IDs與新planrevision、wholeDAG、IO/oracle/catalog/sourcehash、requiredEvidence/actualResult分層、Source-Bound最新路由、原blob不變。後續需要Fresh narrow Independent Re-review、原P00 C3→C5→C6/adoption、existingCompiler runtime adapter/result/cohort/switch qualification、active legal WO、真PG/crash/Restore/Broker/PAPER/Controller/Release。**本章不提供任何 executiongrant、正式Acceptance或Runtime PASS。**

## WORK／CODEX／GPT／LM Handoff

後續WORK輸入＝同版plan/catalog/fixture及sourcehash＋adoptedchapter＋exactdeps/result/reuseproof＋activegrant/protectedbaseblobs＋qualifiedprofile/cost/currentcontext。Executor回傳＝UnitExecutionResult，包含exactdiff/source/invocation/commands/rawlogs/fail/skipped/unverified/actualcost或reason/RemainingIssues/STOP。交existingIndependentReviewer/WORKIntake，不能自己接受。

Known limitations：candidate source/fixtures已設計不等測試harness已實作；成本/能力cohort未實測；schema adapter未Runtimequalified；真實migration/Broker/LIVE無授权。全部按各軸標示，不能把未執行改PASS。


## Candidate.5 有界修正承接

Raw34完整保留、CompilationContext及READY/HOLD雙輸出；95操作producer/consumer/mode/oracle closure；不製造Grant、Implementation Evidence、獨立接受或第二Compiler。

唯一詳細契約：`EXECUTION_UNIT_COMPILER_ADAPTER_ADDENDUM.candidate.v5.md`。原已接受範圍與尚未完成qualification保留。


## Cycle 02 有界後繼契約（設計候選；沒有採納或施工授權）

本章的受影響消費者使用 `MA-ARCH-REVIEW-v6-CYCLE02` 的 MODEL／TYPE／API 精確版本。來源與 plan revision 是 `candidate.6`；傳輸協定是獨立的 `MA-DTO-v6`。不得將 `candidate.4/5/6` 當 wire alias。原接受 P00 設計、永久身份、舊 Wave／Feature 語義及 v5 完整前驅 bytes 保留。

Registry：`CC02_AUTHOR_ADDENDUM.candidate.v6.md`、有限內部 producer allowlist、source-file resolver 及封閉來源正文型別。PAPER／compiler／wire／單元：`ENGINEERING_ADDENDUM.candidate.v6.md`。resolver 依原來源 owner、權限、immutable source bytes 與 schema 驗證；capture、索引與 A/B protection 不能互推。compiler 的 HOLD 和 READY 都固定完整輸入；source-compatible 設計檢查與 qualified producer result 分開。

本輪具體測試世界是合成設計預期值，`EXPECTED_NOT_EXECUTED`，不代表任何實際 DB、Broker、PAPER、Controller、還原或執行。`95_OPERATION_VALUE_COVERAGE.candidate.v6.json` 明列尚未補足的正例；negative wire case 不替代 positive domain oracle。舊 v5 fixture 原文保留，但只能作前驅/版本相容或回歸輸入，不能被推導為本輪當前 wire 實作證據。


## Candidate 7 Source-bound Correction

此有界 successor 必讀 `EXECUTION_UNIT_COMPILER_ADAPTER_ADDENDUM.candidate.v7.md` 與固定C2 final Independent Review。只修必要語義及Consumers，保留原P00/R01/03/04/05/07接受範圍、歷史原文與尚未取得的Qualification。作者checked不是獨立PASS或Execution Authorization。
