# MA04 — Research & Strategy Lab、Builder 與不可變研究版本

Revision `candidate.4`；Owner E Feature Strategy／F Backtest Research；CORRECTED_CANDIDATE／AUTHOR_VALIDATION_PENDING／INDEPENDENT_RE_REVIEW_PENDING。

## Purpose／Source／Reuse／Dependencies

來源 LAB Rev2 trade-attribution decisions、Rev3 SQL/import/localLM addendum、最新 Human 完整 LAB／第一可用產品要求；沿用 `E_FEATURE_STRATEGY.md`、`F_BACKTEST_RESEARCH.md`、features/registry.py、strategy/registry.py、backtest/engine.py。新 Builder 是研究作者工具，不能取代 accepted G decision layer。核心不依賴 UI/ORM/broker；existing backtest 演算法重用需 compatible adapter＋新的多資產 fixtures，不以存在檔案宣稱新能力完成。

## Data Model／身份／版本

| Model | 欄位與責任 |
|---|---|
| SourceInboxItem | id、original_name、capture hash/ref、origin/author/licence、AST report ref、status、人工 disposition；未信任 code 永不 import |
| FeatureDefinitionRevision | id/rev、typed inputs/outputs、lookback/units、parameter schema、implementation ref/hash、determinism/source policy |
| StrategyDefinitionRevision | strategy_id/rev、graph_ref、parameters、asset/universe、signal semantics、feature versions；不包含 broker credentials |
| StrategyGraphRevision | nodes stable IDs、ports typed、edges、outputs、schema revision、source hash；pure DAG；iterations 必須 explicit supported operator，不讓 cycle 混入 |
| GeneratedCodeRevision | graph/ref＋generator/compiler ref、code bytes/hash、dependency lock、checks；code 不是 graph 的可逆替代品 |
| ResearchBranch | 永久 branch/root IDs、CodeAssignment、0-parent root／1-primary-parent clone、generation/state/headrefs；S001-01 scoped alias不重用；不是正式 StrategyInstance |
| ResearchSnapshot | graph/code/features/config/dataset/profiles/env/seed/package-lock exact refs＋manifest；sealed 後不可改 |
| ResearchRun | id、snapshot_ref、method_ref、runconfig、engine ref、seed、attempt、status、result artifacts、metrics definitions、failures |
| ResearchComparison | immutable run refs、alignment window/currency/metric policy、display slots≤6；historical saved experiments 不受6 限制 |
| LibraryRelease | exact strategy/snapshot、approval kind、qualification／例外 receipt、永久 warning、release hash；library approval 不等於 runtime admission |
| Deployment | release_ref、environment/account/group、config/policy refs、admission receipt、epoch；Runtime StrategyInstance 與 release 分開 |

每物件 `ContractRef`；branch move/name 不改 root 身份；snapshot 捕捉 exact graph+generatedcode，後續 Builderedit 不污染已發佈策略。Artifact publication（bytes/schema 安全驗證）、Library approval（研究採納）、Runtime admission（環境／risk 準入）三 gates 獨立。S001 name/code 不是履歷或執行授權。

## Functions／Inputs／Outputs／Business Rules

`analyze_source(item)` 只 AST parser，在資源限制環境檢查 imports/calls/dynamicexec/network/fs/sideeffects/complexity，輸出 findingranges；**AST-only 不能證明惡意 Python 安全**。`archive_source(plan,decision)` 要 typed ArchivePlan＋Human exact bytes approval＋immutable capture、CreateNew/verify/recovery receipt；`build_graph(draft,expectedgen)` typedports/no cycles/parameter bounds；`generate(graph,generator)` deterministic code＋checks；`seal_snapshot(refs)` full closure；`run(snapshot,method)` isolated no LIVE credentials/broker；`compare(runrefs,policy)` alignment report；`publish_library(candidate,approval)` immutable release；`request_admission`交 MA07/08，研究 service 不能自己 admit。

Builder node variants：Feature（純運算）、Rule（ENTRY／EXIT／STRATEGY_RISK）、Substrategy（完整子圖）、Safety（不可停用）；data/comparison/allocation/output按各 definition port。最後一個有效 ENTRY／EXIT／STRATEGY_RISK 不可OFF；Safety永不可OFF。所有可連接 port 有 type/shape/unit/time alignment/nullable；缺 lookback 禁止 lookahead；boolean 與 targetweight/qty 不可直接串。GUI 保存 graph revision、code 生成可下載受控 artifact；手改 code 另 researchrevision，須明示不可 reverse 同期 graph。

Externalcode 安全分析後仍需人工歸檔與新規格映射；執行必隔離 sandbox、禁 network/secrets/hostmount、limitedCPU/RAM/time/process。安全 AST 拒絕 importlib/eval/exec/unboundedfs subprocess 等候選不執行；manualapproval 不解除 runtime 沙箱。

## 研究方法契約

| Method | 固定輸入／避免偏誤／輸出 |
|---|---|
| Single/Multi Backtest | dataset snapshot、execution/cost/portfolio policies、strategy refs、capital、seed；逐策略 intent 與 account aggregation 分開 |
| OOS | chronological train/validation/test windows、purge/embargo policy、fit cutoff；finaltest 不得調參後重稱 untouched |
| WFO | window/step/optimizer/searchspace/budget/selection policy；每 foldfit 僅 training，拼接 OOS 結果保 fold 來源 |
| Monte Carlo | resampling method/blocklength、runs、seed、correlation preservation、confidence definition；不能把 simulated 收益當歷史 |
| Benchmark | exact benchmark/totalreturn/currency/cost/calendar/period；ETF NAV 與交易價不同 |
| Ablation | base snapshot、singlechangedfeature/param、controlled inputs、reruns；多變項明列，非單因素 claim |
| Replay/STANDARD | deterministic eventorder、fill/slippage/commission/risk/latency model、seed；無真 broker；不能當 livequalification |

Metrics 保 definition version：PnL/equity/cashflow/timeweighted/moneyweighted return、drawdown、volatility/riskfree/calendarannualization、fees/tax/slippage、turnover、exposure、tradecount；零交易、缺資料、undefinedratio 顯示 NA＋reason，不填0。Comparison 異 window/currency/model 需明顯 incomparable flag、拒絕無說明排名。最多6 是同步畫面 slot，儲存 Runs 不限。

## Lifecycle／Events／API／UI

SourceInbox facade RECEIVED→ANALYZED→HUMAN_CONFIRMED→ARCHIVED／REJECTED，actual source analysis／archive效果／cleanup狀態及qualification依 `LAB_LIFECYCLE_CONTRACTS.md` 分開；Draft graph EDITING→VALIDATED→SEALED；Run QUEUED→RUNNING→COMPLETED／FAILED／CANCELLED，partialresults 不 qualified。Library CANDIDATE→REVIEWED→APPROVED→RETIRED（old deployments 仍 exact 版本，撤銷需新 riskcommand）；Deployment DRAFT→ADMISSION_PENDING→ADMITTED→RUNNING→PAUSED→RETIRED，restored 回 RECOVERY_HOLD。

Events SourceCaptured、GraphSealed、ResearchRunCompleted、ArtifactCaptured、LibraryReleaseApproved、DeploymentAdmissionRequested；approval 事件只含 receiptref，consumer 驗 exactscope。API `/api/v2/source-inbox`、`/features`、`/strategy-drafts`、`/research-snapshots`、`/research-runs`、`/comparisons`、`/library-releases`、`/deployments`；MA10 完成 wire spec。UI Builder 三欄 library/canvas/inspector，六 Comparisoncards＋sharedmetrics，History 按 branch/run/snapshot；可看 missingartifact 但不可宣稱可重現。

## Local LM／Security／Version Compatibility

Local LM 為受限 AI Analyst：只讀 allowlisted 研究資料／snapshots、提供假說/feature/parameter 建議＋source citations；不持有 SQL/Git write、broker、交易／libraryapproval 權限。LMmodel/tokenizer/prompt/tools/config/inputhash/version 保存於 Suggestion；測試前不宣稱建議可靠。建議進 Draft 待 Human／research gate。LMprovider 可關閉不意味 AI Analyst capability 從產品刪除。EngineeringLM Coding 資格另 MA14，不能繞過研究助理權限。

Replay same seed 不保證跨硬體/engine 版本 bitexact，manifest 標 deterministic level BITWISE／TOLERANCE／STOCHASTIC 及容差。Dependencypackage drift、datasetmissing、graph/codehash 不符拒絕 run；retry 新 attempt 同 runimmutableconfig，不覆寫已完成 artifact。CAS draftwriters409；run duplicate command samehashno-op，diffhashconflict；cancel 與 complete race 由 engine eventsequence 裁決，不銷毀 partialaudit。

## 正反例／Acceptance／Test Strategy／Handoff

正：移動 LABfeature 到 sharedlibrary 後同 id；S001 新 branch 不改已 deployrelease；多策略輸出由 decision/risk 接收。反：ASTpass 立即 exec、LM 直接 SQLcreate/approve、用最後新版 dataset 替原 Snapshot、比較不同年期回報同排行榜、run 成功自動 LIVE、negativeSignal 直接 reverse physicalposition。

驗收：完整 immutable closure、manualapproval、no-IOsandbox、6display 不限 history、正確 methods/leakage tests、account/groupresulttrace、samepublishedrelease 不受 Draft 改動；原 LABwave/productaliases 隔離。Tests：typedgraph/cycles/lookback、generatorgolden/codevariance、OOS/WFOfoldleak、MCseeds/correlation、ablationcontrols、cancelrace、capturefailure/restoremissing、malicioussources、LMpermissionnegativecases。

WORK units 包含 inbox/capture、feature/graph/builder、snapshot/generator、researchmethods、comparison/results、publication/deploymentadapter、AIanalyst；以 objectivefixtures 證明能力，不新增完整 parallelbacktest 引擎。Knownlimits：actualsandbox/datasets/performance/restore/brokerintegration 待 Qualification；S14/S15 只在 MA05 Future 研究 lineage，不改本章 acceptedruntime。

## RCG03 candidate.4 — Required lifecycle closure

`LAB_LIFECYCLE_CONTRACTS.md` C1–C6 與 `RCG03_LAB_FIXTURE_ORACLES.json` 是本章必要 detailed companion，具名補足 PRODUCT-S4-01～06。Archive、Builder、Analyst、LibraryException、LAB research simulation、S001 branch/history 均有 typed request/result、named operation、receipt、CAS、event、consumer、retry/recovery與合成反例。舊 candidate.3 顯示狀態僅兼容 facade，不可取代新效果 state machine。

MA04-U01 主SourceAnalysisRequest→SourceAnalysisReport，archive是Human-gated副契約；U02 BuilderEditCommand→StrategyGraphRevision；U03 BranchCreateRequest→ResearchBranch及generation/seal副契約；U05 manualLibrary／permanentwarning；U06 AnalystRequest→AnalystRun／Human另branch。LAB研究模擬帳戶不是MA08 PAPER SimulationSession，沒有broker／正式capital寫權。舊 LAB-01～08 Wave與新product identity分開；S14/S15仍MA05 Future研究，不變productionstrategy。

完整B3 V1包含這些功能，不以PoC／未qual為由刪除範圍。候選契約充分性、實作、author tests、Independent Review、Human exactadoption、runtime/release qualifications 分軸；本輪不取得其餘gate。
