# PK10 — 恢復與營運證明

狀態：SPEC_READY（文件可讀）／PLANNING_COMPLETE／QUALIFICATION_PENDING／IMPLEMENTATION_NOT_AUTHORIZED。EXECUTION_READY=false。

Git-only／Private／Historical Restore、Recovery Hold、Health／Audit、Runbook 與部署重建資格。

## 開始閱讀

先讀本包 `ENGINEERING_SPECIFICATION.json`，再依下列 Unit 的 exact source／base plan／v9 companion／model closure／operation spec／fixture／negative oracle；不載無關整體架構。此處每個連結都是規劃文件，不是 Grant。

| Unit | UUID | 實作目的 | 原上游 |
|---|---|---|---|
| [MA13-U06](units/MA13-U06.md) | 93f922ea-3084-498d-aa04-2f7c4b41f497 | Restore A/B/C／Recovery Hold | MA13-U01, MA11-U01, MA12-U01, MA13-U02, MA13-U03, MA13-U04, MA13-U05 |
| [MA16-U04](units/MA16-U04.md) | 5fab7bea-92e7-44b4-a481-9a9f8e5df509 | Health／Audit／Observability | MA16-U01, MA13-U01, MA08-U04, MA13-U05 |
| [MA16-U05](units/MA16-U05.md) | f30d40f9-35c5-476c-9392-7a03a8cf1e1d | Ops Recovery／Security Runbooks | MA16-U01, MA13-U01, MA08-U04, MA08-U05, MA13-U06, MA16-U02, MA16-U04 |
| [MA16-U06](units/MA16-U06.md) | be07a8ab-2efb-43b3-a9de-a9908893b39d | Git-only Program Rebuild／DeploymentQualification | MA16-U01, MA13-U01, MA16-U02, MA16-U03, MA16-U04, MA16-U05, MA13-U06, MA11-U06 |

## 精確操作及驗收

各 Unit JSON 已保留原完整 row/base plan、Feature／Requirement revisions、input/output、API DTO欄位、唯一 Producer／Consumer mode、Mock 原文、negative cases、proposed path/preimage、protected blobs、qualification、具體 postcondition 與 Actual evidence要求。

本包直接負責的 API：getAudit, getHealth

Frontend／BFF／Core／Persistence責任沿唯一Producer。Pure UI/UX可在合法範圍集中修正；API/DTO、資料完整性、Capital/Order/Fill或Authority漂移立即HOLD受影響路徑。

Finding Regression候選：按變更觸發器查既有64筆backlog，不創造無關新任務。

所有測試是規格，尚未實作或執行；原強制Full／Wave-final／Independent Review不能由影響選取免除。

取得有效授權後：Contract → Authorized Coding → Targeted Tests → Integration → Regression → 原Review/Intake/Acceptance → Re-entry。尚缺source assembly、Profile/Adapter、WO/Grant/Budget/Writer等，不能執行。
