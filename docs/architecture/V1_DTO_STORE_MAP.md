# DTO → domain → store 對照 — P00 candidate

Status: `CANDIDATE_NOT_ACCEPTED`。機器對照表 `contracts/dto_store_map.v1.json` 逐一涵蓋 Python/BFF 共用 component schemas；schema content fingerprint 防止新增／變更 DTO 後仍把舊對照當完整。這是設計 coverage，尚未實作 adapter。

## 責任與 mapping

每個 schema 指向唯一 mapping group。VALUE／COMMAND／PROJECTION 不直接建立另一份 writable domain truth；IMMUTABLE／MUTABLE／ENVELOPE 指定唯一 semantic owner、storage owner、key、transaction、restore 與 rejection 規則。Nested value 的儲存依 containing owner，不按型別名稱建立泛用 table。新 Signal／Decision／RiskDecision／CapitalState／IncrementalState／envelope 的全部 fields 另列 `new_record_field_sources`，明示 server identity、owning source／calculation 與跨 reference closure；來源文字仍須獨立語意審查，不能把完整欄位數當成 conformance。

| Family | DTO → authority / store | Adapter 必驗證 |
|---|---|---|
| Dataset/version/reference | P01 data owner → immutable manifests + research metadata；reference snapshots 保存 provenance | canonical hash framing、scope/count arithmetic、CSV/calendar/mapping qualification、publication fence，拒絕未知 coverage |
| Strategy/config | E → existing StrategyInstance/state stores + proposed immutable config/artifact registration | string implementation_revision 不假裝 SHA；exact code artifact/config/provenance；持倉 transition 依 accepted C17 |
| Research/job/artifact | research service → research operations/attempts/leases + published artifact manifests | actor/request fingerprint、worker generation、cancel/terminal races、file/database publication closure |
| Simulation | session owner → proposed session/control/currentness records；existing canonical account/OMS | session_id 與 broker/account_ref 明示映射；seed/clock/scenario；restart 不 auto RUNNING |
| Positions/account/reconciliation | API projection → existing respective account/provider/case owners | TARGET/EXPECTED/ACTUAL 分離；UNKNOWN 不製造 empty/FLAT；case resolution 不修復經濟狀態或授予 READY |
| Signal/incremental | E → proposed immutable signals/qualifications + existing StrategyStateSnapshot | exact snapshot/config/observation/codec + output receipt；無 prior virtual state拒絕；HOLD 不省略 required member |
| Decision/risk/capital | G → proposed append-only decisions/risk/capital；selector 只屬 non-economic currentness | cohort closure、staged reversal、REJECT 不等於 flat、Decimal/source arithmetic、complete input cut |
| Auth/UI/status/audit | ASP.NET identity/session owner／producer-owned audit／read-only query | 不接受 browser 權威；Python internal identity 與 cookie 分離；no secrets，missing dependency 保留 reason |

Signal、Decision、RiskDecision、CapitalState、IncrementalState 僅由 TradingEvidenceEnvelope 包覆；envelope 的 evidence_id 必須等於 record identity（qualification 則為其新 immutable ID），owner 分別 E/G/G/G/E。payload_hash 必須按 V1_INCREMENTAL_PERSISTENCE 的 canonical normalization 計算；server recorded_at 不可由 caller 覆蓋。Outer evidence fields 不可抹掉 underlying canonical provenance。

Expected/actual positions 不從泛用 Position JSON 直接寫回 account/provider store。OrderIntent/Order/Fill 目前没有新 wire schema，必須沿用 accepted canonical constructor／repository／UoW，並額外檢查 V1 operational references；source_bindings 保留這些沒有 HTTP DTO 的重要 owner。AccountState.readiness 是 evaluation projection，禁止 PUT 欄位覆寫 readiness。

## New-record identity / closure

| Record | Stable identity / typed unique key | Reference closure / restore |
|---|---|---|
| Signal | signal_id；instance/config/strategy_version/contract/observation | same key 同 material 回原 immutable evidence；prior virtual state、snapshot、canonical observation、current governing context；snapshot/output receipt/signal 原子寫入 |
| Incremental qualification | qualification evidence_id；snapshot_id/codec/config/frontier | 原 state 仍在 StrategyStateSnapshot；codec hex exact roundtrip、warmup/count/frontier、state_blob_hash；missing snapshot 拒絕 |
| Decision | decision_id；account/contract/policy/cohort manifest/observation/expected revision/input-cut hash | complete required signals；selected/excluded attribution closure；sum selected = desired；opposite target stage EXIT=0；沒有 risk approval field |
| RiskDecision | risk_decision_id；decision_id/capital identity/policy/margin/input-cut hash | account/contract 與 decision/capital source 同世界；ALLOW=proposed；REDUCE 依 reduction policy；REJECT=null；execution 另重驗 current cut |
| CapitalState | capital_id；account checkpoint/mark/calculation/margin policy | initial + realized + unrealized - fees - reserved；fees/reserved非負；source=MANUAL 是 genesis provenance，並非所有值來自手填；revision 不取代完整 source identity |

例如兩個不同 mark 可對應同 account_revision；不能用 (account,account_revision) 作 CapitalState 唯一 key。Strategy/config/observation 亦不能只以 timestamp 取最新值。Envelope ID equality、引用可解析與跨欄位 arithmetics 是 adapter duties，JSON Schema shape 並不證明。

## Delivery / review gates

P01/P02 既有 contracts/fixtures 保持不變。P03 實作 research/application durable adapters；P05 提供 strategy/output 純計算與 conformance；P06 提供 decision/risk/capital 純計算與 conformance；P07 提供 simulation OMS/provider bridge；P08 整合交易 stores、composite currentness 與實際 PG/crash evidence。任何 pre-P08 memory test host 的結果不可標 durable trading integration。

Machine coverage 檢查全部 schemas 均有 mapping、mapping fingerprint 與確切 source/class/blob 對得上；缺 field source 或 public semantic 決定的 package 仍 PACKAGE_NOT_READY。獨立審查與正式 adapter conformance 是另兩道 gate，作者自查不計 ACCEPTED。風險集中在引用閉包、同 revision currentness、writer coverage 與實際原子性；見 V1_DECISION_RECOVERY_CUT.md。
