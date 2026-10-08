# V1 Product Architecture — P00 Candidate

Status: `FROZEN_CANDIDATE / NOT_ACCEPTED`。Freeze 是供 review 的穩定候選，不是 implementation／runtime grant。
Baseline 與續作狀態：`../program/current_truth.v1.json`、`../program/p00_status.v1.json`。
Accepted ADR-001／ADR-002 與 GAP-08 source 的 semantics 保留；本文件只定義未交付產品的組合及新契約。衝突要明列 amendment，不以文字覆蓋舊 authority。

## 1. Product / scope

V1 = **Personal Futures Research & Simulation Workstation**：single operator、local machine、browser、reproducible research、BACKTEST／SIMULATED。完全不需要真 broker credentials。
必交付：dataset version、backtest、comparison、parameter study、OOS、WFO、Monte Carlo、incremental strategy、multi-strategy decision、risk/capital、canonical simulation/OMS、expected/actual reconciliation、PG persistence/recovery、Python API、ASP.NET BFF、React、audit、install/diagnostics/backup/restore。
V1.x：更多研究工作流程、報表、策略、資料來源與效能；V2：multi-account／allocation、additional brokers、multi-asset；Future：ML、News、mobile、GIS/property、advanced drawing。未登錄早期對話需求不得聲稱已完整捕捉。
BROKER_PAPER／LIVE_CONFIRM／LIVE_AUTO 是獨立環境及權限 gate；V1 server 必須拒絕，不能只有 UI disabled。券商真連線與實盤不是 V1 offline acceptance dependency。
首批驗收商品 TX／MTX 的明確 listed contracts；既有 TMF identity 保留但不聲稱全商品環境 conformance。Continuous series 只作研究資料，不是可執行合約。

## 2. Cross-layer / ownership

```text
React projection -> ASP.NET authentication/workflow -> Python versioned API
                                                     -> Quant / trading core
                                                     -> Research worker
                                                     -> PostgreSQL repositories
                                                     -> Immutable artifacts
```

| Authoritative responsibility | Owner | Durable direction |
|---|---|---|
| Market observation identity/content/accepted revision | domain/market_observation + acceptance contract | existing trading observation ledger |
| Dataset/version/provenance | ingestion/storage data owner | immutable manifest + Parquet; research metadata |
| Calendar/session/contract identity | trading_calendar + domain/contracts | versioned reference snapshot |
| Strategy definition/instance/config/incremental state | strategy contracts; strategies implementations | existing instance/state repositories |
| Signal/decision/target position | canonical trading decision owner | new append-only decision records |
| Risk/capital permission | canonical trading risk owner | risk/capital version and evidence |
| OrderIntent/OMS/Fill | trading/execution accepted contract | existing execution ledger/UoW |
| Expected position/account | trading/account authority | accepted account head/checkpoint/receipt |
| Actual observation | broker-neutral provider; simulation provider in V1 | accepted observation repository |
| Reconciliation | trading/reconciliation | case/run repositories; not economic repair |
| Persistence transaction | application UoW with repository ports | PostgreSQL adapter; repositories do not commit |
| Recovery/current readiness | accepted recovery resolver + fence | complete RecoveryCut and authoritative evidence |
| Backtest | backtest historical consumer | research artifacts; never live account SOR |
| Simulation | simulation orchestration/adapter | simulation session + canonical operational evidence |
| Research job/artifact | Python research service | research schema + content-addressed files |
| Authentication/permission/browser workflow | ASP.NET application | application schema |
| UI state | React | non-authoritative browser state |
| Audit | producer-owned immutable events, common query envelope | owning schema audit stream; federated query |
| Development execution | accepted automation control plane | existing lifecycle evidence; separate from trading |

Persistence 的物理儲存 ownership 不接管 domain semantics。ASP.NET 不能寫 trading/research operational tables；UI 不保存經濟權威。API 不能直接 serialize private domain object。

## 3. Technology / deployment decisions

選 FastAPI + Uvicorn API、獨立 Python worker；.NET 10 LTS ASP.NET Core host；React 19 + TypeScript + Vite SPA；PostgreSQL 17 為首個驗收 backend。精確 patch/SDK/lock/image digest 必須由 P02/P03 的 dependency lock gate 固定，不能浮動安裝 latest。目前本機工具版本只是 evidence，不是跨機器支援保證。
單機預設 Windows host + supported local container runtime（Linux containers）；ASP.NET serves SPA，只有 BFF 對 browser 公開；API/worker/PG 在 private network。若 host 不具備 container runtime，不能自行改成另一套 deployment target，先記錄環境 blocker；離線核心與 contract work 不受影響。
不導入 Kafka/RabbitMQ/Kubernetes/microservices。使用 PG durable job queue 和一個 research worker 的起始配置；worker 數量可配置，但 lease fencing/claim 必須先測。
.NET 用 logical Api/Application/Infrastructure/Contracts modules；Realtime 先 polling，非獨立 service。不存在合理需求前不新增部署單元。
Operator 透過 ASP.NET Identity password login + secure HttpOnly same-site cookie，mutation 使用 anti-CSRF；bootstrap password 由 operator 本機輸入，不放 demo/repo/log。local TLS／loopback origin 固定；Python internal service credential 以 secret mount 提供，永不走 React。跨服務 actor context 必須綁定經驗證服務身分，不能信任任意 X-Actor header。

## 4. Money / time / identity

- Operational price/money/margin：finite Decimal，拒絕 binary float；JSON fixed-point decimal string，不用 exponent；canonical zero = 0。Research calculation 可 float，但必須標示 approximation，不能回灌 operational truth。
- Exchange timezone Asia/Taipei；持久化 instant UTC；新增 API wire 採 RFC3339 UTC-Z / microsecond subset（既有 accepted source 時間語意不改）；session [open,close)。Trading date 由 versioned calendar 決定，不以 timestamp.date() 猜夜盤。
- timestamp 不取代 sequence/revision；received_at 使用 accepted ADR 的 first durable acceptance，不因 replay 重設。
- Canonical integer instrument/contract identities 重用 domain contract；broker code／dataset alias 不可當 execution identity。
- Corrected data = new accepted revision + new DatasetVersion；舊 run inputs immutable。正在執行的 run pin 舊版本；不 silent switch。
- New object IDs 用 opaque stable string；研究 fingerprint 與 run identity 分離：同 inputs 可有不同 run_id，但相同 input fingerprint／seed 的 deterministic outputs 應等價。
- RNG 使用明確 algorithm/version/seed；parallel subtask seed 由 parent seed + stable trial ID 派生，不能依 worker 排程。

## 5. Research flow / job architecture

DatasetVersion -> ResearchRun -> Operation -> leased OperationAttempt -> worker -> ArtifactManifest -> Result API -> BFF -> React。
ResearchRun pin code SHA、dependency lock、dataset version/hash、calendar/contract versions、strategy/config、decision/risk/cost model、seed、input schema。
Operation 是工作生命週期；ResearchRun 是研究 intent/result identity；一個 run 有一個 operation，多個 immutable attempts。禁止 BFF 建第二套 RUNNING truth。
Claim 使用短 DB transaction、row locking/skip-locked + monotonic lease generation；result publish 必須 CAS live lease/attempt/generation。Lease timeout 不證明舊 worker 已停止，stale worker 的 commit 必須被 fence。
計算不持有 DB transaction。Artifact 先寫 temp、驗證 hash、atomic rename 到 content-addressed path，最後以 transaction publish manifest+terminal operation。未被 DB publish 的 artifact 是 orphan，不是成功結果；GC 必須有 retention grace。
Cancel 接受後標 CANCEL_REQUESTED；未啟動可直接 CANCELLED；running 在安全 checkpoint 停止並由 fence holder 完成。已成功 terminal 不能轉 CANCELLED。Completion 與 cancel 競態由單一 row CAS 排序。
Research retry 可重算，但只有一個 current attempt 的結果可 publish；模擬經濟動作不得沿用 research 任務「整包重做」策略。
Metrics freeze：net return = (ending_equity-starting_equity-net_external_flows)/starting_equity；V1 run 不允許中途 external flow。daily returns 以 calendar trading date 結算；Sharpe 使用 sample std(ddof=1)、明列 periods/year 與 annual risk-free config。樣本不足/zero variance/zero denominator 用 null+reason；profit factor zero loss 時同樣 nullable，禁止 JSON Infinity。所有 assumptions 保存於結果。

## 6. Runtime / strategy / decision / risk

Observation -> incremental feature/state -> StrategyInstances -> Signals -> proposed TargetPosition -> Risk/Capital -> approved TargetPosition -> OrderIntent -> OMS。
Decision 保存 desired／staged proposed target；RiskDecision 以 decision_id 連結 immutable permission，approved target 為其欄位。UI joined projection 不另建競爭 owner。Strategy 不碰 broker/account repositories。
同一 account/contract 的 cohort 必須使用完整 required membership、相同 observation frontier 與 governing versions；缺一項不能以其餘策略 silent 決策。
V1 conflict policy 固定配置版本：同向合併；反向保留既有 PriorityStrategyConflictPolicy：較大 priority 優先；最高 priority 反向平手拒絕，不以 instance ID 猜選；未配置 policy 則 REJECT，而不是隨集合迭代次序。
CapitalSource=MANUAL；run/session genesis 明確資金，cross-strategy borrowing OFF。RiskDecision 保存 proposed/approved quantity、ALLOW/REDUCE/REJECT、每個 constraint/input/version/reason。
Increase exposure 必須有新鮮完整 account/market evidence、margin/capital、max contracts、loss limit。Risk reduction 仍檢查 account/contract/position/currentness，不因稱為 close 就跳過全部 authority。
Reverse 固定 EXIT -> confirmed FLAT -> re-evaluate -> ENTER。Partial close 未 FLAT 不進反向單。
策略 warm-up 未完成不交易；資料 gap 時停止受影響 cohort 的 risk increase。修正版影響已用 feature state 時 pause/rebuild 至 pinned frontier，再重新評估；禁止改写舊 decision。
V1 config 在 session STOPPED/FLAT 且無 pending action 時採新版本；其他 transition 僅依已接受 governing transition contract，不發明 hot-swap。

## 7. Simulation / compatibility

SimulationBroker 與 PaperBroker immediate-fill baseline、Shioaji broker paper 明確分開。
Simulation clock：UTC logical timestamp + monotonic event index；同時間事件按 scenario priority + event ID 排序。Scenario immutable version/hash，包含 latency、partial fills、reject、cancel races、duplicate/out-of-order、disconnect、stale/missing observations、retry/restart。
Fill quantity 不超過 remaining quantity；cancel ack 前的真 fill 必須保留，ack 後 late delivery 依原 event ordering/provenance 處理，不能只按抵達時間丟棄。
Broker actual simulation projection 必須由 simulator execution evidence獨立形成；不能把 expected position 複製成 actual 來製造 MATCH。
Session 使用 synthetic broker-neutral account identity 與固定初始資金；同一 active account 只允許一個 runtime owner。simulation evidence 必須帶 environment scope，不能被 production consumer 當 broker observation。
Legacy backtest/paper models 維持 compatibility adapter；既有成本／next-bar語意保留 golden tests。新 operational writer 只寫 canonical records，不雙寫 legacy Portfolio 作第二套真相。

## 8. Persistence / transaction / retention

Schemas：existing `trading`（Python only）、`research`（Python jobs/results）、`application`（ASP.NET identity/workflow）；audit envelope 共通但 producer tables 在 own schema，避免跨語言 dual writer。
DB roles：migration_admin 僅部署命令；python_runtime 限 trading/research；application_runtime 限 application，無 trading write；backup role least-privilege。不能以 shared postgres superuser 跑全部服務。
重用 accepted UoW/fence semantics；新增 migration forward-only，在 test DB rehearsal 後獨立授權目標 DB。禁止修改 0001–0010 的歷史語意來省 migration。
Cross-service commands 沒 distributed transaction：BFF 記 command request/outcome reference；Python 以 command idempotency key 原子記 accepted command+Operation；response 遺失時 query/retry同 key，不再次產生經濟動作。
Research queue用 READ COMMITTED + row/CAS fencing；canonical recovery 使用已接受的 coherent cut／final fence，不被統一降為 queue isolation。
Retention：published research results、dataset versions、trading/audit evidence預設不自動刪除；temp/orphan 7天 grace、diagnostic logs30天。刪 dataset 若被run引用一律拒絕；user-trigger purge 必須計畫與確認，不是 silent background task。
Backup：manifest列 database backup與referenced artifact hashes；quiesce writers 後建立一致 checkpoint，restore 先驗 hash/references再允許ready。V1 recovery objective：已確認durable command/economic commit不可遺失；restore時間在reference hardware測量，不能先宣稱RTO。

## 9. Operations / six release journeys

Startup：load validated config -> PG compatibility/migration check（不偷偷migration）-> repositories -> worker lease -> read-only API -> explicit simulation start。
Shutdown：停止new claims/commands -> checkpoint/cancel policy -> durable lease/session outcome -> process exit；逾時留下可解析interrupted evidence。
`livez`=process；`readyz`=required service dependencies；account READY/cohortREADY/trading permission須分開顯示。
UI必須显示mode、dataset/config versions、target/expected/actual、stale/reconnecting、operation state、reconciliation reason、audit correlation。Kill switch阻止新risk increase，force-flat是另一个已授权simulation command。
六條journeys及完整preconditions/steps/evidence見 `../program/V1_PROGRAM.md`；只有6/6與independent acceptance才能稱V1 COMPLETE。
Performance驗收採固定hardware/data/scenario manifest；有限候選 targets 與 workload limits 已於 V1_API_ARCHITECTURE.md / contracts/workload_policy.v1.json 定義。P02驗證 targets，不自行補 public semantics；未測之前不得宣稱達標。

## 10. Safety / remaining design gates

P00未 accepted 前不得啟動P01/P02。OpenAPI、contract schemas、state-machine matrix、machine package compiler、independent semantic review是必須完成的gate，不能由此敘述文件代替。
Data timezone/expiry規則需要versioned來源，但research/import/fixtures可以並行，不能讓realbroker驗證阻擋離線V1。
高階owner只處理public semantics/authority重大變更；可推導的local implementation由WORK/CODEX決定。安全gate不等於每天重批同一routine transition。
