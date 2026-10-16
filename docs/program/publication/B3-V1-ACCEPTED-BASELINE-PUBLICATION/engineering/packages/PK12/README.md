# PK12 — 同版本 B3 整合與交付審核

狀態：SPEC_READY（文件可讀）／PLANNING_COMPLETE／QUALIFICATION_PENDING／IMPLEMENTATION_NOT_AUTHORIZED。EXECUTION_READY=false。

六旅程、Source／Unit／Result 追溯、相同 Release Subject 的 Independent Review 與剩餘資格交付。

## 開始閱讀

先讀本包 `ENGINEERING_SPECIFICATION.json`，再依下列 Unit 的 exact source／base plan／v9 companion／model closure／operation spec／fixture／negative oracle；不載無關整體架構。此處每個連結都是規劃文件，不是 Grant。

| Unit | UUID | 實作目的 | 原上游 |
|---|---|---|---|
| [MA15-U03](units/MA15-U03.md) | 1850113a-d5c2-447c-acb6-59f804960ffc | SixJourney Integration Fixtures | MA15-U01, MA01-U01, MA01-U05, MA02-U05, MA03-U01, MA03-U02, MA03-U03, MA03-U04, MA03-U05, MA04-U01, MA04-U02, MA04-U03, MA04-U04, MA04-U05, MA04-U06, MA06-U01, MA06-U02, MA06-U03, MA06-U04, MA06-U05, MA07-U01, MA07-U02, MA07-U04, MA07-U05, MA08-U01, MA08-U02, MA08-U03, MA08-U04, MA08-U05, MA09-U04, MA09-U05, MA10-U06, MA11-U03, MA12-U01, MA12-U02, MA12-U04, MA12-U05, MA13-U03, MA13-U05, MA13-U06, MA14-U01, MA14-U04, MA14-U05, MA14-U06, MA16-U05 |
| [MA15-U06](units/MA15-U06.md) | 4d2d73f5-5f2b-47ea-bee8-63031e9e9a0e | ReviewFinding／Adoption／RemainingQualification | MA15-U01, MA01-U01, MA15-U02, MA15-U03, MA15-U04, MA15-U05 |

## 精確操作及驗收

各 Unit JSON 已保留原完整 row/base plan、Feature／Requirement revisions、input/output、API DTO欄位、唯一 Producer／Consumer mode、Mock 原文、negative cases、proposed path/preimage、protected blobs、qualification、具體 postcondition 與 Actual evidence要求。

本包直接負責的 API：無；其他 API 只作 touched/check-source 閉包，不取得 write scope。

Frontend／BFF／Core／Persistence責任沿唯一Producer。Pure UI/UX可在合法範圍集中修正；API/DTO、資料完整性、Capital/Order/Fill或Authority漂移立即HOLD受影響路徑。

Finding Regression候選：按變更觸發器查既有64筆backlog，不創造無關新任務。

所有測試是規格，尚未實作或執行；原強制Full／Wave-final／Independent Review不能由影響選取免除。

取得有效授權後：Contract → Authorized Coding → Targeted Tests → Integration → Regression → 原Review/Intake/Acceptance → Re-entry。尚缺source assembly、Profile/Adapter、WO/Grant/Budget/Writer等，不能執行。
