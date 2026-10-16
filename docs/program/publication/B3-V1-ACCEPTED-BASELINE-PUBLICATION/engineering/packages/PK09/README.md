# PK09 — OMS、STANDARD PAPER 與 Gateway

狀態：SPEC_READY（文件可讀）／PLANNING_COMPLETE／QUALIFICATION_PENDING／IMPLEMENTATION_NOT_AUTHORIZED。EXECUTION_READY=false。

Send Journal、Order／Fill／Unknown、PAPER STANDARD、Reconciliation／Fresh Re-entry；Shioaji Capability／Adapter 分層。

## 開始閱讀

先讀本包 `ENGINEERING_SPECIFICATION.json`，再依下列 Unit 的 exact source／base plan／v9 companion／model closure／operation spec／fixture／negative oracle；不載無關整體架構。此處每個連結都是規劃文件，不是 Grant。

| Unit | UUID | 實作目的 | 原上游 |
|---|---|---|---|
| [MA08-U01](units/MA08-U01.md) | f4f4e882-c4ab-472e-be9c-4de313d024d5 | Send Journal／UNKNOWN lifecycle | MA07-U01 |
| [MA08-U02](units/MA08-U02.md) | c1d4471a-53a0-47aa-9539-31f920cc69df | OrderEvent／Fill／Cancel race | MA08-U01, MA07-U01 |
| [MA08-U03](units/MA08-U03.md) | 407f7d9c-05a0-4926-9421-b062cc4fde53 | STANDARD PAPER與環境隔離 | MA08-U01, MA07-U01, MA07-U04, MA03-U04 |
| [MA08-U04](units/MA08-U04.md) | e75649b8-6255-49c7-9e1d-58ec44e71b0a | Reconnect／Reconciliation／Hold | MA08-U01, MA07-U01 |
| [MA08-U05](units/MA08-U05.md) | c0ccd521-6c4d-46ad-82c5-a3b5e31f67dc | Fresh Re-entry／Multileg／Kill | MA08-U01, MA07-U01 |
| [MA08-U06](units/MA08-U06.md) | 202b1cf1-aa35-4f14-87cb-d290e6bc19e7 | OMS protocol crash資格矩陣 | MA08-U01, MA07-U01, MA08-U02, MA08-U03, MA08-U04, MA08-U05 |
| [MA09-U01](units/MA09-U01.md) | 2460bd7b-58e9-447e-bdd2-b51e823802d1 | Gateway Capability／SDK profile | MA02-U01, MA08-U01 |
| [MA09-U02](units/MA09-U02.md) | 01061dbc-3f06-4bc5-acc1-1ef93dd2648d | Contract／Account／Unit Mapping | MA09-U01, MA02-U01, MA08-U01 |
| [MA09-U03](units/MA09-U03.md) | 91466dd0-2754-48f1-a6ab-8efbd4c89dfd | Stock／FutOpt native Order adapter | MA09-U01, MA02-U01, MA08-U01 |
| [MA09-U04](units/MA09-U04.md) | f50172c0-079b-483b-ab98-15764bb8068d | Callback Spool／Event Canonicalization | MA09-U01, MA02-U01, MA08-U01 |
| [MA09-U05](units/MA09-U05.md) | 72cdaf5b-3421-4f9a-bef8-8614d07aa6f3 | Query／Session／Reconnect | MA09-U01, MA02-U01, MA08-U01 |
| [MA09-U06](units/MA09-U06.md) | f0b677d7-6a2c-455c-80ca-800525d686be | Shioaji fake/vendor/live資格分層 | MA09-U01, MA02-U01, MA08-U01, MA09-U02, MA09-U03, MA09-U04, MA09-U05 |

## 精確操作及驗收

各 Unit JSON 已保留原完整 row/base plan、Feature／Requirement revisions、input/output、API DTO欄位、唯一 Producer／Consumer mode、Mock 原文、negative cases、proposed path/preimage、protected blobs、qualification、具體 postcondition 與 Actual evidence要求。

本包直接負責的 API：amendOrder, cancelOrder, createOrderIntent, getBrokerCapabilities, getOrder, getRecoveryStatus, getSimulation, listOrders, listReconciliation, pauseSimulation, replaySimulation, resumeSimulation, startSimulation

Frontend／BFF／Core／Persistence責任沿唯一Producer。Pure UI/UX可在合法範圍集中修正；API/DTO、資料完整性、Capital/Order/Fill或Authority漂移立即HOLD受影響路徑。

Finding Regression候選：按變更觸發器查既有64筆backlog，不創造無關新任務。

所有測試是規格，尚未實作或執行；原強制Full／Wave-final／Independent Review不能由影響選取免除。

取得有效授權後：Contract → Authorized Coding → Targeted Tests → Integration → Regression → 原Review/Intake/Acceptance → Re-entry。尚缺source assembly、Profile/Adapter、WO/Grant/Budget/Writer等，不能執行。
