# PK03 — 永久 Registry 與正式出版投影

狀態：SPEC_READY（文件可讀）／PLANNING_COMPLETE／QUALIFICATION_PENDING／IMPLEMENTATION_NOT_AUTHORIZED。EXECUTION_READY=false。

永久身份、代碼／Alias、雙樹／DAG；Exact Review、Publication Unknown、Git Export、SQL Projection。

## 開始閱讀

先讀本包 `ENGINEERING_SPECIFICATION.json`，再依下列 Unit 的 exact source／base plan／v9 companion／model closure／operation spec／fixture／negative oracle；不載無關整體架構。此處每個連結都是規劃文件，不是 Grant。

| Unit | UUID | 實作目的 | 原上游 |
|---|---|---|---|
| [MA11-U01](units/MA11-U01.md) | 24eadee4-4e15-40a4-90d8-90556f574dd1 | PermanentEntity／LegacyCode bridge | MA01-U01 |
| [MA11-U02](units/MA11-U02.md) | 550e6375-b311-43cc-a75b-4468b858b826 | Typed Segment／Grammar／Alias | MA11-U01, MA01-U01 |
| [MA11-U03](units/MA11-U03.md) | 77c0018d-8680-4e94-a7b9-7fe0de492c60 | 雙樹／Typed Relations／DAG | MA11-U01, MA01-U01 |
| [MA11-U04](units/MA11-U04.md) | 31426b58-bf4e-49bb-8e9d-3a85cb8c2218 | Revision／Move／Split／Merge／Retire | MA11-U01, MA01-U01 |
| [MA11-U05](units/MA11-U05.md) | 58445c72-5dbd-4e97-8cbe-c077a2a56ed2 | SQL FK／Unique／CAS／Idempotency | MA11-U01, MA01-U01 |
| [MA11-U06](units/MA11-U06.md) | 4dca68b7-4b4d-46f6-942f-88449b4fe158 | Git Registry Full Rebuild／Weights | MA11-U01, MA01-U01, MA11-U02, MA11-U03, MA11-U04, MA11-U05 |
| [MA12-U01](units/MA12-U01.md) | e185c30d-eebf-43b9-ae51-16e9fbe512da | Frozen Candidate／Review Closure | MA11-U01 |
| [MA12-U02](units/MA12-U02.md) | 56d3d5a6-e69a-401b-b92a-a6dcba032d10 | Review／Adoption／Publisher Roles | MA12-U01, MA11-U01 |
| [MA12-U03](units/MA12-U03.md) | b10bf655-7e29-42bb-9a13-76861e6fd09c | Canonical Safe Git Export | MA12-U01, MA11-U01, MA11-U04 |
| [MA12-U04](units/MA12-U04.md) | a2c5f009-53d8-4b97-bd37-be95b61ba3fe | Publication Intent／Unknown Reconcile | MA12-U01, MA11-U01 |
| [MA12-U05](units/MA12-U05.md) | 0ce2e2ae-646a-4c01-8775-9768cdd56b2e | SQL Projection Import Transaction | MA12-U01, MA11-U01 |
| [MA12-U06](units/MA12-U06.md) | cdecd5cf-839c-4da8-85e0-76c1b0863d62 | Impact／Failure A–O compatibility | MA12-U01, MA11-U01, MA12-U02, MA12-U03, MA12-U04, MA12-U05 |

## 精確操作及驗收

各 Unit JSON 已保留原完整 row/base plan、Feature／Requirement revisions、input/output、API DTO欄位、唯一 Producer／Consumer mode、Mock 原文、negative cases、proposed path/preimage、protected blobs、qualification、具體 postcondition 與 Actual evidence要求。

本包直接負責的 API：getAlias, getOperation, getRegistry, getReviewSubject, proposeRegistry

Frontend／BFF／Core／Persistence責任沿唯一Producer。Pure UI/UX可在合法範圍集中修正；API/DTO、資料完整性、Capital/Order/Fill或Authority漂移立即HOLD受影響路徑。

Finding Regression候選：F2-01, F2-02, F2-03, F2-04, F2-05, F2-07, F3-08, F6-03, F6-04, F6-05, F6-08, F2-08, F3-01, F3-02, F3-03, F3-05, F3-06, F3-07, F4-07, S1-AUTH-01, S1-SCOPE-02, S1-ROUTE-03, S2-CODE-01, S2-REL-02

所有測試是規格，尚未實作或執行；原強制Full／Wave-final／Independent Review不能由影響選取免除。

取得有效授權後：Contract → Authorized Coding → Targeted Tests → Integration → Regression → 原Review/Intake/Acceptance → Re-entry。尚缺source assembly、Profile/Adapter、WO/Grant/Budget/Writer等，不能執行。
