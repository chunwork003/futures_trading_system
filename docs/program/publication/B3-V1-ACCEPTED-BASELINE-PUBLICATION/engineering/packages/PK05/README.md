# PK05 — 既有 WORK 的施工連續性

狀態：SPEC_READY（文件可讀）／PLANNING_COMPLETE／QUALIFICATION_PENDING／IMPLEMENTATION_NOT_AUTHORIZED。EXECUTION_READY=false。

Raw Plan／v9 Companion 到既有 Compiler 的有界 Adapter、能力／成本、Executor 切換、Trusted Context、STOP／Resume。

## 開始閱讀

先讀本包 `ENGINEERING_SPECIFICATION.json`，再依下列 Unit 的 exact source／base plan／v9 companion／model closure／operation spec／fixture／negative oracle；不載無關整體架構。此處每個連結都是規劃文件，不是 Grant。

| Unit | UUID | 實作目的 | 原上游 |
|---|---|---|---|
| [MA14-U01](units/MA14-U01.md) | c709d850-b687-458d-abdd-669bab608b66 | Unit Companion／ExistingCompiler Adapter | MA01-U01, MA01-U05, MA12-U01, MA12-U02 |
| [MA14-U02](units/MA14-U02.md) | 4f430dbc-e115-4b81-b167-213e4bec9618 | Qualified Cost Routing v2 | MA14-U01, MA01-U01 |
| [MA14-U03](units/MA14-U03.md) | a78c07f3-7fe9-4937-b2d2-915e8c01061b | Estimate/Actual/Quota Producer | MA14-U01, MA01-U01 |
| [MA14-U04](units/MA14-U04.md) | 79721523-c63f-4fdb-ac01-f16280c0c487 | Executor Switch／Result Intake | MA14-U01, MA01-U01, MA14-U02, MA14-U03 |
| [MA14-U05](units/MA14-U05.md) | 26cba0b2-f5f6-4bfc-9a87-04f407a4d874 | Context／Trusted Reading／STOPResume | MA14-U01, MA01-U01 |
| [MA14-U06](units/MA14-U06.md) | 069c5da8-3515-4f82-aec7-1a069091b5c9 | Program／DAG／Dailyplan Projection | MA14-U01, MA01-U01, MA14-U02, MA14-U03, MA14-U04, MA14-U05 |

## 精確操作及驗收

各 Unit JSON 已保留原完整 row/base plan、Feature／Requirement revisions、input/output、API DTO欄位、唯一 Producer／Consumer mode、Mock 原文、negative cases、proposed path/preimage、protected blobs、qualification、具體 postcondition 與 Actual evidence要求。

本包直接負責的 API：getEngineeringStatus, proposePlanning

Frontend／BFF／Core／Persistence責任沿唯一Producer。Pure UI/UX可在合法範圍集中修正；API/DTO、資料完整性、Capital/Order/Fill或Authority漂移立即HOLD受影響路徑。

Finding Regression候選：F2-01, F2-02, F2-03, F2-04, F2-05, F2-07, F3-08, F6-03, F6-04, F6-05, F6-08, F3-04, F4-01, F4-02, F4-03, F4-04, F2-06, F4-06, F5-01, F5-03, F5-04, F5-05, F5-06, F5-07, F5-08, F6-07, S1-AUTH-01, S1-SCOPE-02, S1-ROUTE-03, S6-TEST-02, MA-ARCH-v3-S8-EX01, MA-ARCH-v3-S8-EX02, SPECIAL01-OPS-CLOSURE-01, SCHEMA-SPECIAL01-CONSUMER-PAIR-01

所有測試是規格，尚未實作或執行；原強制Full／Wave-final／Independent Review不能由影響選取免除。

取得有效授權後：Contract → Authorized Coding → Targeted Tests → Integration → Regression → 原Review/Intake/Acceptance → Re-entry。尚缺source assembly、Profile/Adapter、WO/Grant/Budget/Writer等，不能執行。
