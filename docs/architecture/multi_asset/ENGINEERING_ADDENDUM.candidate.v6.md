# CYCLE02 工程契約修正候選 — candidate.6

本片段由 Architecture AUTHOR 產出，修正固定 CYCLE01 審查的 CC02／CC04／CC05 指定反例。所有 JSON patch 只供 Root 合入候選 V6；沒有建立 Compiler、Controller、AcceptanceEngine、進度 owner、HTTP operation 或永久 Unit ID。原 accepted P00 與 closed package／execution／claim／invocation／result schemas 不改。作者值檢核與模型案例均非實際施工、獨立審查或接受。

## 分析與修正選擇

READY 反例的問題是永久依賴身分不等，HOLD 反例的問題是完整輸入不可回讀。保留原 raw34；使用既有 WORK 的版本化 companion，讓兩個 outcome 分支都帶 `CompilationInputBindingV6`。不擴大 raw plan、不另建 compiler，也不以 true／名稱清單充當資格證據。

四個 consumer 依實際責任處理：MA11-U01 的 getRegistry 是 `DESIGN_CHECK_SOURCE`，只檢 exact source／schema／wire，不能反接 MA11-U03 造成循環或宣稱冷讀整合。MA12-U03 的 proposeRegistry、MA10-U02 的 getOperation／getGraphDraft 是 `IMPLEMENTATION_INTEGRATION`，分別要求 MA11-U04、MA12-U04、MA04-U02 的 exact qualified result／scoped reuse edge。缺 producer、錯永久 ID、舊 plan revision、profile／account／environment／cut 不適用，一律 HOLD。

MA10-U01、MA10-U05、MA15-U02 的 getArtifactContent 基數是 `ONE`。BODY 與 BINARY_DESCRIPTOR 是這個單一值的兩個互斥 typed variants；binary stream 仍由原 getArtifactBytes 供應，不改整個 API 的基數。

## Compiler 完整輸入與同世界案例

`CompilationInputBodyV6` 保存 lossless_plan、完整 CompilationContext 與 idempotency_key。external request_ref 不放進自身的 canonical hash bytes，避免 self-hash。`CompilationInputBindingV6.request_ref` 解得完整 body；context_ref 解得同一 body 中完全相等的 CompilationContext；input、context、dependency SHA256 分別重算。兩個 HOLD 即使同 plan，只要 writer generation、context、dependency 或 idempotency input 不同，其 immutable body／ref／digest 必不同。同 idempotency key 異完整 input digest 則 conflict；不得重播另一個輸入的 receipt。

`COMPILER_LITERAL_WORLD.candidate.v6.json` 是有限 synthetic source 世界。其 input 是逐 byte 複製的 CYCLE01 `EXECUTION_UNITS.json`，selector `#/units/78`，原永久 MA14-U01 與 34 欄完整保存。這個固定 literal 不指向本輪 fixture catalog，避免 fixture↔new plan 的 hash 循環。四個原 dependency 的永久 IDs、原 plan revisions、selected-body SHA、typed result／ReviewSubject 或 PublicationIntent output、qualification receipt、resource scope、source/schema/profile/cut applicability 全部列明並可解析。

此 historical raw plan 只供版本化 adapter 的模型輸入練習；compatibility receipt 明列限制。真正 candidate.6 executable compile 必須綁 fresh V6 successor plan/source/qualifications，不能沿用這組 historical 模擬接受。`MODEL_ONLY_QUALIFIED`／`MODEL_ONLY_PASS` 明確不是合法 WORK 資格，沒有 runtime execution／writer／invocation／dispatch allocation。

12 個完整 request→outcome 案例包括 exact4 READY、missing-grant writer4／writer5、missing dependency、wrong producer ID、stale plan、unqualified result、profile mismatch、unknown context、unknown quota、unqualified fallback、atomic grant consumed。每個 outcome 完整保存 immutable_inputs，沒有只有 `expected_ready=true` 的正例。原 131072-byte context gate、coverage UNKNOWN、source completeness與 OpenAPI 非 schema component 保護不縮減。

同規格可切換 CODEX 主執行／GPT+VSCode 或合格 LM 輔助，但先保存合法 source／diff／tests／STOP、關閉原 single writer，再依既有流程建立 fresh invocation。永久 Unit／Feature、plan、source、evidence 與接受權限不重置；額度或模型名稱不授權。

## 95 operations 的 transport profile

目前 outgoing canonical wire profile、`X-MA-DTO-Version` 與 ReadEnvelope.schema_version 均為 `MA-DTO-v6`。文件 source revision `candidate.6` 與 DTO profile 是不同維度；candidate.4／5／6 都不是 wire alias，收到這些 token 或未知 profile 回 422 SEMANTIC_VALIDATION_FAILED。Header／body／envelope mismatch 在效果之前拒絕。保留 95 個永久 operation IDs，不增 endpoint。

MA-DTO-v4／v5 只有在逐 operation 列明 exact frozen legacy schema_ref 與 named adapter 時才可 negotiated；否則拒絕。不能依 shape 猜版本、把 source 版號當 alias、或把 v6 欄位注入原 closed legacy bytes。Root 必保存 old source/schema 的唯讀版本並在 final catalog 填 exact refs；没有這個 adapter 的 legacy branch 就是拒絕。

TypedBodyBindingV5 的名稱保留，其目前 dto_version 同 canonical wire profile。Body Catalog schema revision、serializer profile、API/Unit/UI/wire fixtures 要依 Root 的 final V6 bytes 同步；canonical error protocol 仍為 `architecture.transport_error.v2`，不是 DTO profile。

## UI07 冷啟動與 PAPER 選取

既有 getDashboard 透過 `DashboardProjectionV6` 包裝原 DashboardProjection；只有帶 PaperCatalogQueryV6 才回 optional paper_catalog。這是 N_APPLICATION 對原 L_SAFETY SessionStore 與 DeploymentAdmissionStore 的 scoped projection adapter，不創新 truth owner。

Query 明列 account、PAPER environment、exact execution profile、CURRENT／ALL_HISTORY／HISTORICAL_SNAPSHOT、session／deployment states、read snapshot、cursor、limit。historical 必有 exact snapshot；空 state filter 表示此授權 scope 的所有原 state，不能推成未篩選跨帳戶資料。第一次讀取釘住兩個 owner cuts 與 permission epoch。排序是 kind／entity／revision；continuation cursor 綁整組 filter digest、兩個 cut 的 read snapshot、schema、profile 與 permission epoch。filter digest 排除 cursor/read_snapshot_ref 兩個 continuation pin，其餘欄位全部參與。任一變更回 canonical 409 read conflict／RESNAPSHOT。

Page 提供 exact Session／Deployment entries、owning_store source receipts、snapshot、coverage、cursor。只有兩個 original stores 都 COMPLETE，且各有 exact-query positive empty proof，才可宣稱完整空集合；UNKNOWN／PARTIAL／權限拒絕不是 absence 或 FLAT。UI 使用伺服器回傳 exact refs，再讀原 getSimulation；前端不得猜 ref、從 browser cache 恢復 command subject 或從選單存在性推 readiness。start/resume 仍需 fresh 原 lawful gate。

getSimulation／pauseSimulation／resumeSimulation 路徑 id 必等 session_ref.entity_id；replaySimulation 路徑 id 必等 source_session_ref.entity_id。無路徑 alias 或優先權；UUID canonical parse 後 unequal 以 422 拒絕，命令 NO_EFFECT_PROVEN、讀取 NOT_APPLICABLE，不能對任一衝突 target 操作。

## Error 與正文同步

BODY_CAPTURE_READBACK_CONTRACTS 的 current outgoing paragraph 只使用七個 v2 canonical codes。舊 RESOURCE_DENIED／RESOURCE_OR_REVISION_MISSING／CAS_OR_HASH_OR_CURSOR_CONFLICT／DEPENDENCY_OR_OUTCOME_UNKNOWN 只能是 exact incoming legacy table version 的 alias；不得輸出成 v2。unknown code/version 不盲重送。

原 retry table 保持 code owner；增加明示 read validation/denial 的 NOT_APPLICABLE branches，區別命令 pre-invocation NO_EFFECT_PROVEN。Read snapshot conflict 回 RESNAPSHOT；命令可能已提交時保留 QUERY_RECEIPT、effect UNKNOWN／EFFECT_COMMITTED，不能用 status 猜效果。

## 替代方案、风险與建議

新增 session/deployment endpoints 會改永久 operation 集；此輪以既有 getDashboard 的 versioned typed projection 完成發現來源。讓 MA11-U01 依賴 runtime registry reader 會產 inverse cycle；以 source check 保留責任，真正 consumer 加 exact producer edges。只保存 unit_plan_ref 不能辨識 writer/context 差異；完整 immutable request/context 解決 provenance。

Root 合併 Registry 與此片段後，必重新產 schema/body catalog、successor plan revisions、dependency exact revision IDs、interface/IO/test consumers及 final raw/canonical hashes。不能把作者片段中的 historical v5 literal 說成 current V6 acceptance。應用本片段後仍須 fresh independent review；Compiler/P00/R01/SQL/Broker/PAPER/Controller/release qualification 均維持 NOT_RUN_NOT_QUALIFIED。

## References

- CYCLE01 fresh-review/units RESULT：CYCLE01-CC04-COMPILER-01、CC04-DEPS-02、CC05-VERSION-04、CC02-CARDINALITY-05。
- CYCLE01 fresh-review/product RESULT：PRODUCT-V5-PAPER-COLD-02、PAPER-WIRE-01、BODY-ERROR-03。
- 固定 consolidated REVIEW_OUTPUT_MANIFEST SHA256：a1cebe3286fa526cb949fd9553dadf43b7567c5ecb7e5c79329289392782b078。
- fragment.json、FROZEN_CONTRACTS.json、COMPILER_LITERAL_WORLD.candidate.v6.json、PAPER_COLD_LITERAL_WORLD.candidate.v6.json、ENGINEERING_BODY_VALUE_CATALOG.candidate.v6.json。
