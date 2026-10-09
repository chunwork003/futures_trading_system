# R06 remaining Context carriers — exact published subject

狀態：SIZE_AND_VALUE_PRESERVATION_ONLY / REVIEW_PENDING。Subject：`75ef4207aafaaabbf8bf130dea25f78726361626`。SOURCE01 五檔候選保持未套用；此文件不採納 policy、compiler、CURRENT 或 intake successor。

## 分析與證據

| 同一精確 subject / bytes | P01 | P02 |
|---|---:|---:|
| 原 mandatory raw source aggregate | 927649 | 878974 |
| 既有 selective reading pack | 336929 | 433113 |
| 既有 full OpenAPI 去重 pack（CURRENT history 仍是 mandatory source reference） | 491242 | 458759 |
| 所有 JSON 只移除空白，保留所有值；其餘 source raw 不動，不含新 metadata | 695700 | 662976 |
| 上列再假設採用既有 CURRENT history reference 邊界，不含新 metadata | 552921 | 520197 |
| 原 gate | 131072 | 131072 |

最後兩列是未採納的大小分析，不能交給原 compiler 當新 mandatory basis。負面 source 原 resolver 仍未加入 mandatory；兩包各須保留額外 1496 bytes 的完整負面來源。加入該完整來源會增加大小，不會讓 gate 通過。SOURCE01 candidate 在隔離 fixture 處理 representation，不建立 semantic/read/intake qualification。

兩份 OpenAPI raw 為 216252 + 204713 = 420965 bytes；完整 canonical JSON 為 118196 + 110894 = 229090 bytes。無損去除空白仍不能單獨解決 total budget。Full JSON duplicate keys 檢查、roundtrip、full OpenAPI schema pool expand 與 source value comparison 保留所有 HTTP paths、schemas、security、error responses、constraints、required、extensions 與 refs；這是值完整性，並非獨立語意審查。

Selective pack 的額外大項包括 p00_status 35269 bytes、AGENTS 22311 bytes、master manifest 21263 bytes、accepted-core reconciliation 16875 bytes。P02 兩份 OpenAPI document carriers 為 65484 + 57881 bytes，shared schema pool 為 36603 bytes；上述 carrier/metadata 不可當成可任意刪除的冗餘。P01 shared schema pool 為 17912 bytes。逐檔 raw refs、原始與 hypothetical byte accounting、所有 projection/excluded/full fallback 規則保存於 `R06-context-carriers.analysis.v1.json`。

既有 source-reading mapping、676 units、51 critical obligations（包括13 negatives/7 invariants）、P01/P02 contract/HTTP obligation closure 保留，不在此輪重建或降級。未分類條款、歷史 contradiction、review/provenance 仍必須讀取完整 exact source；hash/ref/閱讀 shape 不等於實際理解或可信收據。LATEST RESULT、STOP、pending review/acceptance/integration/delta 的 intake completeness 仍未 qualified；source projection NONE 不等於 global NONE。

## Alternatives、風險與建議

1. CTX01：完整 JSON normalization / schema 去重可減少 transport bytes，但本次實測全部超標，不能只以此結案。
2. CTX02：下一個 compact candidate 應明確處理 p00_status、master manifest、AGENTS 的 current/historical/full-source obligations；完整保存 source bytes 與 fallback，不能刪掉未分類安全/負面語意。
3. CTX03：從既有完整 mapping 逐一證明 obligation discharge、依賴 closure 與 latest result/intake，再接受 carrier successor；須獨立語意審查、actual model reading/eval，不能把 source representation 或 synthetic tests 當成 reading qualification。
4. CTX04：如果完整必要內容仍超過原 aggregate 131072，需 explicit Owner budget/continuity successor decision。每批大小不是原 gate 的替代，不能靜默分批豁免。

建議先以 CTX02/CTX03 保存精確 current metadata candidates 與反例，再交付具體 CTX04 選項。原 compiler/policy/source pointers 保持原狀；P00 acceptance 與 exact package grant 之前，P01/P02 implementation NOT_AUTHORIZED。

## Reproduction / References

`python -B docs/program/decisions/R06-context-carriers.reproduce.py --output .tmp/context-carriers-repeat.json`

兩次完整 JSON identical；canonical SHA256：`5f0d9118207ee01314093add5429bf80330058082c518476a58a00d7554bf58a`。Recipe pins published subject，從 exact raw Git blobs 讀取，驗證 loaded owners；不讀 data、不改原來源。SOURCE01 full-platform successor 的 fixture provenance/完整結果另見 `R06-SOURCE-01.full-platform-validation.v1.json`；不得把 transport/value/fixture 證據升格為 acceptance、model 或 backend conformance。
