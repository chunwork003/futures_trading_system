# V1 Domain Contracts — P00 Candidate

Status: `FROZEN_CANDIDATE / NOT_ACCEPTED`。共通語意由 `V1_BASELINE.md` 定義；既有 accepted canonical contracts 優先，不重新定義相同 class。
下列「新增」是 schema/spec，不代表 source 已實作。wire DTO 與 API schema owner 為 scripts/p00_build_contracts.py；generated OpenAPI 位於 contracts/，語意 owner 為 V1_API_ARCHITECTURE.md。

## Contract envelope

新增 durable record 必有 `schema_version`、opaque stable identity、owner、created/recorded UTC instant、correlation_id；需要因果鏈時有 causation_id。
Append-only evidence immutable；mutable head 必有 integer revision CAS；revision 從1開始，update expected_revision 不符回 CONFLICT，不 silent retry overwrite。
Idempotency key scope=(authenticated actor, command kind, resource identity)。Request fingerprint使用validated canonical payload，不含server timestamps；same key不同payload拒絕。V1不得按時間自動刪除command idempotency receipts。
Unknown != empty/zero/FLAT；nullable 欄位若表示未知必須同時有 reason_code。Identity缺失、來源衝突拒絕；無合法外部觀測則 REVIEW/UNKNOWN，不假造observation。
新fields additive只有在舊consumer可安全忽略且不影響authority時相容；改economic含義必升schema版本和consumer compatibility gate。

## Data / strategy contracts

| Contract | Required identity / material fields | Owner / persistence / recovery |
|---|---|---|
| DatasetManifest | dataset_id, dataset_version, schema_version, canonical_content_hash, source_manifest_hash, calendar_version, contract_mapping_version, quality_policy_version, partitions[{relative_path,byte_hash,row_count,range}], coverage, accepted_quality_report | data owner；immutable file+research index；missing/hash mismatch拒絕載入 |
| DatasetVersion | dataset_id + version_id；semantic_hash、parent_version_id(optional)、correction_reason；ingested_at僅audit | data owner；新版本不覆寫舊run；同canonical內容再匯入返回原version |
| MarketBar | 既有 MarketObservationIdentity/Content/RevisionId 為 canonical owner；research Bar/MarketBar只是適配representation | domain/market_observation.py；operational path使用accepted revision，float只可研究consumer |
| ContractIdentity | existing instrument_id/contract_id、listed expiry/reference revision | domain/contracts.py；不得以TXF alias／broker native code替代 |
| ContractMapping | mapping_id/version, source_namespace/code, canonical contract identity, effective interval, provenance_ref | domain broker mapping owner；無匹配/多匹配拒絕；不可按symbol前綴猜測 |
| StrategyDefinition | existing registry strategy_id、implementation_revision、config schema/factory ref | strategy/registry.py；由code/registry版本resolve；不是UI自由輸入class名稱 |
| StrategyVersion | strategy_id + implementation_revision + code artifact hash | E owner；immutable；recovery不得載入不相容implementation |
| StrategyInstance | existing StrategyInstance完整欄位與instrument_binding_provenance | strategy/instance.py；existing repository；與config_version、policy_version分開 |
| StrategyConfigVersion | strategy_id、config_version、canonical_config_json/fingerprint、schema_version | E owner；immutable；禁止持倉silent mutation，使用accepted governing transition |
| IncrementalState | instance_id、state_schema_version、feature_version、observation_revision_frontier、warmup_status、state_blob_hash | E owner；K repository；只在safe checkpoint durable，history correction要求重建 |
| Signal | signal_id、instance_id、observation_revision_id、config_version、intent、direction、requested_quantity、evidence_refs | E output/G input；immutable；不含broker side effect；重複identity異material拒絕 |

Dataset canonical content hash：排序key=(instrument_id,contract_id,timeframe,bar_open_utc)，欄位順序按schema固定，decimal/time按domain lexical；逐record用length-prefixed UTF-8 framing形成SHA256。Storage byte hash獨立存在，Parquet壓縮器版本改變不應自動改economic dataset identity。
重複同key同material可dedup並保留count報告；同key不同material不能依檔案順序選winner，需explicit correction/source-priority policy形成新version。
QualityReport須列required/observed intervals、missing/duplicate/conflict/out-of-session counts；COMPLETE不能從row_count>0推導。無calendar coverage時UNQUALIFIED。

## Decision / execution contracts

| Contract | Required identity / material fields | Owner / persistence / recovery |
|---|---|---|
| Decision | decision_id、account、cohort/policy_version、input signal IDs、observation frontier、governing refs、proposed_target、approved_target、attribution、reason | trading decision；append-only trading decision table；同input identity retry不產生新economic intent |
| RiskDecision | risk_decision_id、decision_id、account_revision、capital_revision、margin/reference version、constraints/input refs、ALLOW/REDUCE/REJECT、approved_quantity、reason_codes | trading risk；append-only；execution必須引用有效且適用current input的risk result |
| CapitalState | capital_id、account/session、revision、currency、initial_manual_capital、realized_pnl、unrealized_pnl、fees、reserved_margin、available_capital、source refs | capital owner；revision snapshot，fills/mark refs可追溯；不接受UI直接改餘額 |
| OrderIntent | existing OrderIntent + PositionEffect validation（OPEN/REDUCE/CLOSE） | trading/execution.py；保持accepted authority，不自行擴enum |
| Order | existing canonical Order projection；order_id、broker_client_order_ref immutable binding | accepted event/fill-derived repository；不是自身economic truth來源 |
| Fill | existing Fill全部material fields；immutable fill_id/event_id/order_id | trading/execution.py + persistence/execution.py；duplicate identity exact comparison |
| Position | 明確wire discriminated union TARGET/EXPECTED/ACTUAL；不可引入無kind的第四套Position SOR | respective G/J/provider owner；DTO只能projection |
| ExpectedPosition | existing AccountPosition、account revision、snapshot/commit refs | accepted account authority；Fill/Event closure推導 |
| ActualPositionObservation | existing BrokerPositionObservation及items、provider/environment/account/scope/observed_at/completeness refs | provider factual authority；simulation也必獨立產生；不能copy expected |
| ReconciliationCase | existing case_id/version/state/policy/evidence/resolution | J owner/C13 repo；RESOLVED不自行令accountREADY，不重寫經濟狀態 |

Operational Decimal計算中intermediate不做implicit rounding；order price按contract tick驗證，費用與settlement rounding由versioned cost/currency policy明列。Reference/margin缺失fail closed，不能fallback為0；historical explicit no-margin scenario僅research mode適用。
CapitalState採simulated account genesis與單一currency TWD第一個驗收場景；FX、多幣別、資金借貸是V2，不在V1 silently approximate。

## Research / application contracts

| Contract | Required fields | Identity / persistence / failure |
|---|---|---|
| SimulationSession | session_id、mode=SIMULATED、synthetic_account、revision、dataset_version、scenario_version/hash、seed、clock_checkpoint、governing refs、state、initial_capital | Python simulation owner；trading session tables；restart用existing recovery；fresh session不接續未證明的舊account |
| ResearchRun | run_id、operation_id、research_kind、dataset_version、strategy/config refs、policy/cost refs、code_sha、lock_hash、seed、input_fingerprint、created_by | Python research owner；immutable intent；state由operation reference投影 |
| Operation | operation_id、kind、resource_id、state、revision、request_fingerprint、idempotency_scope/key、current_attempt_id、created_at/updated_at、result_manifest_ids、error | Python job owner；research operations；terminal immutable，retry建立attempt而非改runinputs |
| OperationAttempt | attempt_id、operation_id、attempt_no、worker_id、lease_generation、state、started_at/finished_at、checkpoint_ref、failure_code | job owner；attempt_no unique per operation；stale holder不能publish |
| WorkerLease | operation_id、holder_id、generation、expires_at、heartbeat_at | job owner；DB time授予lease，generation CAS；過期只允許重新claim，不證明舊process停止 |
| ArtifactManifest | artifact_id、version、media_type、schema_version、relative_uri、byte_hash、semantic_hash(optional)、size_bytes、producer_run/attempt、created_at | Python artifact owner；immutable；absolute/local traversal/URL任意fetch禁止；只有published references可下載 |
| AuditEvent | audit_id、producer、actor_ref、action、resource_ref、occurred_at/recorded_at、correlation/causation、outcome、reason、redacted_context | producer owner；append-only各自schema；沒有全域timestamp因果假設；secrets禁止進payload |

## Command / result behavior

Research kinds：BACKTEST、PARAMETER_STUDY、OOS、WFO、MONTE_CARLO；comparison引用既有published artifacts，不隱式重跑。
Workload limits由versioned serverconfig宣告(max bars/trials/concurrentjobs/artifactbytes)；超額422 WORKLOAD_LIMIT_EXCEEDED，不能由caller要求無界運算。有限預設值 owner 為 contracts/workload_policy.v1.json；缺失拒絕startup。
Result pages使用opaque cursor，cursor綁run_id、artifact_hash、sort/filter；limit default100/max1000；錯cursor400，舊artifact409。Decimal欄位字符串；non-finite research metrics null+reason。
API error分類：INVALID_INPUT、UNAUTHENTICATED、FORBIDDEN、NOT_FOUND、REVISION_CONFLICT、IDEMPOTENCY_CONFLICT、UNQUALIFIED_DATA、READINESS_BLOCKED、WORKLOAD_LIMIT_EXCEEDED、DEPENDENCY_UNAVAILABLE、INTERNAL_ERROR。對外不暴露stack/native SDK/secrets。
Transport timeout != domain failure；查operation/command receipt。不能把clientdisconnect變成已接受cancel。

## Compatibility acceptance

每個新增contract必須有valid example、unknown/missing identity、same-id/different-payload、version incompatibility、recovery/ref失效反例。
Accepted existingmodel使用reference，不複製改名重寫。新DTO不改既有constructor語意；新consumer以adapter+golden equivalence測試逐步遷移。
