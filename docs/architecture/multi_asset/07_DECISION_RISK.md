# MA07 — 唯一決策層、資本準入、跨資產風險與 Strategy Group 衝突

Revision `candidate.3`；Owner G Decision/Risk；AUTHOR_CHECKED／FORMAL_REVIEW_PENDING。

## Purpose／Source／Reuse／責任

沿用 G_DECISION_RISK、ADR-001、backtest/decision_layer.py blob e4c7c84ac5d7bbeee3bb45ae4af854c5a2bd35d1、accepted StrategyIntent→RiskDecision→OrderIntent 路徑。新 group/crossassetguard 是有界 companion，**不建立第二個 PortfolioDecisionEngine**。研究建議、UItarget、LMsuggestion 皆 proposal，不是 physicalpositionauthority。

## Model／Inputs／Outputs／Functions

DecisionPolicyRevision：account/group/universe、priority/aggregation/conflict/tie/partialleg policy、entry/exit、budget/resource limits、freshness/requiredstrategyparticipation、riskthresholdsources、effective revision。DecisionInputCut：exact strategyinstance/config/releases、market/completeness、AccountCut/RecoveryCut、capital/reservations、riskpolicy、brokercapability/readiness、authorization/fences；hash 包含所有 decision-affectingdependencies。不以 timestamp 替 cut。

RiskProposal：strategy/group/account/env、instrument_ref、target/side/quantity/unit、reason、release/config、sourcecut；RiskDecision：id、policyref/cut、APPROVED/REJECTED/UNKNOWN、reasons、approvednormalizedaction、requiredreservation/admission、validity/fence；FinalSubmissionWitness：exactapprovedintent、currentcut/capability/auth/fence，任何變更重 evaluate。

`evaluate(proposals,cut,policy)` pure decision；`validate_admission(release,environment,account,qualification)` layeredgate；`revalidate_submission(intent,witness)` 在 economicreservation 與 sendboundary 確認 CAS/currentness；riskresult 不能長時間無 cutcarry。所有 threshold 有 unit/currency/valuationmethod，缺 value 回 UNKNOWN/DENIED 不取 default0。

## Decision Rules／Risk Coverage

保留 `EXIT → confirm FLAT → re-evaluate → ENTER`，不是 samebar silentreverse。策略 requiredparticipation 由 exactpolicy 決定，runtime 存在不授權；StrategyRestoreValid、StrategyTradingReady、DecisionCohortTradingReady、ExecutionReady 分開。

Groupintents 相反時候選基本策略 `REJECT_OPPOSING_GROUP_INTENTS`，返回 conflictcase 與原 intents；owner 可採 versionedserializepolicy（完成一 group exit 並確認 physical/virtualinventory 後再 evaluate 另一 group），但不能 internalmatch/netoff。相同方向可 batch 但每 intent/group 資源與 fillallocation 在 send 前 fixed；總 quantity/資源與 bundle 映射不可改 acceptedoldfills。

Riskguard 層：instrumenttradeability/capability、marketfreshness/completeness、account/recoverycurrentness、capital/cash/margin/reservation、position/concentration/leverage、liquidity/spread/slippage、daily-loss/drawdown、Greeks/DV01/currency/credit/rateexposures、settlementobligations、session/orderlimits、human/environmentadmission。Policythresholds 是 deploymentexplicitinputs，無金額/比率來源不替 Owner 發明 riskappetite。

ETF leverage 以 risk exposures policy 估算，不同 underlyings 不能固定相抵；bondcredit/rate/couponliquidity、optionsnonlinear stress/margin、FX 兩 currency、fundgating/settlementcash 皆 explicit。Portfoliohedge 報表可 netrisk，仍保 gross/asset-specific/instrumentexposure；報表 netting 不改 executioninventory。

## State／Events／APIs／Dependencies

RiskDecision DRAFT→EVALUATED→APPROVED/REJECTED/UNKNOWN→CONSUMED/EXPIRED/INVALIDATED；APPROVED 只對 exactcut/intents 有效。KillSwitch ENABLED→HALTING→HALTED→RECOVERY_HOLD，解除必 freshgate；onlyentryblock/controlledcancel/reduce 的 effectspolicy 區分，不能 kill 即自動 marketliquidate。

MA04/05 策略/研究 proposal→G；MA06capital、MA03data、MA09capability→cut；Gapproved→H。API `/api/v2/risk-previews`（研究／preview 無 execauthority）、`GET /risk-decisions/{id}`、`POST /risk-controls`（Human 角色、explicitallowedactions、operationreceipt）；UIrisk 顯示 cut/reasons/stale/missing，approval 不能 checkbox 繞 gate。Events RiskDecisionRecorded、RiskInputInvalidated、KillSwitchTransitioned。

## Error／Retry／Recovery／Security／Compatibility

Changedcash/policy/order/dependency afterapproval→STALE_CUT，deny submit/re-evaluate；sameevent/revisionreturnexistingreceipt，differentpayloadconflict。RecoveryHold cannot autoresume fromrestored APPROVEDriskreceipt；newepoch/currentauthoritiesrequired。Scopedaccount/environmentroles、Humanriskappetite/uploadsourceallowlist；LocalLM 無 riskapproval권限。Legacydecisionlayercompatiblefuturessubsetadapter，groupconflictchecks 與 newriskcut 在 companion，v1symbol 不足就拒絕 newasset。

## Examples／Acceptance／Tests／Handoff

正：riskpreview 足資金但 send 前另一 reservation 成功，freshcheckreject；exitfilled/FLATproof 後新 decision 可 enter。反：僅 reconciliationMATCH 就 strategyready、timestamp 最新就 cutcomplete、netgroupA 買與 B 賣而各造 Fill、riskunknown 當 approve、重啟保留前 epochapproval。

Acceptance：singledecisionowner、完整 cut/finalwitness、riskreason 可重演、independentcapitalresourcechecks、nointernalmatching、unqualifiedproduct/environmentsfailclosed。Tests：sourcecutdependencymutation、allriskguardmissing/thresholdbounds、opposinggroups/partiallegs、concurrentreservations/riskrev、exitflatenter、stalerisk/epoch/replay、kill/cancelunknownrace。Actualbroker/SQLruntimequal 不能以 purefixtures 替代。

WORK：cutassembler/reuseacceptedR01、groupconflictpolicy、asset-riskstrategies、admission/finalwitness、riskUI/API、negativeinvariants。任何 riskappetite/semantics 來源衝突先 Human/Architect，不讓 executor 選閾值。Knownlimits：部署數值 riskpolicy 需 exactOwnerselection，逐 assetmodelqualification 待 runtime；不阻塞其他研究/UI 規格。

## 本次有界補充契約

[ECONOMIC_RESOURCE_CONTRACTS.md](ECONOMIC_RESOURCE_CONTRACTS.md)、[MONEY_SUBMISSION_CUT_PROTOCOL.md](MONEY_SUBMISSION_CUT_PROTOCOL.md) 為本章不可省略的候選 companion；typed resource/obligation、T12 witness、export adapter 與 exact dependency/source bindings 必隨章節 subject 一起編譯及審核。原 accepted predecessor 不變。


## Cycle 02 有界後繼契約（設計候選；沒有採納或施工授權）

本章的受影響消費者使用 `MA-ARCH-REVIEW-v6-CYCLE02` 的 MODEL／TYPE／API 精確版本。來源與 plan revision 是 `candidate.6`；傳輸協定是獨立的 `MA-DTO-v6`。不得將 `candidate.4/5/6` 當 wire alias。原接受 P00 設計、永久身份、舊 Wave／Feature 語義及 v5 完整前驅 bytes 保留。

Registry：`CC02_AUTHOR_ADDENDUM.candidate.v6.md`、有限內部 producer allowlist、source-file resolver 及封閉來源正文型別。PAPER／compiler／wire／單元：`ENGINEERING_ADDENDUM.candidate.v6.md`。resolver 依原來源 owner、權限、immutable source bytes 與 schema 驗證；capture、索引與 A/B protection 不能互推。compiler 的 HOLD 和 READY 都固定完整輸入；source-compatible 設計檢查與 qualified producer result 分開。

本輪具體測試世界是合成設計預期值，`EXPECTED_NOT_EXECUTED`，不代表任何實際 DB、Broker、PAPER、Controller、還原或執行。`95_OPERATION_VALUE_COVERAGE.candidate.v6.json` 明列尚未補足的正例；negative wire case 不替代 positive domain oracle。舊 v5 fixture 原文保留，但只能作前驅/版本相容或回歸輸入，不能被推導為本輪當前 wire 實作證據。
