# Algorithm / Service Responsibility Contract — candidate.1

本 companion 是 MA02–10 的實作責任與演算法規格；沿用既有 D/E/F/G/H/I/J/K owners、使用 adapters。普通演算法選擇由 Architect 決定；金融數值風險限額／策略交易觸發／商品官方條款是 deployment/profile 輸入，不能由執行端推測。所有 golden fixtures 為 synthetic，不取真實帳戶資料。

## Pure Domain／估值與金流

| Service/function | Input→Output／責任 | 具體規則／失敗 |
|---|---|---|
| InstrumentResolver.resolve | scope/code/as-of→ListingRevision+terms/rules | venue/source qualified、effective interval唯一；AMBIGUOUS/MISSING拒絕；不換 expiry |
| CalendarMapper.resolve_session | official calendar revision/event instant→session/tradingdate | timezone+DST/holiday/night-session、邊界半開區間；unknown provider time不製造UTC值 |
| QuantityPriceValidator.validate | intent+tickband/lotpolicy→normalized economics | exactDecimal、tick band lower inclusive upper exclusive、quantity multiple/min；不默默 round price/qty；需要量化由 explicit proposal 新版本 |
| CashFlowScheduler.schedule | terms/calendar/daycount/fixing→immutable CashFlowLegs | accrual interval與paymentdate分開；business-day convention須policy；missing fixing=PROJECTED/UNKNOWN非settledcash |
| EquityValuator.value | lots×price×FX＋receivables→ValuationResult | splitadjusted研究price不能直接mark原shares；price currency≠report currency需 exact FX |
| FuturesValuator.value | contractqty/multiplier/settlement basis→variation+unsettledPnL | daily settlement後重設basis；settled variation與unsettledmark只計一次；margin列resource非購買成本 |
| BondValuator.value | face/clean/accrued/schedule/curve→dirtyPV+sensitivity | quote percent-par: consideration=face×(clean+accrued)/100；coupon entitlement/excoupon依 terms；price-per-unit另profile；discount sum、clean/dirty標清楚 |
| YieldSolver.solve | dirty target+fixedcashflow/calendar/daycount→yield+diagnostic | bracketed root solver，rate domain/compounding/schedule固定policy；無bracket/multi-root返回 reason，不0；tol/iterations存 algorithmprofile |
| RateRiskCalculator.bump | fixedcurve/cashflows→DV01/duration/convexity | DV01=(PV(y−1bp)−PV(y+1bp))/2，貨幣/1bp並標正負；非parallel key-rate另profile；modifiedduration/convexity需同compounding |
| OptionValuator.value | kind/underlying/strike/expiry/curve/dividend/vol→PV/Greeks | EUROPEAN plain vanilla 可 Black-Scholes-Merton profile；AMERICAN 使用 source-bound lattice；不可把European公式當American；exercise/physicaldeliver另事件；T=0按payoff/officialsettlement，缺vol/curve拒絕qualifiedrisk |
| ETFValuator.value | listedquantity×marketprice及NAV metadata→PV/premium/exposure | marketprice與NAV不同，NAV過期標stale；leveraged/inverse以 daily reset/path scenarios，不固定倍數累積報酬 |
| FundValuator.value | unit/NAV vintage/pending requests→PV/projectedcash | order submission不當Fill；NAV cutoff/gating/fees由terms，unknownsettlement不當availablecash |
| FXValuator.value | base/quote legs/value-date/spot-forwardprofile→PV | quote per base、direct/inverse換算明示；inverse rate reciprocal、bid/ask sides需對換；crossrate sourcecut同時點；missing腿拒絕sum |

RoundingPolicy 必含 precision、mode、currency minor-unit、quantity step、rounding stage。研究 intermediate 可 float64，execution/ledger的Decimal不能直接由binaryfloat轉；從 decimal source string或明示量化receipt。Per-unitprice、money、quantity、notional、yieldrate是不同type；units不得靠欄位名稱猜。DayCount 首版支援 ACT/365F、ACT/360、30/360(指定 variant)、ACT/ACT(指定 variant)；variant未知不近似。固定收益 callable/float/default多情境模型保留完整 scope，選定modelprofile後qualification，不能pretend固定coupon公式覆蓋所有債券。

## Research Pipeline／方法

SourceAnalyzer→HumanArchive→GraphValidator→CodeGenerator→SnapshotSealer→ResearchRunner→ResultCapturer→ComparisonProjector→LibraryApprovalAdapter；各服務 output 綁 exact input closure。Graph topological sort，port type/unit/shape/alignment/nullable/parameterbounds/lookback逐edge檢查；非法cycle/forward reference拒絕。Generatorversion+graph+featurecode+package-lock固定，單純相同graphname不證同code。

Backtest event sequence：已知市場事件→策略pureproposal→原G決策/風險→成本/資金reservation→STANDARD可成交事件→原H/J/Keconomiccommit→metrics。Bar-close signal earliest next admissible event fill；禁止用同bar未來high/low執行已在close才知道的signal。Limit/market/partialfill/slippage/fees/latency優先序寫在 ExecutionModelRevision；排序相同timestamp時依source causal sequence及固定 tie policy，沒有可信sequence不得推live因果。STANDARD僅internalmodel，vendor simulation另profile。

OOS/WFO：train_end≤validation_start≤validation_end≤test_start；purge/embargo依feature lookback/label horizon，需資料範圍證據。Optimizer只看train+指定validation；finaltest被調參使用後重新標USED_NOT_UNTOUCHED。WFO每fold持有自己的fit/result，拼接OOS不得重疊同觀察並重複累加。MC首版blockbootstrap of joint strategy/asset return rows，固定seed/blocklength/runs，不分開抽樣破壞correlation；報distribution/quantile definition，不當observed收益。Ablation同snapshot除明示一項delta，其他多變項另label。六comparison slots只UI限制，runstorage無此上限。

MetricsPolicy：外部入出金與投資收益分離；TWR按externalflow切段 linked returns，MWR=XIRR roots保convergence，drawdown基於同currency/cost-adjusted equity series runningpeak。Sharpe取同period return−riskfree，annualization按profiletradingcalendar/samplefrequency；零variance/缺samples→NA原因。不同window/currency/benchmark/costmodel不能無警示rank。重算永遠newRun/resultrevision，不能取代originalbytes。

## Money／Risk／OMS／Broker Boundary

CapitalReservationService 在 account UoW內原子檢查 actualavailable+active/UNKNOWN reservations及groupbudget；full requiredcash/margin/fees buffer由 policy，不臆測限額。FinalSubmissionFence 讀完整 currentcut、持account executor lease/fence及acceptedintent，禁止其他writer越fence；送單外部無SQL原子性，因此先 durable PREPARED/attempt identity→外部IO→durable outcome；prepared跨crash無可信 no-send proof就UNKNOWN，不自動重送。Human取消/停機先記gate，已在途外部IO可能完成，要收回報、hold並對帳，不能承諾遠端瞬間撤銷。

Group conflict預設整批 REJECT_OPPOSING_GROUP_INTENTS，同向批次先固定 allocation plan。第一版只允許各group獨立 broker childattempt；若native混單/多grouppartialfillallocation未qualified，禁止該batchroute。broker真實Fill具native economicidentity；differentpayload同identity conflict/quarantine；每Fill在原economic UoW記cash/position/fees/origin/outbox。origin未確認→UNASSIGNED suspense；不憑qty/price相似推group。虛擬position是歸屬帳，不允internalmatching或賣其他group庫存。

Cancel可能晚於Fill；UNKNOWN/CancelPending保留reservation到可信terminalproof。Amend首版僅price及 reduce quantity qualifiedsubset；increasequantity需newrisk/reservation、native replace semantics獨立qualified。多legportfolio首版 sequential reviewed plan，任何legfailure→HOLD/explicit residualrisk/approved controlledcompensation，不能auto補另一商品或跨市場原子化假設。

RecoveryCoordinator 只有原 K owner；localRestoreValid、brokerCurrent、strategyReady、cohortReady、executionReady、freshHumanAuthority 分開。重啟新epoch、舊lease/token/approval不可再用；完整requesteduniverse/explicitemptyqueryproof後才可評估FLAT。CapabilityGate逐provider/SDK/account/env/listing/operation/qualifier，登入成功不授所有operation；Shioaji通用gateway不支援商品返UNSUPPORTED，標準紙上研究不受此scope刪除。

## BFF／API／UI 連動與客觀測試

每 API operation 都有explicit request fields、named output、ONE/PAGED_MANY/BINARY_REFERENCE cardinality、scope+roles+errors。Command接收回OperationReceipt，businessresult via exactresultref/operation查詢；202 UNKNOWN不是已成功。Query cursor綁snapshot/query/scope，paged array及itemmodel明示；不把single model猜成list。ViewProjector只讀原OwnerCut，positionsphysical與virtual別tag，dashboardwidget逐cutavailability，不創造economictruth。

Syntheticgoldens：bond face100 clean98 accrued1→dirty99；兩筆reservation60/60 available100 oneaccepted；samefill兩次僅一次economicmutation；cancel後已成交仍保Fill；futurepreviousbasis100 settlement103 qty2 multiplier10→variation60，newbasis103 price104→unsettled20，total80；noFXconvert不能USD+TWD；groupA+1/B−1不能internalFill；European/American profile不互替；oldrevision/corruptartifact拒publication/admission。Hash/DTO/alias/schema/generationgoldens是 implementationqualification 必交的具體bytes/數值測試；本稿規格不是已執行RuntimePASS。

## RCG03 candidate.4 Research/LAB service addendum

本節只補E/F Research Pipeline原責任，不修改上文accepted money／OMS／Broker semantics。詳細shape/state/oracle見 `LAB_LIFECYCLE_CONTRACTS.md`、catalogs與 `RCG03_LAB_FIXTURE_ORACLES.json`。

| Service | Exact input→output | 必要規則／failure／consumer |
|---|---|---|
| SourceAnalyzer.analyze | SourceAnalysisRequest→SourceAnalysisReport | 原 bytes/hash/tool/catalog/budget，AST-only；license UNKNOWN不變允許；UI04/E Feature只看候選，不直接execute |
| ArchivePlanner.preview | ArchivePlanRequest→ArchivePlan | provider安全locator/normalizedfilename/duplicate/hashconflict/rename-move預覽；無filesystem effect |
| HumanArchiveService.execute_or_reconcile | ArchiveExecuteRequest→ArchiveOperationReceipt | Human exactplan，CreateNew→verify→durable receipt→approvedcleanup；同id/hashreplay；crash UNKNOWN不blindrepeat |
| BuilderGraphValidator.validate_edit | BuilderEditCommand→StrategyGraphRevision | scopedCAS；Feature/Rule/Substrategy/Safety；fullnestedDAG/ports/lookback/minENTRY-EXIT-RISK；Safety OFF及lastrequiredOFF422 |
| ResearchBranchService.create_or_clone | BranchCreateRequest/BranchCloneRequest→ResearchBranch | firstroot parent0，clone parent1，永久normalizedaliasallocation/rootCAS；history append-only；archive不deleteEvidence |
| ResearchCodeService.generate_or_capture | exactgraph+generator+lock / manualcodecontent→GeneratedCodeRevision | manualedit新revision＋CODE_DIVERGED，不悄悄逆構圖；oldpublishedrefs immutable |
| SnapshotSealer.seal | ResearchSnapshotDraft→ResearchSnapshot | exact branch/graph/code/features/datasets/config/engine/profiles，全closure；sourceMissing/corrupt拒seal |
| AIAnalystService.start_poll_cancel | AnalystRequest→AnalystRun | Humantriggered finitebudget≤5trials；fixedbaseline/benchmark/validation；RESEARCH provider不是Coding executor |
| AIAnalystService.apply_selection | AnalystApplyRequest→ResearchBranch | Human exactselectedsnapshot/validationstatus，新branch，不library/deployment；noimprovement保1–2未驗證方向 |
| LibraryApprovalAdapter.approve | exactsubject+normalqualification/LibraryExceptionApproval→LibraryRelease | 例外只未simulation；permanentwarning不能刪；source/sandbox不豁免；L runtimeadmission独立 |
| LabSimulationService.create_or_recover | ResearchSimulationRequest/SimulationRecoveryRequest→ResearchSimulationAccount | scopeLAB、獨立virtualcapital、STANDARD exactconfig；hotchange forknewaccount；不寫Jactualcapital |
| SimulationObservationPort.record | exactsourceevent+quality→SimulationObservation | immutable OBSERVED/RECONSTRUCTED_ESTIMATED/UNRESOLVED；後補newrevision非改source；mode/fillquality顯式 |
| SimulationQualifierProjector.project | immutable observationrefs/profile/frontier→SimulationQualificationCounters | replay/estimate/unresolved不能計forwardobserved；profile尚未adopt保持未qualification；UI07/E Library readprojection |

原 BacktestEngine/Feature Registry/Decision/Economic writer重用經adapter，不另造相同authority。每個service的projection consumer只讀exact revision/receipt，outbox重送sameevent/hash冪等，differenthash conflict；不能由event名稱或存在檔案製造Library/RUNTIME qualification。合成fixtures是設計驗證，provider/Windows/SQL/sandbox/forwardsource/engine實測均NOT_RUN。
