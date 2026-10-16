# Account Cut → Reservation → Submission Protocol — candidate.1

Owner G/J/H/K；versioned companion，不改 accepted AccountAuthorityCommitService、ADR-001／ADR-002 或已封存 economics。此處固定新 group/capital handoff，禁止施工者把 own-reservation 當任意排除 dependency。

## 金融帳戶與來源

首版一 FinancialAccount 對一 environment-qualified BrokerAccount；包含多 currency ledgers，但不跨實際帳戶共享可用資金。Portfolio 對帳戶 N:M 只讀 reporting。未来 FinancialAccount多brokerconsolidation 需 explicit successor與不同reservationfailure-domain，不在首版自動聚合。Operator login identity與FinancialAccount永遠不同。StrategyGroup恆定隸屬一 FinancialAccount/env，Deployment/StrategyInstance/release/config明示，不用groupname代替。

已知order的ASSIGNED Fill必 exactorder+immutableOriginBinding。外部人工／未知order成交可 EXTERNAL_UNASSIGNED，以完整nativeaccount/listing/side/quantity/price/time/profile/evidence經原H/J accepted rules保存；不能生成假的intent/group/deployment/release。經濟證據未足qualify則保原始 bytes、UNKNOWN/HOLD，不先製造可交易expectedstate。后續Human歸屬是新AttributionRevision，原Fillidentity/economics不改。

## C0 → C1 → C2 有界自變更

1. G 在完整 C0 cut 作 RiskDecision R0：exact account/env/intent/listing/qty/price/rules/policy/cohort/capability/authorities/resource requirements。R0 是對C0的準備資格，不授予外部IO。
2. J account UoW 以 expected C0 generation+fence，重驗所有資源及authorities，建立reservation S並更新cut C1。mutation+ReservationTransitionReceipt T01+outbox 同commit。T01固定R0、C0/C1、唯一新增/變更的reservation ref及完整unchangeddependencyclosure；其餘任何delta拒絕此handoff，回G重新evaluate。
3. G 以完整C1重新作R1，資金計算明示 owned reservation S 的 earmarked funds **計一次**，不把 S 自己再當新消耗，也不重新當自由資金給別intent。R1精確綁S/T01/C1與原intent，不能把任意reservation欄位從cut hash排除。資金/市場/政策/cohort/其他reservation變更仍使R1失效。
4. H/J 在持有效account executor lease/fence下，以 expected C1，原子轉S為SUBMIT_PENDING並記durable send attempt A、final transition receipt T12/resultcut C2、final witness。T12只准精確自變更：S同amount→SUBMIT_PENDING、A PREPARED、對應journal/outbox/frontier；其他economic/resources/risk/context不變。FinalWitness綁R1+C1+T12+C2+A/S/lease/fence+authorities，表達已批准的自變更而非忽略currentness。
5. 外部IO前驗final witness/currentfence/C2、Human/environment/capability/kill policy；scope-scoped dispatcher 序列化同帳戶的 send/stop 許可，其他 writer不得越過fence。開始外部IO與遠端券商不原子：停機競態中已invoke者可能完成，持續capture、UNKNOWN/HOLD+reconcile。寫入若造成任何非授權delta，不能繼續使用舊witness。
6. ack/Fill透過原H/J/K accepted transaction進C3；未知outcome保留 S資源，不拿expiry釋放。exact command/attempt重送先查receipt，不newID resend。Crash在PREPARED且無可信no-invocation證明一律possible-effect UNKNOWN。重啟newepoch，T01/T12/R1舊epoch不可重新取得send權。

帳戶dispatch序列化不阻止raw broker evidence capture；callback先durablejournal，economic apply與send admission的順序由account authority epoch/frontier保留。backlog／gap使 freshness拒newsend。完整cut更新要求不能以長時間持DB transaction包住networkIO替代；DB鎖不控制遠端已接受order。

## 相反群組、同向batch與修單

首版REJECT_OPPOSING_GROUP_INTENTS，不internalmatch/netoff、不賣其他group庫存。同向cohesive plan仍使用每group獨立nativechildorder/attempt+reservation；沒有qualifiedpartialfillallocation的合單route拒絕。未來combinednativeorder須先固定AllocationPlanRevision、rounding、partialfillsequence、unassignedproof，不由callback临時比例猜。

任何repricing(包括同quantity較高limitprice)都需新的RiskDecision、MarketRule/資源增量檢查和C0→C1→C2類型的明示replace/adjustreservationreceipt。減quantity也須nativeprofile確定已成交量/剩餘與terminalrace。increasequantity/cancelreplace不可視為既有amend免費操作；未qualified回UNSUPPORTED/HOLD，不能釋放舊資源再盲send新單。

canonical terminal economics一旦SEALED，完整權威矛盾進INTEGRITY_CONFLICT，不append經濟變更；brokerterminal但canonical尚未接受是不同狀態。Incomplete evidence→RECONSTRUCTION_INCOMPLETE。保留bytes/出case/hold，沒有本候選發出的新correction或retry授權。

## 客觀反例與資格

正常自身reservation不讓合法order永久self-stale；其他group插入reservation要失效；T01包含無關政策delta拒絕；S earmark只能當ownresource一次；T12改quantity/price拒絕；同sourceFill重送no-op；externalFill不偽group；canonicalsealed lateFill conflict；acklost不resend；killbefore/afterinvoke保持unknownsafe處理。必須用two-connection/disposablePG＋brokerprotocolcrash fixtures取得RuntimeQualification，本文只有固定設計，`NOT_RUN`。
