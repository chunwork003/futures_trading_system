# R06-SOURCE-02 — CSV 契約架構決策候選

狀態：DECISION_REQUIRED / NOT_APPLIED / NOT_ACCEPTED。這是 P00 架構提案，原 API、CSV_V1、OpenAPI、package、compiler 與 accepted authority 保持原 bytes。

## 問題與約束

API「Queries, errors and audit」要求九欄且禁止 BOM；dataset owner「CSV_V1」要求十欄、容許檔首一個 BOM。兩份 OpenAPI 都宣告 format=CSV_V1，卻沒有 explicit 九欄轉十欄 adapter。精確來源、原段落與 hash 位於同名 JSON；不以檔名或章節順序自行解消衝突。

P1 / LEVEL 3 / HARD_BLOCK 僅阻擋受影響 CSV 公開語意；可繼續互不相依 P00 證據工作。任何決策均不授予 P01/P02 實作、P00 acceptance 或 publication。

## 替代方案與建議

| 選項 | 具體變更 | 相容性與風險 | 就緒程度 |
|---|---|---|---|
| A（建議，未選定） | HTTP bytes 直接遵守既有 CSV_V1 十欄及一個檔首 BOM；只修 API 一段 | 舊九欄輸入會拒絕；目前是否存在 client 為 UNKNOWN，不能宣稱無 breaking change | exact patch 已備，待語意決策與審查 |
| B | 保留九欄及十欄，但以版本與 explicit adapter 區分 | identity、nullable values、timeframe、BOM、原始 bytes retry/hash/lineage、owner 全需明定；無來源不可猜轉換 | 決策需求已具體化，尚無可套用 patch |

推薦 A 的理由是沿用已命名的 CSV_V1 與 dedicated data owner，不新增第二套轉換責任；這只是建議，不代表已判定原 API 是筆誤。若需要保留九欄 client，應補齊 B 的八項決策與 exact reviewed amendments。

## A 的精確修訂與安全保留

同名 `.option-A.patch` 只替換 API Dataset import 段落。原段落從「Caller supplies trusted reference revisions」起的尾段逐 byte 保留，涵蓋 256 MiB、SHA256、1 MiB metadata、禁止 path/URL、durable admission、7 日 orphan cleanup、exact retry、qualified atomic publication、cancel、correction lineage、canonical adapter authority。原 OHLC predicates 在 replacement 明列保留。

A 不把 BOM 去除後的 hash 冒充原始 upload hash；相同語意而 BOM 或換行不同的檔案仍是不同 bytes，same key 應拒絕。P01 semantic version 與 upload byte hash 不混用。來源文件其餘部分與所有其他 source byte 完整保留；candidate 尚未套用。

## 必讀義務與反例

| 義務 | 正向契約 | 負面／protected 反例 |
|---|---|---|
| CSV_HEADER | CSV_V1 固定十欄；HTTP 與 P01 bytes 同一契約 | 九欄舊 API header 應拒絕，不隱式轉換 |
| BOM | strict UTF-8，最多檔首一個 BOM | 雙 BOM、列中 BOM 不得當第二個檔首 BOM；hash 仍取原始 bytes |
| IDENTITY | source_name + opaque source_code 由 pinned mapping 唯一解析 | 零／多筆匹配、未知 namespace、直接 identity 欄不猜測 |
| TIME | 真實 Gregorian 整分鐘 UTC Z | offset、無效日期、非零秒及本機時區推測拒絕 |
| DECIMAL | 沿用 Decimal lexical；amount 空字串 null | float/exponent/NaN/Infinity 不容許；不自行另定 price format |
| COUNTS | volume 必填；三個 optional value 空字串 null | null 不填 0；負 count／volume 拒絕 |
| CALENDAR | trade_date/session_ref 來自 pinned calendar | 空 calendar／CSV 自報日曆不建立完整性 |
| OHLC | 三個既有 high/low predicates 全部保留 | 合法 Decimal 但 high < open 仍非有效列 |
| UPLOAD | 256 MiB stream；metadata/ordinary JSON 1 MiB；filename ignored；SHA256 | chunk 不改 hash；BOM 差異仍有不同原始 bytes hash |
| RETRY | key compares original metadata + file hash | 語意相同而 bytes 不同，不能冒充 exact retry |
| TRANSACTION | verified upload 才 durable admission；orphan 7 days；atomic qualified publication；cancel/lineage | file 或 shape pass 不等於成功 operation；parent/correction reason 必須成對 |
| AUTHORITY | canonical observation 仍由 accepted adapter 驗證 | CSV、hash、publication、review pass 都不授予交易／實作權限 |

## 審查及後續順序

1. 確認唯一格式選擇與 BOM 邊界，或補足 B 的八項未知決策。architecture approval 必須明指選項與精確來源，不將「繼續」解讀為決策。
2. 若選 A，先以 source SHA/paragraph/patch hash 重驗，形成 bounded 文檔修訂；generator 無 delta 仍須核對，不能手改 generated OpenAPI。
3. 獨立語意審查後，建立 source02 的 successor finding/reading mapping；歷史 map/checkpoint、編譯與結果不改寫成已通過。
4. 完整 negative/protected 義務與 full-source fallback 保留。原 aggregate 128KiB gate、七類 UNKNOWN intake、可信 receipt、P00 acceptance 和 exact product grant 仍各自獨立。

## 證據限制

patch dry-run、source byte/hash checks 與 platform tests 只能證明提案可重現及 bounded preservation；不證明已有 CSV parser、production upload、filesystem/DB crash conformance、review PASS 或 acceptance。

References：同名 JSON 的七份 exact Git sources；`automation/platform/SOURCE_READING_OBLIGATIONS.md` 與 source-map review 是既有待審背景，保持不可變。
