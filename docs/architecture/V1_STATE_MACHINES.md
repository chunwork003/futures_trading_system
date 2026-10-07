# State Machines — P00 Candidate

Status: `FROZEN_CANDIDATE / NOT_ACCEPTED`。State、command、observation與permission是不同軸，不能合成一個READY。
所有mutable head：expected_revision CAS、transition receipt、actor/correlation/reason。Unknown transition拒絕，不預設成功。

## Research / workers

| Machine | States / legal transitions | Authority / effects | Retry / crash / unknown / audit |
|---|---|---|---|
| ResearchRun | intent CREATED；execution/result state從Operation投影，不有第二份mutable lifecycle | research service creates immutable intent + operation in one transaction | retry不改input；missingoperation=integrity error；creation/result refs audit |
| Operation | QUEUED→RUNNING/CANCELLED；RUNNING→SUCCEEDED/FAILED/CANCEL_REQUESTED/RETRY_WAIT；CANCEL_REQUESTED→CANCELLED/FAILED；RETRY_WAIT→QUEUED/CANCELLED；terminal無outgoing | service creates/cancels；fenced worker completes；scheduler requeues bounded retriableattempt | crash=lease失效後新attempt；publish與cancel共用同一operation revision CAS；publish先提交則cancel回傳already-terminal；cancel先提交則禁止publish成功，安全停止後CANCELLED；未知outcome先查receipt |
| OperationAttempt | CLAIMED→RUNNING/FAILED/ABANDONED；RUNNING→SUCCEEDED/FAILED/CANCELLED/ABANDONED；terminal無outgoing | claim transaction分配attempt/lease；current fenced holder写terminal | expired attempt標ABANDONED需CAS；不得從ABANDONED publish；每次attempt保留failure/checkpoint |
| WorkerLease | UNCLAIMED→HELD；HELD→HELD(renew)/RELEASED/EXPIRED；EXPIRED/RELEASED→HELD(new generation) | PG transaction/DB clock；generation嚴格增加 | holder+generation+unexpired共同驗證；lock-free timestamp check不足；unknownDB禁止commit |

Job retry預設最多2個額外attempt，僅transient infrastructure failure；invalidinput/deterministicengine error不自動retry。此預算不同於development correction budget。
RUNNING lost lease不能標成功或繼續發sideeffect；計算可終止，orphanartifact可留待GC。每個attempt得出同semanticoutput時artifact可去重，但不得隱藏不同output nondeterminism。

## Trading / simulation

| Machine | States / transitions | Authority / side effects | Recovery / unknown / terminal |
|---|---|---|---|
| Strategy runtime | STOPPED→WARMING→READY→RUNNING；RUNNING→PAUSED/STOPPING/HALTED；PAUSED→WARMING；STOPPING→STOPPED；HALTED→WARMING only explicit recovery | E orchestrator consumes canonical observation/config；READY僅strategy local readiness，還須cohort/account/tradegate | warmup不足不emitintent；unknownstate=HALTED；checkpoint後resume，不能重emit已durable signal |
| SimulationSession | CREATED→STARTING/STOPPING；STARTING→RUNNING/STOPPING/HALTED；RUNNING→PAUSING/STOPPING/RECOVERING/HALTED；PAUSING→PAUSED/STOPPING；PAUSED→STARTING/STOPPING；RECOVERING→PAUSED/HALTED/STOPPING；HALTED→RECOVERING/STOPPING；STOPPING→STOPPED/HALTED | Python sessionowner、single syntheticaccount fence；start經fullreadiness；stop不隱含forceflat | restart先RECOVERING，不autoRUNNING；STOPPED retainsread-onlyevidence，new session用newidentity |
| Order | exact existing PENDING/SUBMITTED/PARTIALLY_FILLED/FILLED/CANCELLED/REJECTED transition validator | canonical OrderEvent/Fill authority；禁止新增UNKNOWN/PENDING_CANCEL到既有enum作快捷方式 | eventsequence/provenance幫助resolve，broker未知由BrokerAction狀態表達；terminal corrections只依acceptedcontract |
| Cancel command | REQUESTED→ACKNOWLEDGED/REJECTED/OUTCOME_UNKNOWN；OUTCOME_UNKNOWN→ACKNOWLEDGED/REJECTED after authoritative resolution | command/BrokerAction owner，cancelrequest不等於Order CANCELLED | samecommandretry先查status；不得retry成第二個newaction；fill/cancel競態依canonicalevents |
| Reconciliation | existing HALT/REVIEW_REQUIRED/RESOLVED and accepted transitions | C13 caseversion+policy；appendreceipt，不overwritestate/economicposition | NULLscope failclosed；resolvedcase不提供全部READY；audit保留underlying evidence |
| Account readiness | HALT/REVIEW/READY 是對一個RecoveryCut的evaluation，不是隨意mutableflag | accepted trustedresolver/finalfence；READY不等於LIVEauthorization | cut失效重算；unknownprovenance拒絕；歷史READY不得currentreuse |
| Recovery | captured localVALID/RESTORE_FAILURE -> trusted evidence -> reconciliation/strategy/cohort evaluation -> final fenced handoff | accepted recover_runtime/PGgate及ADR-002；保留既有status，不再建競爭enum | crash後freshcut；VALID!=broker-current；任何missingdependency不升級READY |

Simulation pause：停止new risk-increasing decisions；pendingevents仍須drain/record。STOPPED要求沒有in-flightmutator並已checkpoint；可保留非零position供inspection，不能因STOPPED宣稱FLAT。force-flat需要explicitcommand、currentposition/capability/risk-reductionauthorization。
risk_increase_blocked 是 durable orthogonal latch，不是 session lifecycle enum；KILL 與 START-clear 的 command semantics 見 V1_API_ARCHITECTURE.md。
Kill switch可block OPEN/ADD，cancelexistingorders只依explicitpolicy；並不默默平倉。V1 defaults cancel pending risk-increasingorders，已接受fill仍入ledger。減倉command不因kill被認作開新風險，但仍經identity/readiness驗證。

## Development lifecycle（既有accepted語意保留）

| Machine | Owner / transitions | Side effects / crash / unknown |
|---|---|---|
| Work Order authorization | existing NOT_AUTHORIZED→AUTHORIZED→RESERVED→CONSUMED，及SUPERSEDED/REVOKED allowedpolicy | exactparentgrant與currentbinding；consumed不可redispatch，無syntheticgrant |
| Execution | IDLE/QUEUED/PRE_DISPATCH/RUNNING/PAUSED_PROVIDER_LIMIT/RESUME_PENDING_REVALIDATION/RESULT_READY/STOPPED | sameinvokedidentityresume，無invocationevidence不得backfill；wake無authority |
| Review | NOT_REQUESTED→PENDING→PASS/REVIEW_FIX_REQUIRED/BLOCKED | independentreviewer綁candidate/scope；fix生成新reviewbinding，舊PASS不適用新candidate |
| Integration | NOT_PREPARED→PREFLIGHT→INTEGRATED/CONFLICT/BLOCKED | integratorchecks reviewedblobs/protectedfiles/compatiblemaster；不forcepush、不默默semanticconflictresolution |
| Acceptance | NOT_ACCEPTED→ELIGIBLE→ACCEPTED；ACCEPTED→INVALIDATED only explicitaffectedrequirementevidence | WORK underdelegatedgrant核對review+integration+tests；author不可自accept；invalidate保留history不刪evidence |

後三者是P00 operational model候選，adapter必須映射既有review/integration/evidence格式；不能在activecontroller未review時啟用。
Controller ranking只在安全優先序之後及packageboundary發生。Blocked externalpackage若仍有未釋放writer或activeexecution，不能被新工作繞過。

## Required model-based counterexamples

1. lease過期後舊worker提交結果：拒絕，newattempt不被覆蓋。
2. success與cancel同時：唯一CASwinner，terminal不回退。
3. duplicate command相同key不同payload：409，無新增operation。
4. simulationrestart觀測不足：REVIEW/HALT，不autoRUNNING。
5. partialclose遇reverse：未FLAT前無反向ENTER。
6. reviewerPASS但mastersemanticdrift：integrationBLOCKED，不accept。
7. consumed但未invoked：只能exactfirstinvocationroute，不稱resume。
8. brokeractual缺失：UNKNOWN，不以emptypositions建立FLAT。
