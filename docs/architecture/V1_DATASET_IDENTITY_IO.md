# P01 Dataset Identity / CSV / Reference Port — 候選契約

狀態：DEFINED_CANDIDATE / NOT_ACCEPTED。單一語意 owner：B data。P01 只處理 caller 提供的 bytes 與 immutable reference snapshot；不連 broker、DB、不讀寫既有 data/。以下都是候選規格與離線驗證，不是產品 importer。

## Hash framing v1

所有 digest 使用 SHA-256 lowercase hex。`F(tag, values)` 定義為 ASCII tag + LF，依序串接每個字串 `v` 的 `ASCII(UTF8_byte_length(v)) + ':' + UTF8(v) + LF`；長度十進位不加前導零，空字串為 `0:` 後接 LF。禁止 BOM、CRLF、JSON whitespace、Python repr 或 locale 介入 frame。字串不做隱式 Unicode normalization；opaque identity 不擅自改寫。

Canonical key K 的四個欄位順序：instrument_id、contract_id（真正正整數十進位）、timeframe（1m）、bar_open_utc。時間統一沿用 accepted MarketObservationLogicalKey.interval_start_at_lexical（六位 microseconds、UTC Z）；CSV 與 coverage 的整分鐘 wire 先轉此 lexical。按 instrument_id 整數、contract_id 整數、timeframe UTF-8 bytes、UTC instant 升序排序，不按字串排序數字。Listed contract 不容許 null。

逐列使用既有 domain/market_observation.py 的 canonicalize_market_observation_content 與 build_market_observation_revision_id；保留 OHLCV、amount/trade_count/tick_count、calendar trade_date/session_ref 的既有規則，不重寫 mor1 演算法。`bar_open_utc` 是 interval_start_at 的 wire alias，不是另一套 identity。

* key-set digest：`F('dataset-keys-v1', [unique_key_count, *flatten(sorted unique K)])`。
* content digest：`F('dataset-content-v1', [unique_row_count, *flatten(K + [mor1_revision_id] for each sorted row)])`。
* version digest：`F('dataset-version-v1', [dataset_id, content_digest, expected_keys_digest, coverage_start, coverage_end, '1m', contract_count, *flatten(sorted (instrument_id,contract_id)), *calendar_ref, *mapping_ref, *quality_policy_ref, parent_version_id_or_empty])`。每個 reference 展開順序固定為 owner、identity、version、sha256，coverage time 同樣正規化六位 microseconds。version_id = `dv1_` + digest。DatasetVersion.semantic_hash 為此 version digest；DatasetManifest.canonical_content_hash 為 content digest，兩者不得混用。

完全相同 key/revision 去重；同 key 多 revision 拒絕，不使用輸入順序選 winner。合法 empty key-set 可用於 missing-set 診斷，但 qualified dataset 不可為空。Root parent 使用空字串；wire null 先明確轉空字串，literal 'null' 不是空值。Parent lineage、coverage、reference 任一改變，version 必須改變。Correction reason、source bytes/hash、ingested_at、duplicate counts 不進 semantic version frame，保存在每次 import metadata/receipt。

`contracts/dataset_identity.fixture.v1.json` 是 literal frame/hash vectors；以既有 canonical model 產生 mor1，再由測試依上列 framing 獨立組裝、對照保存的 frame bytes 與 digest。Fixture 不是 production truth 或 review acceptance。

## CSV_V1

UTF-8 strict；僅檔案最前方容許一個 BOM。RFC4180 逗號／雙引號、LF 或 CRLF，拒絕 NUL、重複 header、額外／缺少欄位及空資料列。固定十欄順序：

`source_code,bar_open_utc,open,high,low,close,volume,amount,trade_count,tick_count`

source_code 為不可空、不含前後空白的 opaque mapping key；source_name 為 mapping namespace，必須與 mapping snapshot 一致。時間只接受整分鐘 `YYYY-MM-DDTHH:MM:00Z`，真實 Gregorian 驗證；不猜本機時區。OHLC 與非空 amount 必須符合現有 Decimal wire lexical，禁止 exponent/NaN/Infinity/float。volume 必填非負十進位整數；amount/trade_count/tick_count 空字串代表 null，count 非空則非負整數。trade_date/session_ref 不由 CSV 提供，必須從 pinned calendar snapshot 取得。

P01 input 為 bytes stream（最多256 MiB；超額提前拒絕），不可傳入 URL／任意檔案路徑；呼叫端提供 staging/output root。實作可 streaming，但結果不得受 chunk size 或列順序影響。壓縮、ZIP、delimiter sniffing、連續合約推估不在 CSV_V1。

## ReferenceSnapshotPort 候選介面

Port 放在未來 storage/dataset_contracts.py，implementation adapter 放在同一 P01 已列 allowlist 的 dataset_import.py。不改既有 calendar/repository classes。

| 方法 | 明確輸入 | 明確輸出／拒絕 |
|---|---|---|
| resolve_reference | EvidenceRef | 驗證 owner/identity/version/hash 的 immutable snapshot；missing/hash mismatch 拒絕 |
| map_source | mapping_ref, source_name, source_code, bar_open_utc | 唯一 instrument_id/contract_id 與有效區間；0或多筆匹配拒絕 |
| resolve_contract | mapping_ref, instrument_id,contract_id | pinned ContractSpec、InstrumentSpec、effective interval；tick_size exact Decimal 必填正數 |
| calendar_slice | calendar_ref, contracts, start_at,end_at | 明示 covered interval、ordered tradable intervals、每段 trade_date/session_ref；coverage hole 拒絕 |

Calendar slice 必須聲明整段 requested range 的 coverage，包括明示休市。Tradable intervals 為 UTC [open,close)，對同 contract 不重疊、端點整分鐘、trade_date 為明示日期、session_ref 為穩定非空識別。Listed validity 同樣明示有效區間，不從系統今天的 ACTIVE flag 推導歷史可交易性。Reference canonical bytes/hash 的 registry owner 仍為 C；P01 只消費，不從本機 DuckDB 即時讀值後自行聲稱 pinned。

既有 trading_calendar/session_resolver.py 提供交易日計算 helper；repository.py 為 DB lookup，均未因此自動提供上述 snapshot completeness authority。無符合 Port 的證據時 fail closed；synthetic snapshot fixtures 可完成 repository 內驗證，真實 reference provider qualification 另列外部驗證，不把空 reference 當正式資料。

## 發布與查詢引用鏈

P01 先 stage partitions、quality report、source manifest，再建立 dataset manifest；所有檔案 bytes hash 必須一致。Source manifest 保存第一個被發布來源的 source_sha256、import metadata EvidenceRef 及 quality report EvidenceRef。Hash 是該 immutable JSON 檔的實際 UTF-8 bytes SHA256（固定 compact JSON key sort、LF）；與 content/version semantic hash 明確分開。

Layout 為 caller-owned root 下 `versions/<dv1_hash>/manifest.json`、`partitions/<number>.parquet`、`quality.json`、`source.json`。Manifest.partitions.relative_path 相對於 version directory；只允許既有 partitions regex，禁止 symlink／traversal。Stage 在相同 filesystem 的獨立目錄；完整 fsync 檔案、驗證 hashes 後原子 rename，目標已存在則驗證其 manifest/content/version 完整一致後 REUSED，不覆寫。Crash 前未 rename 的 stage 永遠不是 published dataset。目標存在但不一致為 integrity conflict，禁止修補成成功。跨 filesystem publish 拒絕。平台無法提供要求的 durable rename/flush 時明示環境限制，不宣稱 crash durability。

P01 publication 回傳 immutable PublicationResult（version_id、manifest byte hash、qualified report ref、PUBLISHED/REUSED），不自行建立 DB operation。P03 transaction owner 將 command/operation、此次 import metadata/report、DatasetImportReceipt 與 artifact manifest/index 綁定；receipt 引用此次來源，REUSED 不改第一份 dataset manifest。Operation success 只有在引用鏈 durable、artifact hash 可解析且 fence/current attempt 通過後才成立。檔案已發布但 DB commit 前 crash，可用 deterministic version 重查；orphan file 本身不代表 operation success。

Dataset lookup 依 exact version_id 找 manifest、驗證 hashes 再讀 partitions；immutable version 不依 mutable latest pointer。P03/P04 應提供 lookup adapter/API 與 receipt artifact 查詢，不能讓 P01 在 scope 外加入 server route。取消、worker fencing、唯一 terminal receipt 的交易語意歸 P03；本文件不以檔案 rename 冒充 DB 交易。

## 剩餘 gate

Snapshot machine schemas 已由 scripts/p00_build_contracts.py 定義 DatasetCalendarSnapshot、DatasetMappingSnapshot、DatasetQualityPolicySnapshot；另有 DatasetSourceManifest、DatasetPublicationResult。Fixture 與有限集合 oracle 見 dataset_quality.fixture.v1.json / test_p00_dataset_quality_cases.py。這些提供候選語意與反例，未實作 importer。

Machine snapshots 不含自身 sha256；外部 EvidenceRef 綁定其整份 compact UTF-8 JSON bytes（sort_keys、ensure_ascii=false、無額外空格、結尾LF）。消費端同時核對 owner/identity/version 與 hash。Reference snapshot 是 registry projection，不能建立新的 canonical contract/instrument owner。mapping entry 的 instrument_spec_ref/contract_spec_ref 必須解析既有型別並核對 IDs、tick_size 與有效區間；任何 unresolved/ref disagreement 一律拒絕。範圍、interval ordering/non-overlap、日期有效、mapping uniqueness、正 tick 與 calendar contract 集合的跨欄位約束由 consumer semantic validation 負責，schema 通過不取代它們。

P01 design status 為 DEFINED_CANDIDATE_PENDING_INDEPENDENT_REVIEW。真正 CSV parser、port/provenance integration、Q01-Q10 產品 end-to-end、filesystem crash/concurrency 與 P03 DB conformance 是未來 implementation acceptance；不能循環地要求它們先完成才授權實作。實作前仍須 P00 baseline 獨立接受、明確 scope/grant、context gate 與 dependency checks。產品 implementation 不由本文件授權。

PUBLISHED/REUSED 的 release acceptance 必測兩個 simultaneous publishers、rename 前後 crash、已存在但損壞 target、stale attempt、DB commit 前 crash。REUSED 比對 semantic version/material 與既有 byte integrity，不要求此次不同來源的 source manifest byte hash 等於首份來源；首份 manifest 不被覆寫。單機無法證明 filesystem durability 時不可標 durability PASS，可完成無此主張的功能測試並列環境 gate。
