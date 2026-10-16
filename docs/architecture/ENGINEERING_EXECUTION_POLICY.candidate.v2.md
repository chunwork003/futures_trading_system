# Architecture／Engineering Execution Policy — 有界路由 Successor 候選

Policy `candidate.v2`；來源：Human 最新「全系統架構整合、Git 主線修復與持續工程規格建構」；狀態 `DESIGN_DRAFTED_PENDING_REVIEW_ADOPTION`；runtime activation `NOT_GRANTED`。

本候選是 v1 的明確 successor，**不改寫** `ENGINEERING_EXECUTION_POLICY.candidate.v1.md`（raw SHA256 `64d1402c78806ca9f476038e7fb92f740b00fbeac298caa9069d185f8d17d8bc`）。v1 來源曾指定 CODEX Sol 6.1 High 為主要執行端；最新 Human 請求改為最低合格總成本優先，本機 LM 符合客觀驗收時優先，接口穩定時合理拆分，不足或高風險才 Sol High／CODEX／更高模型。本差異只透過新版本採納，不默默修改既有 R07 或 Machine Policy。

Ultra／existing Architect 保留完整架構責任；WORK 是唯一編譯、成本、依賴、路由、writer、STOP／Resume、Intake 管理者。具體契約與能力資格見 [MA14](multi_asset/14_ENGINEERING_EXECUTION.md)。能力、授權、依賴、測試及獨立審核先於價錢；最低成本包含修正、整合與審核，不只單次 token 單價。

共用 Unit／Source／Chapter／Test／Result／Cost／STOP 契約不因模型切換變更，身份、權重、scope、grant、budget、acceptance不重置。`same_execution_multi_executor = DENIED`；durablecheckpoint與singlewriter條件沿用 MANUAL_EXECUTOR_FALLBACK。GPT＋VS Code 是 client/人工套用路線；LM建議可用 HUMAN_DIALOGUE，LM直接改檔/測試必有 actual writer profile、exactgrant、resultadapter及客觀qualification，不能冒稱既有 CODEX mode。

六因素 routing 保留：complexity/risk/uncertainty/contractcompleteness/value/cost。無LMcohort資格或高風險contract不完整時 HOLD／highercapability／Architectdecision；quota不足保留原工作、選其他合法eligibleunit或等額度，不降低review。Token/Time/Cost actual無法取得須UNKNOWN/null+reason，不把sharedquota百分比當taskcost。

Sourceintegration、正式adoption、implementationgrant、runtimequalification分開。此檔不授權Compiler、Controller、SQL、broker、migration、Commit/Push/Merge或coding；採納需 exactv2subject＋compatibilityreview＋existingHuman/Intake gate；acceptedclosedpackage/authorization/execution schemas用versionedcompanion/adapter。

Done：v1hash不變、v2sourcebound、WORK唯一、capability/成本/安全規則可測、executorcontinuity與resultintake相容、完整Architectureindependentreview、Ownerexactadoption。普通codingtasks不要求Ultra重審；章節/高風險跨模組變更必freshIndependentReview。
