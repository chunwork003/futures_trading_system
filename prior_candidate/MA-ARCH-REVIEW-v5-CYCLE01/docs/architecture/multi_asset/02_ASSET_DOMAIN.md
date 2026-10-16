# MA02 — 多資產 Domain、商品生命週期與估值契約

Revision `candidate.3`；Owner D Canonical Domain／C Calendar Contract；狀態 DESIGN_DRAFTED。

## Purpose／Scope／Source／Reuse

以既有 `D_CANONICAL_DOMAIN.md`、`C_CALENDAR_CONTRACT.md`、ADR-001 與 accepted contract identity 為前身。新 InstrumentProfile 是 versioned companion，保留舊 futures Instrument／integer contract ID 的 immutable bridge，不大改 closed constructors。來源：最新 Human 多資產要求；市場規則由 SOURCE_REGISTRY 的 S0 exchange、S1 vendor exact source versions 管理。

TWSE 普通交割規則與 TAIFEX TX 規格本次已查官方來源，但它們不能覆蓋所有商品。規則引用：<https://www.twse.com.tw/zh/clearing/clearing/operations.html>、<https://www.taifex.com.tw/cht/2/tX?menuid1=12>。例示 TW 普通證券 T+2、US 一般證券 T+1 需各自 policy/calendar，非全商品常數；US/特殊商品上線前重新驗證官方 profile。

## Data Model／Inputs／Outputs

Instrument 永久 ID；Listing 有自己 ID，指向 instrument、venue、symbol、currency、validity。Symbol 不是全球唯一；同經濟商品可有多上市／幣別。DerivativeContract 是到期、strike、option right、underlying、settlement 的不可變身份，continuous future 只是 research series，不可下單。InstrumentRevision 固定產品條款，MarketRuleRevision 固定 tick/lot/session/settlement/fees/tax，ValuationPolicyRevision 固定算法與模型。

| Entity／欄位 | 必要語義／驗證 |
|---|---|
| Instrument | id, kind, issuer_ref?, economic_currency, lifecycle；kind 候選 enum EQUITY/FUTURE/OPTION/ETF/BOND/FUND/FX_PAIR/CASH |
| ListingRevision | instrument_ref, venue_ref, local_code, quote_currency, quantity_unit, status, effective_interval；source-qualified unique |
| ProductTerms | multiplier>0, face_value?, quote_basis, maturity?, settlement_style, exercise_style?, underlying_ref?, contract_size；按 kind 選 typed extension |
| MarketRule | tick ladder、lot/min quantity、allowed order/TIF、limit policy、session/calendar、settlement currency/day rule、short permissions、fee/tax policy refs |
| CashFlowSchedule | immutable leg IDs、currency、accrual interval、day count、reset/fixing、payment date/calendar、principal/coupon/dividend type、source revision |
| CorporateAction | announcement/effective/record/ex/pay dates、ratio／cash、affected refs、source/correction；estimated 與 confirmed 分開 |
| PricingObservation | quote_ref, as_of, source_sequence, bid/ask/last/NAV/model, currency, quality；未知值 null＋reason |
| ValuationResult | positions/cash refs, price/FX/curve/model refs, as_of/cut, value/currency, sensitivity, confidence、missing inputs |

重要函式契約：`resolve_listing(source,code,at)` 唯一 profile 或 AMBIGUOUS；`validate_quantity_price(profile,order)` 返回 normalized units 或違規原因；`schedule_cashflows(terms,calendar)` 無副作用 immutable schedule；`value_position(position,cut,policy)` 返回 result＋完整 dependencies，不取得交易權限；`bridge_legacy_id(catalog,id)` 持久一對一映射，同 ID 異內容 conflict。

## 各資產專屬商業規則

| Asset | 計價／現金流／持倉 | 風險與事件 |
|---|---|---|
| TW/US Equity | share quantity；cash consideration=price×shares；交易與交割 balances 分開；dividend entitlement 依 record/ex policy | split/reverse split、dividend、rights、delisting；short availability、lot/tick、settlement calendar |
| Futures | contract quantity；notional=price×multiplier×contracts；margin 非買價；variation settlement 由官方 policy | expiry/roll、daily/final settlement、margin calls；cash/physical settlement 不能混同 |
| Options | option contracts；premium=price×multiplier×qty；underlying/strike/right/expiry/exercise binding | Greeks/model inputs、exercise/assignment、writer margin、cash/physical obligations；未確認自動履約不可猜 |
| ETF | listed share＋fund exposures metadata；交易價與 NAV 分開 | distribution、tracking、liquidity、premium/discount；leveraged/inverse daily reset path dependence，不能用固定倍數長期報酬 |
| Bonds | face/notional quantity；clean price quote basis(%par/perunit)；dirty=clean+accrued；coupon/principal separately | day count、excoupon、call/put、default、duration/DV01/convexity、settlement accrued adjustment |
| Funds | fund unit quantity；NAV dealing/cutoff、subscription/redemption、settlement delay | pending order 非 exchange Fill；loads、gates、suspension、share class/fee/FX rules |
| FX | base/quote 明確，rate=quote per base；spot/forward 不同 product terms；兩幣現金腿 | pip/lot、value date、holiday calendars、forward points、funding/rollover；本輪不預設 Shioaji 支援 |

Fixed coupon schedule：每期 coupon=notional×annual_rate×day_count_fraction，具體 coupon convention/rounding 依 terms。折現 value=sum(cashflow_i×discount_factor_i)，dirty/clean transform 明示 accrued policy。Yield 根搜尋須報無解/多解/收斂資訊，不能 0 代替失敗。DV01 的 curve bump、parallel/nonparallel、currency 及 sign 固定在 policy。期權 Greeks 不得將 stale implied volatility 或缺 curve 當成可執行風險事實。

Capital/valuation 用 Decimal、保留原 currency amounts；research vector float 可用，但轉入交易須 explicit quantization／precision proof。Currency conversion 只在 ValuationResult 使用 versioned FX cut；不直接改寫原現金帳。不同 listing 不能因共同 instrument 就視為同一可交割庫存。

## Lifecycle／Events／Interfaces／Dependencies

Instrument：DRAFT → VALIDATED → ACTIVE → SUSPENDED → RETIRED；retire 不刪歷史。Derivative ACTIVE → EXPIRING → EXPIRED → SETTLED；correction 形成 successor event。Listing rules valid interval 不重疊，announced revision 可以 future-effective。舊 accepted trading observations 指向原 revision，不能 current-head join 改歷史。

Events：InstrumentRevisionPublished、MarketRulePublished、CorporateActionConfirmed、CashFlowDue、SettlementObservationRecorded；event 並不直接更動持倉，MA06 economic writer 決定適用入帳。API `GET /api/v2/instruments`、`GET /api/v2/instruments/{id}/revisions/{rev}`、`GET /api/v2/market-rules/{id}`；管理 Draft 走既有 publication gate。MA03 produces observations、MA04/05 consume research profiles、MA06 accounting、MA07 risk、MA09 broker negotiation。

## Error／Retry／Concurrency／Security／Compatibility

Missing/ambiguous listing、unknown policy、expired contract、wrong currency/unit、tick/lot invalid 回 typed validation failure；不得自動近似成另一合約。revision publication generation CAS、valid interval overlap exclusion；所有 artifact bytes hash binding。公共 issuer data 可 Public，account holdings 私有。Untrusted instrument files 只解析資料，不能動態 import code；provider correction 不直接 mutate accepted terms。

LegacyAdapter 只映射已驗證 futures subset；新 kind 不導入舊 futures API。不同 currency/settlement styles 若舊 DTO 無欄位，v2 companion 包含 ref；v1 consumer 明確 UNSUPPORTED，不吞欄位。Canonical domain 不依賴 backtest、broker SDK、ORM。

## Examples／Acceptance／Test Strategy／Handoff

正例：同 ETF TWD/USD listings 共 instrument、不同 listing/currency/settlement；bond 100 face price98＋accrued1，dirty consideration99 與 coupon schedule 分開；TX/MTX 不同 multiplier profiles。反例：把100USD 股票現金支出當期貨 margin、將 continuous future 送 broker、option assignment 當普通 sellfill、ETF 逆向兩天固定負倍數、fund redemption 無 NAV 便造 Fill。

Concurrency：兩 writers 同 effective_interval 發布不同 tickpolicy，只能一個成功另一409；corporateaction 重送同 ID 同 hash no-op，同 ID 異 hash conflict 保留原事件。驗收：每 kind 有 terms/valuation/cashflow/risk/settlement mapping；未知必 fail-closed；source revision 與 rules 時間固定；oldfuturesIDs/acceptedblobs 不變。

Tests：公式 fixtures、calendar 跨日/DST/holiday、fractional/share/bondunit precision、lifecycle/overlap、correction-history、legacy roundtrip、缺 price/curve/FX、long/short 及 cashflowdoublecount。真實市場/券商 profile qualification 另 Gate，模型測試不證交易所 conformance。

WORK units：identity/profile＋asset valuation strategies＋cashflow/CA＋legacy adapters；帶 sourceallowlist 與 goldenfixtures；protected 原 constructor/schema。Known limits：逐商品官方 rule 資料載入與 actualbrokerqualification 待實作；這不削除 asset 產品 scope。

## 本次有界補充契約

[ECONOMIC_RESOURCE_CONTRACTS.md](ECONOMIC_RESOURCE_CONTRACTS.md) 為本章不可省略的候選 companion；typed resource/obligation、T12 witness、export adapter 與 exact dependency/source bindings 必隨章節 subject 一起編譯及審核。原 accepted predecessor 不變。
