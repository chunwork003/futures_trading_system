# PK08 — 資金歸屬、原子保留與風險准入

狀態：SPEC_READY（文件可讀）／PLANNING_COMPLETE／QUALIFICATION_PENDING／IMPLEMENTATION_NOT_AUTHORIZED。EXECUTION_READY=false。

單帳戶群組、Budget／Actual 分離、共享資本 UoW、Fill Attribution、Decision Cut／Risk／Admission／Kill。

## 開始閱讀

先讀本包 `ENGINEERING_SPECIFICATION.json`，再依下列 Unit 的 exact source／base plan／v9 companion／model closure／operation spec／fixture／negative oracle；不載無關整體架構。此處每個連結都是規劃文件，不是 Grant。

| Unit | UUID | 實作目的 | 原上游 |
|---|---|---|---|
| [MA06-U01](units/MA06-U01.md) | 46af7db1-aace-42c4-9e90-1046f5deb3de | Financial Identity／StrategyGroup Origin | MA02-U01 |
| [MA06-U02](units/MA06-U02.md) | ddc16700-5687-4b64-9110-fb180fe5b60b | Budget與實資金Revision | MA06-U01, MA02-U01, MA06-U03 |
| [MA06-U03](units/MA06-U03.md) | ba31cb9c-7280-486d-bb87-4c876fbeca3c | Shared Capital Reservation transaction | MA06-U01, MA02-U01 |
| [MA06-U04](units/MA06-U04.md) | 210f5fa9-f030-4aab-a156-65f8f340053e | Fill Economics／Attribution UoW | MA06-U01, MA02-U01 |
| [MA06-U05](units/MA06-U05.md) | 7f17ce05-eec2-40d8-9915-267db9c07d6d | Multi-Currency Ledger／Settlement | MA06-U01, MA02-U01 |
| [MA06-U06](units/MA06-U06.md) | 0e93d037-baa6-4c80-8de7-c8a92c128830 | Valuation／Physical-Virtual reconciliation | MA06-U01, MA02-U01, MA06-U02, MA06-U03, MA06-U04, MA06-U05 |
| [MA07-U01](units/MA07-U01.md) | 21acd223-737f-4587-b0d8-928191b687fe | DecisionInputCut完整閉包 | MA06-U01 |
| [MA07-U02](units/MA07-U02.md) | 3e17cc07-98bb-4a34-bf93-3559c70e862c | Group conflict與decision adapter | MA07-U01, MA06-U01 |
| [MA07-U03](units/MA07-U03.md) | 704034d3-4b03-45a9-a26e-7cf723d3aa91 | Asset Risk計量與Policyguards | MA07-U01, MA06-U01 |
| [MA07-U04](units/MA07-U04.md) | 3ea5aaf9-8a64-48ac-adb0-e5b315c8e548 | Library→Runtime Admission | MA07-U01, MA06-U01 |
| [MA07-U05](units/MA07-U05.md) | fc92c842-a14b-493b-9779-c83823027490 | Final Witness與Kill Controls | MA07-U01, MA06-U01 |
| [MA07-U06](units/MA07-U06.md) | 40e58124-2b3f-4086-9111-27f003bd47e1 | Risk跨域並行與逆轉資格 | MA07-U01, MA06-U01, MA07-U02, MA07-U03, MA07-U04, MA07-U05 |

## 精確操作及驗收

各 Unit JSON 已保留原完整 row/base plan、Feature／Requirement revisions、input/output、API DTO欄位、唯一 Producer／Consumer mode、Mock 原文、negative cases、proposed path/preimage、protected blobs、qualification、具體 postcondition 與 Actual evidence要求。

本包直接負責的 API：changeRiskControl, confirmBudgetAllocation, getAccountCapital, getPortfolios, getRiskDecision, listGroups, previewBudgetAllocation, previewRisk, queryAttribution, queryCashFlows, queryPositions, requestDeploymentAdmission, reviseBudget, saveGroup

Frontend／BFF／Core／Persistence責任沿唯一Producer。Pure UI/UX可在合法範圍集中修正；API/DTO、資料完整性、Capital/Order/Fill或Authority漂移立即HOLD受影響路徑。

Finding Regression候選：PRODUCT-S5-01, PRODUCT-S5-02, PRODUCT-S5-03, MA-ARCH-v3-S7-IF02, MA-ARCH-v3-S7-IF03, MA-ARCH-v3-S7-IF04, MA-ARCH-v3-S7-IF05

所有測試是規格，尚未實作或執行；原強制Full／Wave-final／Independent Review不能由影響選取免除。

取得有效授權後：Contract → Authorized Coding → Targeted Tests → Integration → Regression → 原Review/Intake/Acceptance → Re-entry。尚缺source assembly、Profile/Adapter、WO/Grant/Budget/Writer等，不能執行。
