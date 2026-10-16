# PK01 — 來源、Scope 與可追溯採納輸入

狀態：SPEC_READY（文件可讀）／PLANNING_COMPLETE／QUALIFICATION_PENDING／IMPLEMENTATION_NOT_AUTHORIZED。EXECUTION_READY=false。

固定 Source／Release Slice、權重與反向映射、變更影響及審核輸入；不物化 Human 接受。

## 開始閱讀

先讀本包 `ENGINEERING_SPECIFICATION.json`，再依下列 Unit 的 exact source／base plan／v9 companion／model closure／operation spec／fixture／negative oracle；不載無關整體架構。此處每個連結都是規劃文件，不是 Grant。

| Unit | UUID | 實作目的 | 原上游 |
|---|---|---|---|
| [MA01-U01](units/MA01-U01.md) | cfc91817-46ea-4145-8427-139e06e5569d | 來源與需求 Ledger |  |
| [MA01-U02](units/MA01-U02.md) | a4f5ef10-5f3b-4102-955e-40dfec5e9670 | Scope／ReleaseSlice Crosswalk | MA01-U01 |
| [MA01-U03](units/MA01-U03.md) | 633d33a6-fe05-4935-ba18-be8c9566092c | 歷史權重與reverse mappings | MA01-U01 |
| [MA01-U04](units/MA01-U04.md) | d577c63a-cdb0-4f9d-b822-e0729b39caea | P00 C3／C5／C6 compatibility | MA01-U01 |
| [MA01-U05](units/MA01-U05.md) | b0e3f573-d911-4ea1-8dc3-57a89f7bd95e | Scope Delta採納 companion | MA01-U01 |
| [MA01-U06](units/MA01-U06.md) | 2451c839-f649-459e-ad0a-000ce0d15e70 | 來源與scope整合驗證 | MA01-U01, MA01-U02, MA01-U03, MA01-U04, MA01-U05 |
| [MA15-U01](units/MA15-U01.md) | 6aa09fb0-df29-41cc-aa5a-9d7aafb8011a | Requirement→Design→Unit Traceability | MA01-U01 |
| [MA15-U02](units/MA15-U02.md) | f6d3c601-3859-4405-80d1-3ea1b8e737b4 | CrosschapterSchema/API/EventCompatibility | MA15-U01, MA01-U01 |
| [MA15-U04](units/MA15-U04.md) | 87685a87-d4a5-43f5-b5b9-df5c61d067aa | Four Gate／P00 C3C5C6 Matrix | MA15-U01, MA01-U01 |
| [MA15-U05](units/MA15-U05.md) | 6fde1133-cc4a-4e92-a48a-97ce79775779 | Immutable Review Bundle／ExactSubjects | MA15-U01, MA01-U01 |

## 精確操作及驗收

各 Unit JSON 已保留原完整 row/base plan、Feature／Requirement revisions、input/output、API DTO欄位、唯一 Producer／Consumer mode、Mock 原文、negative cases、proposed path/preimage、protected blobs、qualification、具體 postcondition 與 Actual evidence要求。

本包直接負責的 API：無；其他 API 只作 touched/check-source 閉包，不取得 write scope。

Frontend／BFF／Core／Persistence責任沿唯一Producer。Pure UI/UX可在合法範圍集中修正；API/DTO、資料完整性、Capital/Order/Fill或Authority漂移立即HOLD受影響路徑。

Finding Regression候選：按變更觸發器查既有64筆backlog，不創造無關新任務。

所有測試是規格，尚未實作或執行；原強制Full／Wave-final／Independent Review不能由影響選取免除。

取得有效授權後：Contract → Authorized Coding → Targeted Tests → Integration → Regression → 原Review/Intake/Acceptance → Re-entry。尚缺source assembly、Profile/Adapter、WO/Grant/Budget/Writer等，不能執行。
