# CC03／CC05 版本化資金與傳輸補充契約 — candidate.5

Subject：`MA-ARCH-REVIEW-v5-CYCLE01`。Owner：原 G_CAPITAL／J_ACCOUNT／B_DATA／N_APPLICATION；本文件為設計提案，無執行或採納權限。狀態 `CLOSED_PROPOSAL_PENDING_INDEPENDENT_RE_REVIEW`。SQL、PG concurrency/crash、Broker、PAPER、UI及跨語言 runtime資格均 `NOT_RUN`。

## 來源、限制及方案選擇

Rev2 `LAB_REV2_MD.md` N02（36–43行）確認 `100 × 90% = 90`、群組45／45，權益變為30／80後仍凍結90／45／45；只有明確更新採人工確認新基準110，沿用90%及50／50後，預覽99／49.5／49.5，確認才提交。N03（45–51行）確認安全可轉額、單帳戶原子CAS、超额不自動平倉。Rev2 JSON `#/confirmed/N02`、`#/engineering_defaults_not_user_signoff/budget_refresh`、`fill_allocation`、`#/confirmed/DEC-TRADE-ATTR-02` 保留。逐檔實讀SHA256及selector見 `SOURCE_EXACT_BINDINGS.json`；沒有重問已確認功能。

v4單一`reference_amount`不能區分110×90%與99×100%，因此採獨立人工基準、比例、總額與分配，不以改欄位名稱當作語義修正。雙page採相等或拒絕的相容方案；既有API canonical errors保留，disposition table改為同詞彙，舊表用具版本alias解碼。所有舊candidate／Rev2／接受憑證原bytes保留。

本文件不修改已接受R01的DecisionCut、FinalWitness、T01/T12、closed Fill constructor、SEALED經濟事件政策或J AccountAuthorityCommitService ownership。只在原資金／會計application service及read projection承接版本化companion，不設第二個經濟writer。無多貨幣或跨帳戶移轉批准；產品resource adapter欠缺資格時UNKNOWN／HOLD。

## 完整人工政策及欄位責任

`ManualCapitalReferenceRevision`是原MANUAL政策的來源companion：不可變account/environment/currency、人工確認額、Human receipt、Owner source decision、prior revision。不是券商即時數據，不能自動由最新權益填入。

`AccountBudgetPolicyDraft`及提交後`AccountBudgetPolicyRevision`完整保存：manual_reference_ref、manual_capital_reference、budget_ratio、budget_total、rounding_policy_ref、Owner來源、Human確認及prior_ref。`reference_amount`只是candidate.4相容alias，必須等於manual_capital_reference；從此不可稱作budget_total。舊v4只有reference_amount而缺ratio的歷史body不能靠猜測升級；只有找到exact原始ratio＋人工來源才建立新revision，否則MISSING／UNKNOWN。

`AccountAllocationSet`完整保存exact confirmed policy、account、group/deployment唯一集合、比例、總額、各層unallocated及rounding trace。總和綁`budget_total`。群組策略比例明確以group budget為父層，不能誤用全帳戶總額。未編輯比例沿exact prior policy／allocation承接，不能從30／80權益推導新的30／80配置。

`BudgetAllocationPreview`包含完整typed proposal、manual source/value/ratio/total/splits、actual-equity與executable-capital來源觀察ref、AccountCut、dependency closure、policy/head generations、reservation frontier、expiry、available/uncertain/reserved/deficit。Human UI可讀完整body後才确认。`BudgetAllocationConfirm`固定上述exact refs/hash/cut/frontier及Human decision；`BudgetAllocationReceipt`只在全集合COMMITTED存在，保存提交後policy/allocation/budget refs及相同計算摘要與result cut。

`BudgetCapitalObservation`是既有J/G真相的唯讀投影。actual_equity與executable_capital獨立，各有KNOWN/UNKNOWN與來源；未知值null不是0。既有instrument/resource policy未qualified，不能因預算99便宣稱可買99。Human的110人工基準也不等於110可用現金。

## Decimal／比例／幣別及可執行計算

Money維持既有Decimal字串wire；本預算companion要求：純十進位、不接受float、NaN、Infinity、指數或千分位，canonical不含前置零、尾隨零及負零。整數字串`0`及`110`，小數`49.5`；金額與ratio使用任意精度整數／有理數中間值，禁止IEEE754作authority。wire canonical JSON為UTF8無BOM、排序keys、無多餘空白；輸入`90.0`可在UI轉為`90`，server contract接受canonical字串，不能各端自行不同rounding。

`BudgetRatio`保存reduced unsigned integer numerator/denominator；分母>0、gcd=1、0≤ratio≤1。90%=9/10，50%=1/2。group ratios總和≤1，strategy ratios在各group內總和≤1；差額是明列unallocated bucket。舊weight_percent是exact比例×100的顯示alias，結果無法有限十進位表達時省略，不能用近似decimal覆蓋rational。每幣policy只處理一幣，quantum由exact versioned planning precision policy決定，與券商交割精度分開。本合成golden採TWD0.01只是planning fixture，不宣稱市場法定結算單位。

總額：`raw_total = manual_reference × ratio`；`budget_total = floor(raw_total / quantum) × quantum`，低於一quantum的差額保存total_floor_residual。保守下捨維持不超過人工上限，不隱藏餘數。

分配：父層已是quantum整數；各bucket exact quota=parent×ratio。先各自floor_quantum，將剩餘quantum依exact小數餘額由大到小分配；同餘額按永久Entity UUID network-byte ascending，unallocated bucket最後。策略層重用相同演算法，包含strategy_unallocated。明列exact quotas、floors、award keys、rounded amounts及總額捨入殘差。每層`sum(children)+unallocated=parent`，重播順序不影響結果。百分比與請求供應的group／strategy摘要若不等server計算結果，422；不能任選一個欄位。

合成oracle：100×9/10=90，兩group各45；110×9/10=99，各49.5；120×9/10=108，各54。1.01×1，三group各1/3，floor0.33/0.33/0.33後剩0.02，永久ID排序前兩group各獲0.01，結果0.34/0.34/0.33。99×1雖同總額，來源與policy hash不同，不可冪等混同110×9/10。

## 單帳戶CAS／UoW及可用資源

1. Preview命令只持久化不可變preview/body/receipt；不寫allocation、cash、position、PnL、broker或經濟事件。
2. Confirm先讀scope+command_id下receipt；同canonical payload hash重播原result，異hash409並依已存receipt決定effect，不能再執行。
3. 進入原account-scoped UoW後核expected account/allocation generations、exact policy/manual reference、complete AccountCut及每個recovery-critical dependency、reservation frontier、Human decision/expiry、availability policy資格。
4. 新reservation、partial fill、settlement、未知outcome、cut或配置head改變使舊preview STALE／409；不能將最新cut偷換到舊Human approval。重新preview產生新subject後另明確確認。
5. 同transaction append policy/allocation/group/strategy budgets＋heads＋audit／command receipt／outbox。結果只有全有或全無。只更新planning budgets，不生成deposit、cashflow、return、lot或Fill。
6. Transfer另外經既有合法service，只可用實際安全未占用額。qualified adapter先將overlap的position/margin/order/settlement claims正規化為互斥claim，避免同額重扣或重credit；`max(0,min(unencumbered_budget,unencumbered_cash,account_safe_available)-exit/safety reserve)`。任何來源UNKNOWN／stale禁止轉出或增加風險。提升額度不就是transfer。
7. 降額低於現有occupation，保留部位、標明deficit、阻止新risk增加，不默默賣出或把其他group資金補上。風險減少及明確後續處置沿既有policy，不在此創設交易授權。

兩Human確認同allocation generation時只有一個成功，另一409；winner新增完整revision集合一次。兩策略各需要60而帳戶safeavailable100時，第一reservation60，第二僅見40且拒絕；group額度不是兩份可各自重用的account cash。beforecommit failure全NO_EFFECT_PROVEN；commit後ack遺失UNKNOWN／QUERY_RECEIPT，不能blind resend；restart後同command/hash從durable receipt恢復同result。

## 部分成交、修正及OriginMapping不變式

每原intent/order固定一account/group/deployment/release/policy的OriginBinding；所有partial fill保留同origin。原broker fill identity/hash冪等：同內容no-op，異內容CONFLICT／HOLD；未知external fill留EXTERNAL_UNASSIGNED及suspense，不憑ticker/current budget/current deployment分配。

同一原economic UoW將已成交資源由open-order reservation轉為可信position／settlement／fee claim；這是claim轉換，不是額外扣款或免費資源。未成交、cancel pending、UNKNOWN剩餘部分依qualified worst-case政策保留，不可單用filled_qty/order_qty比例釋放cash。填成40／原100且unitcost1的簡化fixture，position claim40＋remaining-order claim60=100；UNKNOWN剩餘時60仍占用，account safeavailable不因收到40成交而多60。price/slippage/fee/margin非線性商品須exact資產policy，未知便HOLD。

cancel與late partial競態先去重accepted fill及因果frontier；只有可信完整terminal proof＋final fills＋settlement/margin依賴可釋放真正未占用餘額。expire、pause、UI取消、socket timeout不是terminalproof。rebudget110→99不重標任何已成交origin，歷史PnL也不改。

OriginMapping correction使用既有J／AttributionCorrectionRecorded的audit successor authority：保存original mapping、來源、corrected mapping、prior/supersedes refs、Human決策、causal/economic cut及reason；不能overwrite原Fill/intent/EconomicEvent或回改SEALED terminal。需資源重新歸屬時使用既有明確批准而且quantity/cash守恆的successor，不自動重播原economic apply，不改已有order reservation ownership。缺合法correction權限HOLD。本輪不創新correction API或多deployment split grant。

同股票groupA100shares，groupB50shares，B賣30後A100/B20；無授權不能B賣A股。opposing intentions不得產生internal fill、互抵、transfer lots或借額度。實際broker持倉與各origin projection reconciliation獨立保存，總量相等也不證明歸屬已知。

## queryMarketBars單一有效page

outer `page`及`query.page`都optional。只有一個提供，採該完整物件；兩個提供必須canonical逐欄完全相等（limit/cursor/snapshot_ref/sort_key/filter_hash），否則422 `SEMANTIC_VALIDATION_FAILED`，FieldViolation同時列`page`與`query.page`。不能只比cursor，也不能任選inner或outer。兩者缺席，server固定limit100、sort=bar_start_asc、snapshot=query.dataset_snapshot_ref、filter_hash=exact非pagination BarQuery canonical hash，cursor absent。

分頁snapshot_ref必須等dataset_snapshot_ref，filter_hash由server重算；簽署cursor另綁actor/account/env、immutable snapshot、filter、sort、limit、schema版本及expiry。innerS1/outerS2及不同limit/cursor/filter/sort皆拒絕；單個cursor內容與snapshot/query不符409 canonical conflict，未授權scope403。該query的BarQuery.page不納入non-pagination hash，避免自我參照。end exclusive、known_as_of、來源calendar／policy／adjusted/raw／continuous約束仍沿原MA03；空集只有正面completeness proof才是COMPLETE。

## 共用錯誤詞彙、版本alias及GoldenWire

候選v5Outgoing `ErrorEnvelope.protocol_version=architecture.transport_error.v2`。`API_CATALOG.errors`和table每status使用同canonical code：401 AUTHENTICATION_REQUIRED；403 RESOURCE_SCOPE_DENIED；404 RESOURCE_NOT_FOUND；409 CAS_OR_HASH_OR_ALIAS_CONFLICT；422 SEMANTIC_VALIDATION_FAILED；429 RATE_LIMITED；503 DEPENDENCY_UNAVAILABLE_WITH_RECEIPT_WHEN_EFFECT_POSSIBLE。409涵蓋CAS／hash／alias／cursor conflicts，detail用FieldViolation及safe reason，不創未登錄的cursor code。

table保存完整read/command分支；retry及effect來自invocation journal／durable receipt證據，不由status猜測。401／403只在pre-invocation denial證明NO_EFFECT；404 authorized read為NOT_APPLICABLE，command missing在執行前才NO_EFFECT；409既有command/hash conflict若已commit則EFFECT_COMMITTED/QUERY_RECEIPT、未知則UNKNOWN/QUERY_RECEIPT，不能一律NO_EFFECT；429 read可RETRY_SAFE_READ，command uncertainty查receipt；503 read WAIT_DEPENDENCY，command UNKNOWN或已commit但ack未知查receipt。缺operation_ref的未知command仍可用known command_id透過既有getOperation exact scoped lookup，不自行重送。

incoming旧詞彙只在明示`architecture.transport_error.v1.api_catalog`或`architecture.transport_error.v1.disposition_table`按列出的alias轉換，保留或保守降級未知effect；不能無version按HTTP猜。未知version/code → DO_NOT_RETRY，安全訊息、保留correlation，已知command查receipt。refresh／reauth／resnapshot不會extend原Human subject或trading grant。

Python service、.NET BFF、TypeScript client採同份`CC03_CC05_GOLDEN_FIXTURES.candidate.5.json`。golden保存canonical UTF8 JSON文字及SHA256、完整synthetic ContractRefs、Decimal string、Ratio integer string、typed model/request/error fixture。每語言將解析結果再序列化成同canonical bytes，逐byte／hash相等；所有負例須同status/code/retry/effect及zero/recovery disposition。這是未来cross-language qualification oracle，本輪只執行Python設計計算與shape检查，不能宣稱.NET/TS或runtime通過。

## Consumers／Units／驗證及剩餘資格

fragment.json提供完整models_replace/add、structs_replace/add、enum bindings、四個API replacement、errors及table replacement、affected永久Unit IDs與operation-level producer／consumer、secondary IO、positive/negative/race oracles。所有95 operation IDs及96 Unit IDs保留；root建立succesor plan revisions／sourcehash／schema bindings。`getOperation`及OperationReceipt shared model不變。

CC02必須承接typed BudgetAllocationPreview／BudgetAllocationReceipt exact-body readback：由OperationReceipt.result_ref／body resolver取得expected model/revision/hash/account/env，cold-load、確認前Hash／型別／revision／scope、missing private bytes顯式不可用；不能用latest或虛構預覽。readback producer的root整合未完成前，本片段不宣稱完整B3 closure。

`design_oracle.py`以實際算術與狀態機跑原budget案例、rational及餘數、dual-page各欄衝突、每error分支和version alias、兩confirm／reserve race、UNKNOWN partial/cancel、idempotency/restart、origin保留及拒借別group。結果是author design consistency evidence，狀態只能`AUTHOR_DESIGN_CHECKED`。獨立Reviewer必須對新exact subject另行裁決。

仍需依法授權WORK：真正PG兩連線CAS、account UoW atomicity、reservation/economic crash、invocation/receipt durable recovery；qualified各資產cash/margin/settlement policy與broker callbacks；Python/.NET/TS GoldenWire執行；UI02/UI08 cold reentry／Human preview／95API integration。全部`NOT_RUN`，無runtime／SQL／publication／dispatch progression。
