# MA06 — Portfolio、Capital、Cash Flow、Accounting 與策略歸屬

Revision `candidate.4`；Owner G Decision/Capital、J Account、K Persistence；AUTHOR_CHECKED／FORMAL_REVIEW_PENDING。

## Purpose／Source／Reuse

沿用 J_ACCOUNT_RECONCILIATION、K_PERSISTENCE_RECOVERY、accepted GAP08 AccountAuthorityCommitService（account_authority.py blob6a8a413861dbcf4ef268fde7685ea013960040ca）。Rev2 singleaccountstrategygroup/budget/PnL 為 delta。新財務帳本 companion 必須在同 accepted economic UoW 建立映射，不能新增 SQL 直改 Fill/position 的另一 truth writer。

## Model／欄位／責任

OperatorIdentity 為登入/角色，不是 FinancialAccount。BrokerAccount 具 provider/account/environment 身份；FinancialAccount 可有 currencyledgers 與 settlementsubaccounts；Portfolio 是 policy/reporting grouping，不產生額外資金。StrategyGroup 固定隸屬一 FinancialAccount/environment；Deployment 發佈策略版本在該 group 的實例。跨帳戶 portfolio 可估值 aggregate，不能把 cash/position 互用。

| Entity | 必要欄位／不可混用 |
|---|---|
| BudgetRevision | group_ref, amount/currency, effective_at, ownerdecision, priorrev；planning allocation，不是 bankdeposit/equity |
| AccountCut | accepted AccountStateHead、RecoveryCut＋cash/positions/orders/reservations/fees/settlements/frontiers；完整 dependencies |
| CapitalReservation | id、account/group/deployment、intent_ref、currency/resource、amount/quantity、cut/policy、fence、status；exclusive 資源計入 sharedaccount |
| EconomicEvent | id、sourcefill/corporateaction/settlement ref、occurred/received/recorded/effective time、account/environment、currency/unit、revision |
| LedgerEntry | event_ref、debit/credit account code、currency amount、value date、groupattribution/provenance、settledflag；每幣雙分錄平衡 |
| VirtualPosition | account/group/deployment/instrument refs、lotID、fill lineage、qty/cost/fees、markref；不能冒充 brokeraccountphysicalposition |
| AttributionRecord | sourceintent/fill/economicevent、origin group/deployment/release、allocation rule revision、amount/qty、unassigned status |
| ValuationCut | holdings/economicfrontier、prices/FX/curves、policies、NAV/PnL/availablecash/margin、missingdependencies |

## Business Rules／Input／Output／Functions

`reserve(intent,risk_receipt,expectedcut)`：account-scopedserial/CAS+fence，checkbudget＋actualcapital＋allactive/uncertainorders 保守 reservation；samecommandhashreceipt；發送前不能用 read-onlycheck 再各自扣款。`commit_fill(fill,origin)`：existingeconomicwriter exactly-once eventdedup＋position/cash/fees/attribution/outbox 同 transaction。`revise_budget` appendbudgetrevision，不製造 cashflow、不回改 oldfills；reservation 不足新 entry 拒絕而非更改他 groupbudget。

Actual equity=assetvalues＋cash＋receivables－liabilities，分 available/settled/encumbered；budget 是 Humanallocationreference。fees/coupon/dividend/tax/FXtranslation 可 distinctledger events，不能又併入 FillPnL 重算。Per-currency journal entries balanced；crosscurrency transaction 兩幣 legs＋FXclearing/valuationpolicy，不直接 sumUSD+TWD。

groupOrigin 在 OrderIntent creation 固定到 account/group/deployment/release/policy；Fill 續用原歸屬。改 group／rebudget 對 futureintents 生效。人工 mappingcorrection 是 auditedsuccessor 不能 rewriteeconomicfacts；broker 未知/外部 manualtrade 留 UNASSIGNED suspense，Humanclassification 後 newattributionrevision，不默認第一 group。

**禁止 groupinternalmatching/autooffset**：opposinggroupintents 不得虛構彼此 Fill、無 broker 成交就轉移 lots；不能出售另 group 持有的 shares。Physicalaccount 可能 exchange/broker netting，組合前 MA07 conflictpolicy 須 reject/serialize/人工處理 opposingintents；不能偷偷以 nettarget 消去各 groupeconomicclaims。broker 淨持倉與 virtualgroupssum reconciliation explicit，會計 roundingresidual 有指定 suspense/roundingledger，不丟失。

## 資產-specific 入帳／生命周期

Equity/ETF trade date 產生 inventory 與 settlementpayable/receivable，value date 確認 cashsettled；short/loan 有獨立 liability/borrowfees。Futures variationcash 與 pricebasis 按 settlementpolicy，不在 mark-to-market 及 dailysettlement 重複 PnL。Options premium 與 exercise/assignmentobligation 分開。Bond consideration dirtyprice、couponaccrued/purchasedinterest/principal 單獨 ledger；fund subscriptionpending 不是 Fill；FXtwolegsvalue-date 與 rate 固定。

Reservation HELD → SUBMIT_PENDING → CONFIRMED/PARTIAL → RELEASED；UNKNOWN／CANCEL_PENDING 資金保留到可信 terminalproof。Expiry 不可只 clock 釋放已可能送 broker 的 reservation。Budgeteffectivepastdate 不能回改 acceptedhistoricalcut；correction 有 effectivebusinessdate＋newrecordedrevision。Portfolio rebalance 決策→Risk→OMS 多 leg，不假設跨 market atomic；partialleg 風險 policy 由 MA07/08。

## API／Events／UI／Dependencies

Inputs MA02units/settlementpolicies、MA03prices、MA07approvedintents、MA08fills、MA09brokerobservation；Outputs MA07capitalavailability、MA08reservationreceipts、UIportfolio/cashflow/PnL、MA13recoverycut。API `/api/v2/accounts/{id}/capital`、`/strategy-groups`、`/budgets`、`/positions`、`/cashflows`、`/attribution`；writebudget 需 Humanrole/CAS，readDTO 帶 cut/currentness。Events BudgetRevised、CapitalReserved、FillEconomicsCommitted、SettlementApplied、AttributionCorrectionRecorded。

## Error／Recovery／Security／Compatibility

Wrongaccount/environment/currency/sourcebinding/duplicatefilldiffhash 拒絕；unknownbrokerexternaltrade 進 reconciliationcase、不 fabricateFLAT。DBfailurebeforecommit noack，aftercommitackunknown 查 receipt；cash/virtualposition/attribution 必同 UoW，projectionfail 可 replay。Recordlevelaccountpermissions; rawaccountIDs/交易明細 private，publicGit 只 schema/contracts/syntheticfixtures。Legacysinglefuturesaccount 映射只 qualifiedsubset；closedFillconstructor 用 OriginBindingcompanion keyed immutablefillID，不新增 silentenums。

## Examples／Acceptance／Test Strategy／Handoff

正：budget45/45、actualequity30/80 皆保；Human99→49.5each 只 newbudgetrevision；2groups 各預留60 但 account 只有100，onewins 另一 insufficient。反：重送 Fill 雙扣 cash、groupmove 重標 oldPnL、未知 orderreservation 自動釋放、groupA 賣 Bshares、不同 currency 直接 sum。

驗收：account-level 資源唯一控制、EconomicUoW/immutableorigin、sumattribution 與 accounteconomicevents 可 reconcile、budget 與 equity 分離、nointernalfills、所有 assetcashflow 合理平衡。Tests：concurrentreserve/twoconnections、duplicate/outoforderfills/cancelrace、doubleentry/multicurrency、settlement/CAcorrections、externalfillsuspense、recoverycutfreshness、projectionreplay。實際 SQLdurability/concurrency/crash 另 QualificationGate。

WORK：legacybridge＋originbinding/economicUoW adapter、capitalreserve、multicurrencyjournal、settlement/cashflows、valuation/attributionprojection、UI/API。不得大改 acceptedcore 或真實帳戶資料；重要 comment/docstring 繁中，moneyprecisionpoliciesexact。Knownlimits：actualmarketsettlement/brokerfees/positions/DBtransactions 需 qualifiedfixture 與 isolatedruntime 測試。

## 本次有界補充契約

[ECONOMIC_RESOURCE_CONTRACTS.md](ECONOMIC_RESOURCE_CONTRACTS.md) 為本章不可省略的候選 companion；typed resource/obligation、T12 witness、export adapter 與 exact dependency/source bindings 必隨章節 subject 一起編譯及審核。原 accepted predecessor 不變。


## RCG04 candidate.4 mandatory consumer closure

[TRADING_CAPITAL_UI_ADDENDUM.md](TRADING_CAPITAL_UI_ADDENDUM.md)與MODEL/TYPE/API/EVENT同版為本章不可省略契約；external EconomicOrigin、全帳戶budget preview/confirm、PAPER SimulationSession、MarketBar DTO、servercold-reentry/error/cursor/stream及consumer映射隨exactsubject一起審核。原accepted語義不變，Runtime NOT_RUN。


## Candidate.5 有界修正承接

人工資金基準×比例→預算總額，版本化群組比例與餘數；Actual Equity/Executable Capital分離；single account UoW/CAS/reservation frontier及Origin不可改寫。

唯一詳細契約：`CAPITAL_TRANSPORT_VERSIONED_ADDENDUM.candidate.5.md`。原已接受範圍與尚未完成qualification保留。
