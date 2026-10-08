# Dataset Quality and Correction — P00 Candidate

狀態：DEFINED_CANDIDATE / NOT_ACCEPTED。Owner：B ingestion、C versioned calendar/contract reference。這是研究資料集資格，不能提供 broker-current evidence、RecoveryCut readiness 或 production authority。

## 品質政策與 required coverage

第一個政策為 `RESEARCH_STRICT_1M_V1`，只接受一分鐘 OHLCV、明確 listed contract identity、固定 calendar/mapping references。其他 timeframe 拒絕，不默默 resample；後續政策可擴充，但不能改變舊 dataset。此限制不縮減既有 MarketObservation domain 支援的 timeframe。

必要區間由 caller 明示 `[start_at,end_at)`，使用對齊整分鐘的 UTC instant，且 end > start。不得從已觀測第一／最後一筆推導必要區間，否則會隱藏頭尾缺棒。Calendar evidence 必須覆蓋整個區間，包含休市區段；缺少 reference coverage 一律 UNQUALIFIED_REFERENCE，不得推導 required_bars=0。

C 提供每個 listed contract 的 tradable intervals 與 trading_date。只有完整位於一個 tradable interval 內的一分鐘 bar 才屬 required；非整分鐘 session boundary 在本政策拒絕。Expected keys 為明示 contract 集合及其有效上市期間內的 required minute intervals。空 expected set 拒絕為 EMPTY_REQUIRED_COVERAGE。夜盤 trading_date 由 calendar 提供，不得用 UTC date 代替。

Observed key 使用既有 identity `(instrument_id,contract_id,timeframe,bar_open_utc)`。比對前以 exact mapping reference 解析 source code；無匹配、多重匹配、超出有效期間、listed metadata 缺失均拒絕。不猜近月、不以 alias 當 canonical identity。內容沿用 accepted MarketObservation 驗證；價格 exact finite Decimal 且符合 reference tick grid，volume 為非負整數，OHLC 滿足 low <= open/close <= high。不得用零量棒填補缺棒；來源明示且其他條件合法的零量棒可接受。

## 計數與判定優先序

先 canonical normalization，再按 key 計數，與輸入順序無關。duplicate_rows 是完全相同 material 的多餘列數，不是重複群組數。conflicting_keys 是存在多種 material 的 key 數。observed_bars 是 expected set 中僅有一種 material 的 distinct key 數；missing_bars 為 expected 減 observed，因此 unresolved conflicting key 同時列入 missing。Out-of-session/out-of-range 按 distinct key 計數。Report 可同時列多項失敗，verdict 按下表優先序選擇。

| 優先序 | 條件 | 結果 |
|---|---|---|
| 1 | Bytes/schema、值或 identity 無效 | INVALID_INPUT；不發布 |
| 2 | Mapping/calendar 缺失、歧義或 coverage 未證明 | UNQUALIFIED_REFERENCE；不發布 |
| 3 | 本次上傳同 key 不同 material | CONFLICTING_CONTENT；不選 winner、不發布 |
| 4 | Out-of-range/session、缺棒或空 required set | INCOMPLETE_COVERAGE；不發布 |
| 5 | 全部條件滿足 | QUALIFIED_RESEARCH；才可進入發布程序 |

完全相同重複列可 dedup，保留 audit count，不改 canonical content identity。QualityReport 綁定 policy/version/hash、reference hashes、required interval、expected/observed key-set fingerprints 與各項 counts。DatasetManifest.accepted_quality_report 必須解析至該 immutable report。載入時 report/reference 缺失是 integrity error，不得只信歷史 QUALIFIED flag。

## 更正 lineage 與 precedence

Correction 是同一 dataset、同一 required key set 的完整替代 snapshot，必須明示 parent version 與非空 reason。Parent 必須存在、immutable 且屬同 dataset。第一版 correction mode 的 calendar/mapping/quality-policy references 與 coverage 維持一致；更換這些內容須建立新 root lineage，不能冒充單純改棒。

Candidate 必須獨立通過完整品質驗證；不接受缺項 delta upload 從 parent 自動補列。不以 ingestion time、檔名順序、provider priority 或最高價格選 winner。可有多個明示 parent 的 child versions；不存在 mutable latest authority，research run 必須 pin exact version。即使有 correction metadata，上傳內容本身 unresolved duplicate conflict 仍拒絕。禁止原地覆寫與刪除 parent。

相同 semantic inputs 重送應返回既有 immutable version。Raw source bytes、檔名、ingestion timestamp、duplicate counts 屬個別 import receipt，不屬 economic content identity。每次 receipt 保存自己的 source hash 與 report；重排上傳不得改寫第一份 published manifest。區分 canonical content hash（rows）與 version identity（dataset、content、required coverage、policy/reference hashes、明示 parent lineage）。Exact byte framing 與 import receipt DTO 尚待下節 closure，不交給 executor 猜測。

## 必要 golden cases

使用 synthetic calendar evidence；以下時間不是實際交易所時段主張。

| ID | 輸入 | 必要結果 |
|---|---|---|
| Q01 | Expected opens 00:00、00:01；反序輸入 | 與正序相同 content；observed2/missing0 |
| Q02 | 同 expected；00:00 完全相同兩列，加 00:01 | observed2/duplicate_rows1；content 相同 |
| Q03 | 同 expected；只有 00:01 | observed1/missing1；INCOMPLETE_COVERAGE |
| Q04 | 00:00 有兩種 close，加 00:01 | conflicting_keys1/observed1/missing1；CONFLICTING_CONTENT |
| Q05 | Calendar 無 required range 尾端證據 | UNQUALIFIED_REFERENCE；不偽造 missing0 |
| Q06 | Synthetic 夜盤指定 next trading_date | 保存 calendar trading_date，不用 UTC date 替代 |
| Q07 | Qualified child 更正一筆 close，明示 parent/reason | 新 child；舊 run 保持舊 parent 內容 |
| Q08 | Child upload 自身含 conflicting duplicate | 拒絕；correction metadata 不提供 winner |
| Q09 | 相同 rows，不同 reference hash 或 required range | 不得僅凭 content hash 宣稱相同 version |
| Q10 | 空 required set 或自動零量補棒 | 空 coverage 拒絕；importer 不得產生 filler |

## 尚待介面 closure

目前 ImportMetadata 缺 explicit timeframe/required coverage；source_manifest_hash 也不足以表達 content dedup 後每次 import provenance。P00 必須在單一 OpenAPI authoring source 定義這些 wire fields、import receipt、QualityReport schema 與 exact version-hash framing，再跑 schema/golden consistency tests。上述是具體架構缺口，不是 P01 implementer 可自行猜測的 routine correction。本文件提供品質／更正語意決定，未授權 execution。
