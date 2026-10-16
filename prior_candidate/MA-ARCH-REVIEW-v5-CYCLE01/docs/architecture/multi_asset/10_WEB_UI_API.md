# MA10 — Web UI、ASP.NET BFF、Python API 與可施工畫面契約

Revision `candidate.4`；Owner O React／N ASP.NET Application／M Python Service；AUTHOR_CHECKED／FORMAL_REVIEW_PENDING。

## Purpose／Source／Reuse／Architecture

保留既有 O_REACT_WORKSPACE、N_ASPNET_APPLICATION、M_PYTHON_SERVICE 與 CONNECTION_MATRIX：React→ASP.NET application/BFF→Python typed usecases→domainports；React 不直連 DB/broker，ASP.NET 不 importPythonclasses/SDK。新多資產/URMS 頁面為 companion routes，不把偏好 FastAPI/React 解讀成可刪 ASP.NET。實際 runtime 版本 pin／身份機制依既有 Human gate，不偷偷換 framework。

## 共用 Layout／Permission／狀態

Desktop12column：左 navigation、上方環境/account/contextbar、中間 main、右 detaildrawer；小螢幕 drawer/stack，不縮表到無法看。LAB/PAPER/LIVE 醒目環境文字，不只顏色；不同環境切換重新取得 resourcepermissions、禁止保留上環境送單 draft。金融值顯示 currency/unit/asof/cut/quality；NA/UNKNOWN/stale/empty 完整區分。

Every page：initial-loading、verified-empty、partial、stale、permission-denied、offline、validation-error、operation-pending/unknown、success、conflict409。Skeleton 不顯示假0；empty 需 successfulcoverage。表格 key stableID，filter/sort/page 基於 snapshotcursor，refresh 不可重排影響正在 approval 的 subject。非同步 job 保存 operationID，可離頁回 History。Highriskcommands 顯示 exactsubject/environment/account/action/authority，Human confirm 後 server 仍重新 gate。

Roles VIEWER、RESEARCH_AUTHOR、LIBRARY_APPROVER、TRADING_OPERATOR、RISK_APPROVER、ENGINEERING_EDITOR、REVIEWER、PUBLISHER、RESTORE_OPERATOR 經 existingAuthN/AuthZ policy 映射，不另建 AcceptanceOwner。role 不是單一 boolean admin；account/env/operation scope compulsory。CSRF/session/token、XSS/CSP、uploadlimits/content-disposition、privateartifactdownloads 短期 resourceboundpermission；noBrokersecretclientstate。

## 全頁面契約

| Page／Layout | Interactions／Data owner／API | Empty/error／權限／客觀測試 |
|---|---|---|
| Dashboard：healthstrip＋equity/exposure/timecards＋activity | account/envselector、snapshotrefresh；MA06/07/08；GET dashboard/accountcapital/risk/recovery | partialcut 分 widget 標 missing，不匯總未知值；VIEWER；stale/FX 缺/permissiontest |
| Chart：instrumentsearch＋candles＋volume/indicator＋sourcefooter | fixedsnapshot/serieskind/timewindow、compare/annotations；MA03 GET market-bars/queryMarketBars（pricing observations另用） | no data≠0price；raw/adjustedbanner；VIEWER；DST/gap/latecorrectfixture |
| Market：asset/venuefilter＋listingtable＋detail | profile/rules/source/quality；MA02 GET instruments/market-rules | symbolambiguousdialog、unsupportedtradeflag；VIEWER；samecodeacrossvenues |
| Strategy Builder：library/canvas/inspector＋validationdrawer | typeddrag/connect/configsaveCAS/generate/sealsnapshot；listResearchBranches/listGraphDrafts/getGraphDraft、MA04 strategy-drafts/features | port/type/cycle/sourceerrors、409reloadmergeproposal；AUTHOR；lookahead/retiredfeaturetests |
| Research：method/window/configform＋jobqueue＋runresult | backtest/OOS/WFO/MC/benchmark/ablation/rerun/cancel；research-runs/listResearchRuns | missingdataset/readinessdisable、partial/cancel/warning；AUTHOR；foldleak/unknownjoboutcome |
| Comparison：sixslots＋alignedcurves＋metricstable | selectsavedruns/window/currency/metricpolicy/savecomparison；comparisons | >6slotsreject、unlimitedhistorypager、incomparablealert；VIEWER/AUTHOR；differentperiod/model |
| Simulation：release/group/capitalconfig＋STANDARDtimeline | requestadmission/startpause/replay/status；simulation-sessions/deployments | LABdraft 不能 PAPER、noLIVEtoggle；OPERATOR(PAPER)；env/cut/seedtests |
| Portfolio：assets/groups＋holdings＋allocation/exposure | cutfilter/groupdrilldown/researchrebalanceproposal；portfolios/positions/attribution | partialvaluationsflag、proposalnotorder；VIEWER；FX/qty/conservation |
| Orders：lifecyclegrid＋event/detail＋controlpanel | approvedintent/detail/cancelqualified/amendrequest；order-intents/orders/listOrders | UNKNOWNpending 不可顯示 notplaced、receiptquery；OPERATOR；duplicateclick/cancelrace |
| Positions：physical/virtualseparateviews＋lots | group/contract/cutfilter、expectedvsactual；positions/reconciliation | noFLATwithoutproof、不允 group 轉賣；VIEWER/OPERATOR；unassigned/externalfill |
| Risk：guardstrip＋decisionreasons＋limits/exposure＋killswitch | preview、新 policy 候選、explicitcontrol；risk-previews/risk-controls | unknownfailclosed、高風險 Humanapproval；RISKROLE；stalesubmit/reentry |
| Cash Flow：currency/value-datecashschedule＋ledger | settled/pending/projectedfilter、cashflows/accountcapital | 不把預估 coupon 當現 cash；VIEWER；doublecount/settlementholiday |
| Bond/Rate Lab：sourcevintage＋curve/scenarios/stages＋cashflowresults | portfolio-research/scenario-runs/macro-snapshots；MA05 | sourcecells/modelassumptionbanner、S14/15Future 研究；AUTHOR；original/candidatepreservation |
| Artifact/History：tree/run/revisionbrowser＋content/manifest | immutableview/download/hash/availability、controlledcapture；artifacts | missingcontent 只顯 reference、corrupt 禁止 restoredclaim；scopedVIEWER；path/privacy/hash |
| URMS：producttree/worktree＋crosswalk/relations＋drafteditor | registry/registry-candidates、scopefilter/history/validation；MA11/12 | ambiguouscode、不 countedges、acceptedreadonly；EDITOR/REVIEWER；cycles/identity |
| Automation/Progress：existingprogramlane＋DAG＋cost/context/evidence | existing WORK projections／engineering-status；dryplanningproposal | NOTAUTHORIZED 不是 READY、actualunknown、no dispatchsideeffect；engineeringroles；capacity/gatedependency |
| Settings：profile/config/providers/capabilities＋versiondiff | config-candidates、secret-handle-status(readonlyavailability)；MA16 | 不展示 secret 值、credentialconfigure 走單獨 authorizedworkflow；ADMINRESOURCE；secretexposure/CAS |
| Audit：actor/subject/correlationtimeline＋receiptverification | audit-events/operation-receipts；read-onlyfilters/exportredacted | absence≠noevent、exactfrontier/coverage；AUDITOR；tamper/replay/privacy |
| Library/Deployment：releasecatalog＋approvalsubject＋envstatus | library-releases/deployments/manualreview/admission；MA04/08 | libraryapproval≠runtimeadmission、Draft 不能 release；APPROVER/OPERATOR；exacthashchange |

## Wire／API／事件契約

API catalog 是同候選的 machine companion。共用 command envelope `{command_id, payload_hash_domain, payload_hash, resource_scope, expected_generation, subject_refs, payload}`；payload_hash 由 server canonicalizer 重算，clienthash 不是 authority。authenticatedactor 由 servercontext 取得不可 payload 冒名。Read response `{schema_version, resource_scope, data, snapshot_ref, as_of, coverage, missing, next_cursor}`。Command result `{operation_id, state, receipt_ref, result_ref?, reasons}`；UNKNOWN 不等 FAILED_NO_EFFECT。

所有 decimal 用 string，quantities 附 unit，timeISO8601UTC/tradingdate 另欄；ref 包含 id/rev/owner/hashdomain。Cursor 綁 query/snapshot/scope、maxpagelimit 候選200；array 過大用 job/contentref。Error `{code, message_zh_tw, correlation_id, fields?, retry_disposition, operation_ref?}`：401/403auth、404resource、409CAS/hashconflict、422semantic、429rate、503dependency；非 economicqueries 可有限 retry，commands 查 receipt 優先。

BFF DTO 和 Python DTO 是 versionedserializationcontracts，domainobject 不直接 JSONserialize。OpenAPI 版本/contractbundlehash 與 clientgeneration 固定；breakingadditionclosedenum 需 v2successor，unknownenum 畫面安全呈現不默認既有值。SignalR 只推 readmodel 事件 envelope{event_id,type,schema,scope,sequence,projection_generation,subject_ref,redacted_payload}；失 gap 先 resnapshot 再 cursorresume，connection 不能當 authority。

## Application Functions／DB／Security／Recovery

`AuthorizeResource`先 tenant/account/environment/action；`HandleCommand`持 commandreceipt 冪等；`CallPythonUseCase`傳 exactsubject/currentauthref 但 Python 再次 gate；`MapProjectionDto`附 cut/coverage；`ResumeSubscription`snapshot 一致。UI 只暫存 displaydraft，正式 draft 由 SQLrevisionhead 管理；privateartifacts 在 ArtifactStore 並 hashindex，下載權限即時驗證。

Optimistic UI 僅 reversibledraft，如 graph nodeposition；交易/publish/approve/budgetchanges 不先 fake 成功。Approvalpanelreview frozen hash 後 refresh 若 subject 變動就阻止；browserback/postduplicate 返回 sameoperation。Request cancellation 不代表取消 brokerorder；DB 或 brokerunavailable 狀態要 serveroperationreceipt。

## Examples／Acceptance／Test Strategy／Handoff

正：networktimeout UI 保 orderUNKNOWN 並查 receipt；privateartifactmissing 仍保 entity/tree；comparison6display＋history。反：UIcheckboxaccepted=true、brokersecret 進 localstorage、JS 預估 cash 當 riskpermission、SignalR 最新當 allcutvalid、settings 直接執行 migration、progress 把 mappingcount 當工作量。

驗收：19 頁 route/permission/state/API/dataowner/fixtures 都有 mapping；wiredecimal/ref/cut 一致；BFFdirection/closedschema 保護；accessiblekeyboard/labels/focus、empty/partial/stale 完整。Tests：componentstates/contractgolden、serverauthnegatives、E2E 六 journeys、duplicate/CAS/timeout/streamgap、account/envswitch、XSS/upload/downloadprivacy。實際 authNscheme/.NETpin 若未 Owner 選定，spec 保持 providerinterface 並在 scaffoldGate 集中選，不阻塞 wire/UI 章節。

WORK 單元：designsystem/sharedDTOstate、typedBFFclient/permissions、19 頁 cohesivejourneygroups、SignalRresume、contract/e2efixtures；禁止只生成空 page scaffold 當功能 complete。Knownlimits：現有 UI 完成度與所有 actualendpoints 本次未測；設計 data/APIcatalog 不是已部署 API。

## 精確文件下載及模擬 wire binding

getArtifactContent 返回 ContentDescriptor；getArtifactBytes 是獨立權限再驗證的 VerifiedBinaryStream/BinaryContentMetadata，不返回 ArtifactRevision JSON 代替原始內容。PAPER SimulationSession 與 LAB ResearchRun 的 STANDARD 研究方法分開；startSimulation/session lifecycle 僅 PAPER admission。


## RCG04 candidate.4 mandatory consumer closure

[TRADING_CAPITAL_UI_ADDENDUM.md](TRADING_CAPITAL_UI_ADDENDUM.md)與MODEL/TYPE/API/EVENT同版為本章不可省略契約；external EconomicOrigin、全帳戶budget preview/confirm、PAPER SimulationSession、MarketBar DTO、servercold-reentry/error/cursor/stream及consumer映射隨exactsubject一起審核。原accepted語義不變，Runtime NOT_RUN。


## Candidate.5 有界修正承接

candidate5 uses versioned closed readback companions and exact Body Catalog; receipt/ref alone is insufficient for display or Human preview. Original DTOs/95 operations retained; legacy profile immutable.

唯一詳細契約：`BODY_CAPTURE_READBACK_CONTRACTS.md`。原已接受範圍與尚未完成qualification保留。
