# CYCLE03 有限設計世界回讀規則

來源 subject 為 `MA-ARCH-REVIEW-v7-CYCLE03`；wire 仍為 `MA-DTO-v6`。所有資料均為 `SOURCE_DESIGN_ONLY_SYNTHETIC_NOT_EXECUTED`。作者回讀檢查不等於 Reviewer PASS、真實 SQL／券商證據、Library 接受、Execution Grant 或 Runtime Authorization。

`CYCLE03_FINITE_OPERATION_WORLD.candidate.v7.json` 的 67 cases 是具體、逐 operation 的有限狀態場景。`state_before_ref`、`state_after_ref`、request、operation scope source、typed business result、response、read snapshot 都可回讀。共用 body catalog 是不可變修訂的資料庫式設計範例；其中的全部歷史／分支場景 body 不會自動成為任一場景的 current membership。GET 的 owner 狀態場景列出所查的有限集合；POST 的不同結果場景保留獨立的前後狀態。拒絕「看到 archive 內有某 body，便推定它是當前或任何查詢結果」的捷徑。

候選 staging 後，所有 `sources`、`model_schemas`、body value catalog 的相對路徑均以 `fixtures/finite_worlds/` 為根。作者 fragments 內回讀則以本資料夾為根。不得在 `fixtures/engineering-final/` 猜測新的 body 路徑。

依完整 ContractRef 的 `entity_id / revision_id / owner / hash_domain / source_hash` 比對 `reference_resolution_index`。此 index 只是導覽；驗證仍必須讀到正文：

1. `source`／`source_schema`：讀 `sources[label].relative_path`／`source_schema_path`，核對原始位元組、byte size、literal schema 與 inline body。
2. `body`：讀 body value catalog 的 `relative_path`，核對 canonical bytes、content hash、named model、schema 與 model semantic hash。來源雜湊和 typed body 雜湊分開處理。
3. `binding`、`capture`、`source_capture`、`artifact`、`source_artifact`：讀 world 內具體正文及 `auxiliary/<kind>/<label>.json`。capture／binding 的原始 input fields（不含自己的 `ref`）另存在對應的來源檔案，不是 opaque hash token。
4. `model_schema`：讀 `model_schemas[name]` 的確切 schema contract 與檔案，schema semantic hash 使用既有 `ma-body-schema-sha256-v1` domain。
5. `predecessor_*`：只依 `predecessor/BUILDER_OPERATION_WORLD.candidate.v6.json` 及固定 C2 model／type／body catalog 查閱原修訂。`CYCLE03_PREDECESSOR_28_ARCHIVE_MAP.json` 綁定完整原始文件的 raw hash 與 actual archive path；不可將舊 schema hash 套到更新後的 P3 文件。

Command 的 `OperationReceipt.result_ref` 指向具體 business body。schema 本身無 `ref` 欄位的 named body（例如 `RegistryProposalResultV5`）仍由 catalog `contract_ref` 及 `TypedBodyBindingV5.subject_ref` 綁定；不能只用 `payload.ref` 建立 resolver 而漏掉這些合法 body。

每個正例必須重算 request／response canonical hash、operation-selected response cardinality、business body hash 與 readback payload equality。不能將 error-only case、只宣稱 expected 的字串、泛用空 object、未回讀的 ref pool 或作者的 67 計數當成正例閉包。

原 28 組 C2 正例保留固定 wire profile、body/source/schema bytes 與 hash。若新 schema 只新增 optional selector，該相容範圍也須另行驗證；相容不能推導出新的 runtime qualification。

本世界保留 Library 的永久未模擬例外警告、ADMISSION_PENDING、NOT_SENT、未知 broker currentness、Recovery HOLD、未採納 simulation threshold、不可覆寫歸檔衝突，以及 PARTIAL_NOT_FULL_RESTORE_CAPABLE 備份。預期模型轉移成功不授予真實 Human approval、broker IO、SQL、Git publication、正式採納或 WORK dispatch。
