# PK11 — 單一契約的 Web 與跨層旅程

狀態：SPEC_READY（文件可讀）／PLANNING_COMPLETE／QUALIFICATION_PENDING／IMPLEMENTATION_NOT_AUTHORIZED。EXECUTION_READY=false。

共用 UI／DTO／狀態、19 頁、React→ASP.NET BFF→Python API 的完整操作與端到端整合。

## 開始閱讀

先讀本包 `ENGINEERING_SPECIFICATION.json`，再依下列 Unit 的 exact source／base plan／v9 companion／model closure／operation spec／fixture／negative oracle；不載無關整體架構。此處每個連結都是規劃文件，不是 Grant。

| Unit | UUID | 實作目的 | 原上游 |
|---|---|---|---|
| [MA10-U01](units/MA10-U01.md) | 8ae2d3b5-7d39-4d7d-a05c-23ecfbecb8dc | Shared UI Layout／DTO／State system | MA01-U01 |
| [MA10-U02](units/MA10-U02.md) | 5af2fc67-7bb1-425e-99d2-3a345e356b6f | Market／Dashboard／Portfolio／Cash UI | MA10-U01, MA01-U01, MA02-U01, MA02-U05, MA03-U02, MA03-U04, MA05-U02, MA05-U03, MA05-U04, MA06-U01, MA06-U02, MA06-U04, MA06-U05, MA06-U06, MA16-U04, MA12-U04, MA04-U02, MA08-U03, MA08-U01 |
| [MA10-U03](units/MA10-U03.md) | 3d613bb3-e281-4ea7-a682-341eb3aff9d8 | Builder／Research／Compare／Library UI | MA10-U01, MA01-U01, MA04-U01, MA04-U02, MA04-U03, MA04-U04, MA04-U05, MA04-U06, MA07-U04 |
| [MA10-U04](units/MA10-U04.md) | 75db228f-e2b7-40f6-a45b-0bd6d339aeab | Simulation／Orders／Risk／Positions UI | MA10-U01, MA01-U01, MA04-U04, MA06-U02, MA06-U06, MA07-U02, MA07-U05, MA08-U01, MA08-U03, MA08-U04, MA10-U02 |
| [MA10-U05](units/MA10-U05.md) | 62dbf7f6-c1bf-406f-b448-e84b114c59e6 | URMS／Artifact／Automation／Settings UI | MA10-U01, MA01-U01, MA09-U01, MA11-U02, MA11-U03, MA11-U04, MA12-U01, MA12-U04, MA13-U01, MA13-U02, MA13-U05, MA14-U06, MA16-U02, MA16-U04 |
| [MA10-U06](units/MA10-U06.md) | 0725e6af-4fbf-4f0f-b1f4-37fb0455548f | BFF／Python／SignalR與六旅程E2E | MA10-U01, MA01-U01, MA10-U02, MA10-U03, MA10-U04, MA10-U05 |

## 精確操作及驗收

各 Unit JSON 已保留原完整 row/base plan、Feature／Requirement revisions、input/output、API DTO欄位、唯一 Producer／Consumer mode、Mock 原文、negative cases、proposed path/preimage、protected blobs、qualification、具體 postcondition 與 Actual evidence要求。

本包直接負責的 API：getDashboard

Frontend／BFF／Core／Persistence責任沿唯一Producer。Pure UI/UX可在合法範圍集中修正；API/DTO、資料完整性、Capital/Order/Fill或Authority漂移立即HOLD受影響路徑。

Finding Regression候選：F4-08, F6-01, F6-02, S6-TEST-02, PRODUCT-S4-01, PRODUCT-S4-02, PRODUCT-S4-03, PRODUCT-S4-04, PRODUCT-S4-05, PRODUCT-S4-06, PRODUCT-S5-01, PRODUCT-S5-02, PRODUCT-S5-03, MA-ARCH-v3-S7-IF02, MA-ARCH-v3-S7-IF03, MA-ARCH-v3-S7-IF04, MA-ARCH-v3-S7-IF05, MA-ARCH-v3-S8-EX01, MA-ARCH-v3-S8-EX02

所有測試是規格，尚未實作或執行；原強制Full／Wave-final／Independent Review不能由影響選取免除。

取得有效授權後：Contract → Authorized Coding → Targeted Tests → Integration → Regression → 原Review/Intake/Acceptance → Re-entry。尚缺source assembly、Profile/Adapter、WO/Grant/Budget/Writer等，不能執行。
