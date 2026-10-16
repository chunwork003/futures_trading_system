# PK02 — 商品與可信資料快照

狀態：SPEC_READY（文件可讀）／PLANNING_COMPLETE／QUALIFICATION_PENDING／IMPLEMENTATION_NOT_AUTHORIZED。EXECUTION_READY=false。

Instrument／Listing／商品規則與 Calendar；來源、MarketBar／Observation、Quality、Dataset Snapshot、Replay 相容。

## 開始閱讀

先讀本包 `ENGINEERING_SPECIFICATION.json`，再依下列 Unit 的 exact source／base plan／v9 companion／model closure／operation spec／fixture／negative oracle；不載無關整體架構。此處每個連結都是規劃文件，不是 Grant。

| Unit | UUID | 實作目的 | 原上游 |
|---|---|---|---|
| [MA02-U01](units/MA02-U01.md) | 69b6baec-4e0d-42df-ab4f-5900e97f48b6 | Permanent Instrument／Listing bridge | MA01-U01 |
| [MA02-U02](units/MA02-U02.md) | 12e11da3-4d67-4fa7-a29f-f34ac6e64d27 | Stock／ETF corporateaction／rules | MA02-U01, MA01-U01 |
| [MA02-U03](units/MA02-U03.md) | 1f4be8f2-675d-4a0f-82a9-3f8376c106e2 | Futures／Options terms和cashflows | MA02-U01, MA01-U01 |
| [MA02-U04](units/MA02-U04.md) | d8a840bf-577a-4689-9317-2b6db9520ad0 | Bond／Fund／FX valuation profiles | MA02-U01, MA01-U01 |
| [MA02-U05](units/MA02-U05.md) | bb7fcd6e-af41-43e9-aeb4-81fc14571315 | Calendar／Settlement policy interfaces | MA02-U01, MA01-U01 |
| [MA02-U06](units/MA02-U06.md) | 029f6c82-78b0-45d5-9c05-ddea6ce17f02 | 多資產Domain legacy適配與資格 | MA02-U01, MA01-U01, MA02-U02, MA02-U03, MA02-U04, MA02-U05 |
| [MA03-U01](units/MA03-U01.md) | 06b5e143-8782-463d-863c-0b58dbde03aa | 來源捕捉與immutable RawObject | MA02-U01 |
| [MA03-U02](units/MA03-U02.md) | ad7fdaed-5e0d-4a51-a24b-1922f8ce6f26 | Canonical typed observations | MA03-U01, MA02-U01 |
| [MA03-U03](units/MA03-U03.md) | cc769c63-0f27-4815-adf3-754774b76d5f | Quality／Completeness proofs | MA03-U01, MA02-U01 |
| [MA03-U04](units/MA03-U04.md) | a8a56800-81b9-4297-8847-ad2bb530ae83 | Dataset／Snapshot／Parquet閉包 | MA03-U01, MA02-U01 |
| [MA03-U05](units/MA03-U05.md) | fd74b3fa-93fc-473f-9208-106dc4e1742b | Feed／Replay／cursor resume | MA03-U01, MA02-U01 |
| [MA03-U06](units/MA03-U06.md) | d8b043c9-d0b1-482e-8983-b27bddb726e5 | Data Pipeline consumer契約測試 | MA03-U01, MA02-U01, MA03-U02, MA03-U03, MA03-U04, MA03-U05 |

## 精確操作及驗收

各 Unit JSON 已保留原完整 row/base plan、Feature／Requirement revisions、input/output、API DTO欄位、唯一 Producer／Consumer mode、Mock 原文、negative cases、proposed path/preimage、protected blobs、qualification、具體 postcondition 與 Actual evidence要求。

本包直接負責的 API：getDatasetSnapshot, getInstrumentRevision, getMarketRule, listDatasets, listInstruments, queryMarketBars, queryObservations, sealDatasetSnapshot

Frontend／BFF／Core／Persistence責任沿唯一Producer。Pure UI/UX可在合法範圍集中修正；API/DTO、資料完整性、Capital/Order/Fill或Authority漂移立即HOLD受影響路徑。

Finding Regression候選：按變更觸發器查既有64筆backlog，不創造無關新任務。

所有測試是規格，尚未實作或執行；原強制Full／Wave-final／Independent Review不能由影響選取免除。

取得有效授權後：Contract → Authorized Coding → Targeted Tests → Integration → Regression → 原Review/Intake/Acceptance → Re-entry。尚缺source assembly、Profile/Adapter、WO/Grant/Budget/Writer等，不能執行。
