# MA09 — Broker Gateway 與具體 Shioaji Adapter

Revision `candidate.3`；Owner I Broker Adapter；DESIGN_DRAFTED；documentation source review ≠ runtime capability verification。

## Purpose／Source／Reuse

沿用 I_BROKER_ADAPTER、existing shioaji mapping/fill/contracts seams、GAP08 broker capability classifications。Adapter 只翻譯 broker-native objects/IO，不能決定 accountnettarget/riskapproval 或 expectedposition。Core 無 `sj.*` dependency；ASP.NET／React 不接 SDK。採 SDK 版本明確鎖定，官方1.7 及後續範例與舊程式有 API/物件差異，不默默升級 acceptedadapter。

本次官方文件查核日2026-10-11：

- [Login/support](https://sinotrade.github.io/tutor/login/)：國際複委託 API trading 未支援；不能由 platformfullscope 推出 broker 涵蓋 USstocks。
- [Contracts](https://sinotrade.github.io/tutor/contract/)／[1.7 upgrade](https://sinotrade.github.io/zh/upgrade_to_1_7/)：native contract lookup/object 依 SDKrevision 選 adapterprofile。
- [Stock order](https://sinotrade.github.io/tutor/order/Stock/)：place/update/cancel；stocklot/condition 與 qtyunits 要顯式 mapping，custom_field 小欄位不能當全球永久 id。
- [Futures/options](https://sinotrade.github.io/tutor/order/FutureOption/)：FuturesOrder/price/TIF/open-close typed mapping，不能從 IDprefix 推 New/Cover。
- [Order/deal callback](https://sinotrade.github.io/tutor/order_deal_event/)／[status](https://sinotrade.github.io/tutor/order/UpdateStatus/)：callbacks 及 statusqueries 仍需本系統 durablejournal/currentness/duplicateprotection。
- [Positions](https://sinotrade.github.io/tutor/accounting/position/)／[margin](https://sinotrade.github.io/tutor/accounting/margin/)：query 可得到 accountobservations，不能代替 internalexpected 或完整 recoveryproof。
- [Vendor simulation](https://sinotrade.github.io/tutor/simulation/)：獨立 vendorenvironment，不能代表自家 STANDARD 或真實交易資格。

## Capability Model／Negotiation

CapabilityRevision 固定 provider+SDK+adapter+accounttype+environment+instrument/market+operation+orderqualifiers+source＋qualificationreceipt。三態 SUPPORTED_QUALIFIED／DOCUMENTED_UNQUALIFIED／UNSUPPORTED_OR_UNKNOWN；unknown operation deny。Capabilities 包括 submit/cancel/amend/readorders/readfills/readpositions/readcash/margin/marketdata、historywindow/querycompleteness、timeouts/nativecorrelation、minimumunits/rates；每操作不依賴其他 PASS 推定。

| Product/operation | 本次 source disposition | Runtime route |
|---|---|---|
| TW listed stock/ETF | documented stockpath；每 listing/condition/lot 需 qualified | 股票帳戶＋精確 contract/MarketRule＋permission |
| TAIFEX futures/options | documented futoptpath；每 contract/effect/TIF 需 qualified | 期權帳戶＋explicit New/Cover/effect |
| Combo/orderextensions | 另 capability，非 simpleorder 自動繼承 | 未 qualified 拒絕，不自動分腿 |
| US 股票/個別 bond/funds/spotFX/其他 market | 本輪無 Shioaji 交易支援證據 | research/PAPER 可設計；LIVE gateway 返回 UNSUPPORTED |
| Exactly-once submit/nativeclientkey | 尚無可依賴完整契約證據 | localdedup＋UNKNOWNhold/query；不承諾 broker 冪等 |
| Account queries/empty completeness | documented query≠完整 cut 資格 | scope/run/completeness proof 待 Qualification |

## Adapter Interface／Mapping／Methods

`connect(session_config_ref,secret_handle)`：僅 adapterprocessresolvecredentials、authenticate/selectexplicitstock/futoptaccount/requiredCA；返回 SessionReceipt＋SDK/profile refs。`negotiate(scope,operations)`返回 capabilityrevision；`resolve_contract(listing_ref,mapping_ref)` exactnativecontract 或 typederror。`submit`建 StockOrder/FuturesOrder＋nativeplace_order，回 nativeTrade 投影/UNKNOWN；`cancel`對 boundnativeTrade 呼 cancel_order；`amend`只 qualified update_order；`query_orders`以 account update_status/list_trades nativeprofile；`query_positions`list_positions；`query_margin`margin；每 methodactualsignature 以 pinnedSDKtest 固定，舊 profile 用自己的 adapter 不混 API。

Stock：sideBuy/Sell、LMT/MKT 與 ROD/IOC/FOK、lot(Common/Odd/IntradayOdd 等)、condition(Cash/credit 等) independentbindings；只有 qualifiedcashbasicroute 可 admit，borrow/short/credit 權限不能猜。內部 sharequantity 轉 SDK lotquantity 需 instrumentlotpolicy；不能硬除1000 套所有商品。

Futures/options：canonicalqty 是 contracts；profileprice/tif mapping；PositionEffect OPEN→New、CLOSE/REDUCE→Cover（以 exactSDKenum profile），不默認 Auto，不從 ENTRY-/EXIT-字串猜。合約到期映射必 exactlistedcontract，連續代碼/rollingselector 不能在 send 時無聲轉另一 expiry。

Native callbacks：`set_order_callback`接 order/deal 訊息，只 capture/spool 到 boundedqueue，consumercanonicalize/dedupapply；callback 不能直接 neworder。Raw native IDs/status/seq/trade qty 在 privatepayload，canonicalhash/correlation/adapterrevision 可 audit。nativeunknownenum→UNMAPPED_EVENT+hold，保留 rawcontent 供 Human，不能 map 成 REJECTED 或 FLAT。

## Lifecycle／Retry／Recovery／Failure

Session CREATED→AUTHENTICATED→ACCOUNT_SELECTED→CAPABILITY_BOUND→OBSERVING→READY(ifMA08gates)；DOWN→RECONNECTING→OBSERVING，非立即 READY。Sdkupgrade/newcontractcatalog→newprofile+requalification，只 affectedoperationsinvalidated。RateLimit 僅 safequery 有限 backoff，orderexternalUNKNOWN 不 autoresubmit；cancelackunknown 查 status/fills，不釋放 pendingquantity 直到 closure。

Query completeness receipt 固定 accountselector、instrumentuniverse、runid、requested/coveredwindow、nativeprofile limitations、success/error/explicit-empty、captured_at/frontier；不能聲稱 SDK 提供全歷史與全球 sequence。若 orderIDcorrelation 不足，保留 manualresolutioncase，不以相似 price/qty 自動唯一 match；關聯 Hash 不是確實 brokerrecognition。

## Security／API／UI／Dependencies／Compatibility

SecretHandle resolve 需要 existingAuth/SecretProvider、無 export/log/querydisplay；證書路徑/密碼不出 adapter。Operator/financialaccount/nativepersonID 分開，PIIredact 在 boundary。GatewayonlyPythonapplicationprivateport；BFF `/api/v2/broker-capabilities` read，connectioncommand 具 resource/environmentpermission，UI 顯示 documented 與 qualified 差別，不能點 connect 就 LIVEadmitted。

MA02profiles→contractmapping；MA07witness/admission→MA08→I；Iobservation→H/J/K；MA13privatebackupcapture 適當 licence/privacy。Existingnativefuturesadapterreusequalifiedsubset，newstock/ETFprofilecompanion，不搬移 package 以破壞既有 imports。

## Examples／Acceptance／Tests／Handoff

正：stocklotunit 明示、optionsCover 對 exactcontract、unknownstatuscapture 後 hold；反：API 登入成功當所有 asset 支援、把 custom_field=globalUUID、placeordertimedout 再 send、拿 positionempty 當 completeFLAT、SDK1.7 程式套舊 enum 無 test、fundtypefakeStockOrder。

Acceptance：matrix 每 cell 有 source/revision/quallevel、unsupportedfailclosed、SDK/nativeobjects containment、accountselectionexplicit、quantizationunits、callbackdurability/dedup/unknown、completequerylimitation 明示。Tests：mappinggoldens 每 asset/lot/TIF/effect、nativeenumdrift、partialdeal/outoforder/duplicate、connection/rate-limit、lookupambiguous/expiry、callbackoverflowspoolfailure、queryempty/error distinction、PII/secretsredaction。fake tests、vendor simulation、read-onlyconnectivity、trueorders 各獨立 Gate；本次皆未執行。

WORK units：profile/capability registry、contract/accountmapping、stock/futoptordertypedadapter、event/queryreceipts、session/reconnect/ratepolicy、安全 filter。只有合法限定 WO 才可 SDKinstallation/DB/brokerruntime，真實 credentials/order 必獨立 Human grant。

## 本次有界補充契約

[ECONOMIC_RESOURCE_CONTRACTS.md](ECONOMIC_RESOURCE_CONTRACTS.md)、[MONEY_SUBMISSION_CUT_PROTOCOL.md](MONEY_SUBMISSION_CUT_PROTOCOL.md) 為本章不可省略的候選 companion；typed resource/obligation、T12 witness、export adapter 與 exact dependency/source bindings 必隨章節 subject 一起編譯及審核。原 accepted predecessor 不變。
