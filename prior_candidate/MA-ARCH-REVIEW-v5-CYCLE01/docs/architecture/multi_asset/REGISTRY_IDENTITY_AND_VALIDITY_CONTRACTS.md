# RCG02 — Permanent Code Allocation／Versioned Relation Import Contract

Revision `candidate.4`；Original Registry／R05／Projection Importer 是唯一 Domain Owners。此 companion 是 MA11/MA12 的施工語義輸入，狀態 `FIXED_CANDIDATE_PENDING_INDEPENDENT_RE_REVIEW`，不是 Identity Freeze、正式 Git Registry 或 SQL 執行授權。

## 来源與最小相容修正

保留 MA-ARCH-REVIEW-v3 原927 code assignments／aliases、1630 relations、entity/revision IDs及LAB Wave來源。原 STEP3 L100/L153 的永久配置要求由 `CodeAllocation` 明確承接；原日期必填 RelationRevision 只在本候選 successor 改為 typed validity，原凍結v1/v2/v3及accepted schemas不改。檔案來源列、wire model、正式SQLprojection不是相同格式。

## Permanent semantic key／allocation／tombstone

唯一鍵是 `(immutable catalog ID, immutable entity kind, namespace, stable code family, canonical typed semantic segment vector)`。Segment鍵包含ordinal、semantic_type、value_type及其NUMBER值或TOKEN值；**不包含format policy ID/revision、width、separator、display、時段或entity revision**。NUMBER值以整數比對，不以`01`與`1`字串作兩個配置；TOKEN是grammar定義的精確token，不默默做case/Unicode轉換。grammar變更若改語義須新code family/catalog/source decision，不能借format更改釋放同鍵。

`CodeAllocation` permanent ID一次分配並保存；其 allocated_entity_id 永久不改。`CodeAssignment`只是此allocation的呈現／生效版次，須滿足相同semantic key與target。Original C01 across Capability Map／GAP08 correction catalogs是兩allocation；same catalog C01在E1退役後給E2即使不重疊也拒絕。Retirement新增`CodeAllocationRetirement`，projection為`RETIRED_RESERVED`；沒有unreserve/reassign API。Original spelling alias映射原allocation與exactsource target，所有歷史Code/Alias allocation都納正式Git閉包，tombstones無期限保留。格式新版同entity合法，split／merge新增entity但不得沿用舊entity code allocation；可新增new code或保留old code指已retired parent。

| Request | Result／receipt／權威 |
|---|---|
| 同semantic key／同entity／同command hash | 返回原allocation與receipt，不新增ID/weight/events |
| 同semantic key／同entity／新display policy | 新CodeAssignment revision，allocation不變，歷史alias不改 |
| 同semantic key／不同entity／不同時間或format | `CODE_PERMANENT_ALLOCATION_CONFLICT`，整批不啟用 |
| 不同catalog same C01 | 各自合法，裸alias查詢回`AMBIGUOUS_REFERENCE`或要求完整scope |
| 已retired code給new entity | `CODE_RETIRED_RESERVED`；不能因當下沒有activeassignment而通過 |
| 歷史raw data本身同scope矛盾 | `HISTORICAL_BINDING_CONFLICT` quarantine；沒有自動豁免；需原scope Owner證據，不重寫既有來源 |

## Typed source row → wire → projection

`REGISTRY_SOURCE_BINDINGS.candidate.v1.json`保存source_manifest raw bytes reference與source snapshot labels的明確捕捉界線。`MA_ARCH_CANDIDATE_1`等舊label只是原列metadata，不能推導已存在／已採納同名RegistrySnapshot或日期。`SourceSnapshotBinding` reference固定已捕捉原列所在manifest/file/pointer範圍；original registry snapshot未能證明時explicit null，capture coverage只對此source record set。

CodeAssignment原列保留；`assignment_allocation_bindings`把exact assignmentID/revision接到新permanent allocation。LegacyAlias原列保留；`alias_allocation_bindings`同樣接原allocation。Opaque WO／Execution／Evidence IDs經原scope legacy bridge保持；不強制重編碼。CodeValidity.SOURCE_SNAPSHOT以SourceSnapshotBinding供source closure，TEMPORAL則有真實來源interval與governing source snapshot。Alias query採`AliasResolutionSelector`，SOURCE_SNAPSHOT不要求instant，TEMPORAL才要求`at`。

原relation列保留，`relation_source_records`為versioned companion，帶recordID/revision、原relationID/revision、exact from/to revisions、typed qualifier、`RelationValidity`及source binding。未原有Owner來源的生成邊，source_ref指凍結v3檔案exact hash/JSON pointer，分類`CANDIDATE_GENERATED`，不能冒充Human receipt。原有source_binding額外原樣保留供source closure；adapter不得丟失717mapping/phase/unit/sourcecontext。

| Validity kind | 必需 | 禁止／邊界 |
|---|---|---|
| SOURCE_SNAPSHOT | governing RegistrySnapshot exact ref，兩端 `(snapshotID,entityID,revisionID)` membership；exact captured source binding | effective_interval非null、捏造from、偷取latestendpoint；source snapshot不授Acceptance |
| TEMPORAL | governing snapshot exact ref＋來源可證的半開`[from,to)`，to可null；真實source interval | 未知from用capture time替代；to≤from；缺endpoint revision |

Wire RelationRevision.effective_interval降為僅TEMPORAL的derived nullable projection，需與validity interval相等；SOURCE_SNAPSHOT為null。所有正式Tree/Dependency/Split/Merge/Move仍以accepted snapshot membership固定；新move/split/merge/endpointrevision需successor relationrevision與prior pointer，不能回寫historicalrecord。Source-record revision與relation revision是兩種revision，不因presentation adapter不同就否認原relation身份。

## Whole graph／CAS／replay

RegistryChangeSet／RegistryImportRequest固定所有connected ProductTree、EngineeringWBS、Dependency DAG、Lineage DAG與cross-project imported graph heads/generations/sourcehash。在同SQLtransaction驗allocation、FK、single-parent、整批新增/移除/有效時相與snapshot membership、complete cycle scope；只驗新增edge／單project subset不充分。Cross-project必要closure缺失→`UNKNOWN/HOLD`。Concurrent A→B、B→A只能一方提交；stale generation必須重讀全部cut再驗，不重用先前PASS。

ProjectionReceipt與snapshot/headCAS/event/outbox同transaction；已接受來源Git/Intake decision僅由既有Publisher/Importer承接，不新增AcceptanceEngine。Command key(scope,commandID) samehash返回原receipt；differenthash→`IDEMPOTENCY_CONTENT_CONFLICT`，不覆蓋receipt；相同relationID/revision不同canonical bytes→`IMMUTABLE_REVISION_CONFLICT`。Oldsnapshot可歷史保存但不能回退formalhead；newformalhead需verifiedGit＋exactadoptionreceipt＋ancestry/CAS。Changed graph完整檢核與semantic re-review reverse closure分開，未受影響歷史Acceptance不重寫。

## Git-only required closure／hash domains

Formal Git export必有 allocations/tombstones、Code/Alias source bindings、source snapshot captures、wire models/grammar/policy/source橋、entity/revision/snapshotmembers、兩樹/typededges/deps/lineage/weightuniverse/必要contracts。Importer不能空DB重配ID或把display当key。Private bytes不在Git時MISSING/UNVERIFIABLE，Evidence binding不產生新Acceptance。

Raw frozen file hash、Git blob ID、typed semantic snapshot digest是不同domain。Snapshot語義hash只含固定members的ID/revision/recordhash及source binding，不含自身ref/hash、derivedhead、lateprotection/reconciliationreceipt，也不遞迴hash展開whole graph。新增SourceWireBinding/SourceSnapshotBinding IDs一次保存，rootfinalmanifest須能解析每一ref；未閉合producer/context拒匯入。

## 客觀oracle／qualification

機器架構例子檢查：927 permanent keys無same-key-other-entity；same C01 differentcatalog合法；retirement→E2拒絕；formatwidth改仍衝突；GAP-07-TIME-001 typed7/TIME/1及AUTO-IMP-003 AUTO/IMP/3；1630 SOURCE_SNAPSHOT relation有效性與exactendpoint保留，不造instant；parentcycle/dependencycycle/CAS/replay/conflict/sameIDrebuild。Counterexample fixtures附具名預期。

此輪是SOURCE_REVIEW/AUTHOR_MODEL_SIMULATION；PostgreSQLFK/unique/Serializable/two-connection/importer/runtimecanonicalbytes/emptySQLrebuild/Crash未執行。Original frozen IDs/counts不等formal adoption，root整合之新snapshot/endpoint plan successors須再次全圖驗證及Fresh Independent Re-review。

原assignment.source_binding.sha256的hash domain未完整聲明，不能當整份原文件rawSHA。New CodeAllocation source_ref改為prior frozen CODE_ALIAS rawbytes＋assignment JSONpointer；legacy provenance另存原樣並標UNDECLARED，真正原doc來源由原SourceManifest各自驗證，不猜測linehash/rawhash。

Typed RelationQualifier保留scope_kind＋original source_scope_key；scope_ref解析固定ScopeContract，UNIT_PLAN_DEPENDENCY／P_PHASE_DEPENDENCY不能互當eligibility。ScopeContract payloadhash不含snapshot/head，RegistryGraphHead另pin exact snapshot/generation，避免snapshot↔relation↔scope hash環。重用既有ProjectionReceipt successor，不建立第二個Importer result owner；MA12-U05以RegistryImportRequest為完整typedinput。

ProjectionReceipt只承接成功APPLIED或REPLAY_NOOP；拒絕stale/conflict/invalid使用既有OperationReceipt／ValidationFailure，不生成假的appliedhead或成功receipt。legacy event_frontier為committed_frontiers canonical summary，base/applied_projection_ref對應relevant localgraphhead的derived projection，二者不成新真相。
