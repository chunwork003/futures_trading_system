# Logical Schema Contract — candidate.4

本文件補足 MA11–13 的可施工約束；只定義 Schema 規格，不包含 DDL、不授權 Migration。唯一 Registry／經濟資料／WORK Owners 沿用原契約。MODEL_CATALOG 是 wire/logical model，不能機械式逐 model 建一張表。

## 共用身份、版本、Hash 與寫入

永久 ID、revision ID 為一次分配且保存的 UUID；legacy integer/string ID 經 scope-qualified bridge 保留。Entity head 可變，revision payload、relation endpoint、snapshot membership、receipt/event 不可變。未採納 candidate bridge 不宣稱已是正式 historical ID。引用檢查包含 project/catalog/kind/revision/owner，不只 UUID 存在。

Hash domains：`raw-bytes-sha256-v1` 是完整原始 bytes；`git-blob-sha1` 是 Git object identity，不能代替前者。`ma-canonical-json-sha256-v1` 限定 UTF-8、LF、無 BOM；object keys 依 Unicode code point 排序，無多餘空白；禁止 duplicate keys、NaN/Infinity、float money、未知欄位。UUID 小寫、hash 小寫 hex、UTC instant 固定 ISO8601 `Z`；decimal 是字串、零不得負號、移除非必要尾零，unit/currency 必須保留。數字只允許安全範圍整數；大整數用明示 typed string。非 ASCII 字元原樣 UTF-8，不做 Unicode normalization 或翻譯原文。Order-sensitive arrays 保序；snapshot membership 等集合依 type＋ID＋revision 排序並拒重複。Hash input 為 `domain + '\n' + canonical payload bytes`；hash 與 witness 不納入自身 payload。實作必提供 golden byte fixtures 與跨 Python/.NET/TS 一致測試，不能讓各端選自己的 serializer。

## 最小持久模型與約束

| Family | PK／FK／Unique／Check | Writer／交易與 Index |
|---|---|---|
| entity / entity_revision | permanent PK；revision FK entity/prior；unique(entity, revision token)；prior 必同 entity；kind/project owner 不原地變 | Registry scoped writer；entity+recorded frontier；immutable payload hash |
| catalog / code_policy / code_assignment / code_segment | policy immutable；segment ordinal unique；grammar/value type/number range/width；CodeAllocation permanent(catalogID/entitykind/namespace/family/semanticvector) unique永不改target；CodeAssignment同allocation呈現effectiveinterval不重疊，不釋放永久key | assignment 與所有 segments 同 transaction；索引 catalog/type/normalized vector；raw string 只是 display |
| legacy_alias / identity_bridge | exact source context/raw code/CodeValidity/source snapshot/target revision/原allocation；bridge(scope,legacy_id) unique；不能 global bare C01 unique | append revision；歧義返回候選列表，絕不 first match |
| relation / relation_revision | relation identity 與 endpoint revisions FK；typed kinds；snapshot membership exact endpoints；RelationValidity SOURCE_SNAPSHOT無日期、TEMPORAL source interval；同logical edge/qualifier的active temporal intervals不重疊 | same graph-scope generation CAS／serializable transaction；索引 type/from/to/effective snapshot |
| snapshot / snapshot_member | snapshot ID/hash immutable；member(scope,snapshot,entity/relation ID) unique；closure 必完整 | staging validate→單 transaction activate head；relationship 和 endpoint revisions 必在 closure |
| draft_head / formal_projection_head | key(scope,entity/tree)；generation monotonic；head FK revision；Draft 與 Applied Formal 分開 | update where generation=expected；0 affected rows=CONFLICT；不能改 accepted flag 授權 |
| command_receipt / audit_event / outbox | unique(scope,command_id)＋payload hash；event identity/stream causal frontier；outbox FK receipt | mutation+receipt+audit+outbox 同 transaction；duplicate same hash 返回原 receipt，不再 event；異 hash拒絕 |
| artifact_revision / availability / protection_receipt | immutable content ID/revision/hash/size/media/class；locator opaque；capture 與 A/B protected receipt 分離 | bytes durable verified 後才能 SQL 引用；availability 不是 Acceptance；refs/hash/privacy 索引 |
| review_subject / publication_intent / projection_receipt | base snapshot、exact changes、relevant closure、review/adoption refs、Git source/outcome、applied generation | 既有 Intake/Publisher/Importer scoped writers；Git 與 SQL 無分散式原子提交假設 |
| engineering task / unit / result reference | 原 WORK IDs/contract refs 保留；unit scope、dependency、result/acceptance typed；weight universe／allocation version | WORK 單一 owner；SQL 只管理 Draft、歷程及投影；progresscredit不由 mapping edges 增加 |
| research definition / graph / snapshot / run | immutable graph/code/features/dataset/config/toolchain refs；run attempt/cancel sequence | F Research owner；results bytes先 capture；index strategy/branch/snapshot/run time |
| group / budget / origin / reservation companion | group 固定 financial account/env；origin binding immutable；reservation FK intent/account/cut/fence | J/G accepted account UoW；account-scoped serialization；切 executor 或改 budget 不改 fill origin |
| ledger / economic event companion | source economic identity+revision unique；journal per-currency balance；fill ID bridge immutable | 既有 accepted J/K economic writer；不可另建 SQL direct writer；projection可重建 |

3NF 核心身份、代碼片段、FK、關聯版本、來源與貨幣不可藏成單 blob。可用 schema-validated JSONB 保存 kind-specific terms、graph configuration、policies；JSON schema revision 是必需 FK/reference，查詢可用 generated projection/index，原 bytes/revisions 不改。Current projection 是 derived cache，存 producer/source head，不是第二 truth。

## Concurrency、Graph 與異常

兩筆 transaction 各新增 A→B、B→A，逐筆本地檢查都可過；因此只用 FK 或逐 edge CAS 不足。Product tree、Work tree、Dependency DAG、Lineage DAG 的所有新增/移除/有效時相組合，要在相應完整 graph scope 的同 generation CAS 下驗證並提交。跨 project 依賴要取得完整已導入 closure＋其 head generation；缺外部 closure 為 UNKNOWN/HOLD，不能只檢 project 子圖。DB serializable retry 必重讀 cut、驗整批，不重用舊成功判斷。批次禁止 partial activation。

Root 需在 snapshot 明列，child 最多一 parent；關聯多父用 mapping，非第二 parent。Move 建 successor relation；split/merge 新 target IDs、lineage 保舊；不刪 historical aliases/revisions。Accepted snapshot membership 永遠不原地覆寫。

## Long-term 與重建

Audit/receipt 依 source stream/time 可 partition；全局冪等 key 不因 partition/drop 而消失，retention 必保最小 receipt/tombstone 或受控 replay floor。Hash索引不可唯一替代內容驗證。Recursive query visited set＋資源限額，達限制返回 INCOMPLETE。大量 Artifact bytes 放 Store、SQL 只 refs，舊受保留集合不能 GC。

Git registry export 保存 permanent IDs/revisions、scoped code/grammar/alias、exact dual-tree/mapping/dependency/lineage、roots、sources/contracts、availability requirements、Acceptance 原 receipt binding及資格層級。Import 在 isolated staging驗完整 closure→same-ID upsert→CAS activate→durable reconciliation receipt。缺私人 bytes 留 MISSING，不複製 Acceptance。清空 SQL 後可從 export 重建正式投影，不恢復從未發布的 Draft 或不可再生私人歷史。

驗收：FK/kind/unique/interval/dag/CAS/idempotency/wholebatch原子性、Python/.NET/TS canonical bytes、same-ID rebuild、受保留歷史查詢、兩連線write-skew/crash。前者規格／模型檢查；實際 PostgreSQL/DDL/restore 仍 `NOT_RUN`，需合法 disposable qualification Work Order。

## RCG02 / RCG05 successor invariants

永久CodeAllocation／CodeAllocationRetirement為最小normalized allocation+event責任；unique semantickey不含format/time。FK allocation→permanent entity，CodeAssignment/Alias→allocation，retirement不cascade delete或開放reuse。snapshot/temporalvalidity discriminator與endpoint compositeFK在candidate模型明確；原已closed schema必須versionedadapter，不直接覆寫。

OwnerInventorySnapshot／ExternalCaptureJournalCut是外部privatebackup權威，不是另一SQLAcceptanceOwner。BackupInventoryClosure／BackupCoordinationReceipt與SQLBackupCut分別固定inventory/journal/SQL causalcut，FullPrivate requiredcoverage為三者union。SQL未index並非bytes缺失；未index verifiedbytes仍必required；missing/mutable原文必PARTIAL。Externalcatalog保存可於無SQL/無A恢復的objects/bootstrap/keys安全handles，不把secrets進SQL/Git。
