# Registry Export / Wire Adapter — candidate.4

本檔是 MA11/MA12 的候選編譯契約，Owner 沿用 Registry Writer／既有 WORK。歷史來源列、候選匯出資料與 API ContractRef 是不同格式；不得直接把 JSON 檔案列送進 closed API model。未正式採納的匯出檔仍是候選資料，不能成為 Formal Projection Head。

## 身份及欄位轉換

| 匯出列 | Wire／持久責任 | 拒絕條件 |
|---|---|---|
| assignment_id + revision_id | CodeAssignment.ref 的 permanent/revision ID，既有 ID 不變；新版內容採 successor revision | 同 revision 不同內容，或重送創新 ID |
| entity_id + entity_revision_id | CodeAssignment.entity_ref；在 snapshot identity/revision 閉包查證 kind、project、owner、hash | 目標缺失、scope 不符、hash 未驗證 |
| catalog_scope / namespace / code_type | source-scoped catalog key 經正式 catalog companion 解析；catalog identity 必在正式 registry 匯出閉包，不能用裸 C01 尋找 | context 缺失、跨來源誤合併、未採納 catalog |
| segments | 精確 CodeSegment：ordinal 為 0 起的連續順序；semantic_type、value_type、numeric_value/token_value、format_width | NUMBER/TOKEN 非互斥、負號／越界、width 不符 grammar、未知 segment type |
| format_policy | 指向採納後的不可變 CodePolicy revision；原始顯示、格式與可驗證 grammar 保留 | 以通用 split('-') 取代 grammar，或把 P8 自動改成 P08 |
| source_binding | 精確 Source ID／commit／blob／raw hash／行或 JSON pointer；來源 bytes 在審核包保全 | 有路徑無版本、hash 不符、行內容不符 |
| effective_snapshot | source-snapshot 的有效性；不是未知歷史生效時間的替代品 | 捏造 timestamp、把候選 snapshot 當已接受 snapshot |
| display / raw_text | 僅可衍生顯示／保留原始 LegacyAlias；source context 不可遺失 | display 成唯一身份或直接重新賦予歷史含義 |

候選 export 的 CodeAssignmentSourceRecord 以以上欄位為封閉檔案格式。正式 API CodeAssignment 的有效時相由 **CodeValidity** 表達：SOURCE_SNAPSHOT 分支綁精確 catalog/snapshot，TEMPORAL 分支另綁有效 interval；不能為匯入歷史 snapshot 虛構日期。正式 Source Registry/CodePolicy materialization 需採納契約、具相同永久 ID 的新增 companion；缺該閉包便停止正式 export/import，不能由匯入器臨時配置不同 ID。

LegacyAliasSourceRecord 保留 alias_id、revision_id、raw_text、context、target_entity_id/target_revision_id、source_binding 與原 interval label。wire LegacyAlias 的 source context 與 snapshot validity 分支不可省略；既有 Git/WO/Execution/Evidence string IDs 以 bridge 原樣保存，不要求替換。

## Dependency 與可重建資料

Registry relations 除雙樹、717 historical mappings、243 phase mappings 及 unit-feature mappings，亦包含 **267 DEPENDS_ON**：252 exact logical-unit plan dependencies、15 source-bound P phase dependencies。兩類 qualifier scope 分開，權重均為零。PHASE endpoint 明示合法；phase DAG 不自動授予 task execution。

Unit edge endpoint revision 必等 required_plan_revision_id，不取 latest；successor unit plan 必更新受影響 edge revision。新 dependency 不可只存 WORK 的裸別名或 UI 顯示欄位。完整 connected graph scope 必做 cycle/CAS 檢查；跨 scope 的新邊沒有 owner 契約時拒絕。

正式匯出閉包包含 permanent IDs、exact entity/relationship revisions、catalog/policy/validity、code/alias/source bridges、雙樹 roots、dependency/lineage/crosswalk、必要 contracts、原 acceptance source binding、私人 artifact availability。候選 Git Registry 檔是這個檔案契約的示範 subject；尚未 commit 或採納，不宣稱 Git-only runtime rebuild 已成功。

## 驗收與邊界

同 source C01 重送返回原身份；不同 catalog 的 C01 必兩身份；GAP-07-TIME-001 必為 GAP number 7／subdomain TIME／item number 1，寬度 2/3；AUTO-IMP-003 必為 work family IMP／package 3，不能誤當兩個數字。LAB 原 Wave 與新 Feature 同字串保留兩 catalog，不重解舊 Alias。

逐列 shape/kind/source/identity/segment、全閉包 FK、267 dependency endpoints、same-ID JSON roundtrip 為來源／模型檢查。正式 importer、跨語言 canonical bytes、實際 PostgreSQL transaction、SQL 清空後還原及發布 crash qualification 仍 NOT_RUN。

## Permanent allocation companion and typed relation conversion

`code_allocations`與`assignment_allocation_bindings`／`alias_allocation_bindings`為versioned companions；原source rows immutable。Allocation key不能包含format/width/effectiveinterval；retired state/tombstone不釋放。CodeAssignment及CodeAlias wire必須先resolveexactallocation並做target/keyequality，外部opaqueIDs原bridge照舊。

`relation_source_records`封閉shape在TYPE_VARIANTS。按record来源驗證原relationID/rev、endpointID/rev、kind/qualifier及SOURCE_SNAPSHOT/TEMPORAL branch；再以fixed新RegistrySnapshot membership查endpoint。SOURCE_SNAPSHOT不產生instant；TEMPORAL只接受真實sourceinterval。以prior-candidate filehash/JSONpointer标CANDIDATE_GENERATED，只表示原設計來源，不形成OwnerReceipt。SourceManifest-ref、snapshot-label捕捉與exact wire refs需由REGISTRY_SOURCE_BINDINGS閉包解析；無法解析則HOLD而非配置guessID。

Same relationID/rev內容不變時保留；新增endpoint planrevision/move/依賴更新由root successor relationrevision＋prior pointer承接，originalv3 rows保全。正式snapshot/wholegraphvalidation與GenerationCAS整批activation，samecommand不同hash拒绝。Root最终consolidation須refresh所有96plan endpointrefs／embeddedcatalogs/SourceManifest／relationrecords與snapshotsemantic digest後再freeze。
