# PK07 — Portfolio／Macro 研究與歷史界線

狀態：SPEC_READY（文件可讀）／PLANNING_COMPLETE／QUALIFICATION_PENDING／IMPLEMENTATION_NOT_AUTHORIZED。EXECUTION_READY=false。

一般 Portfolio／Macro／利率情境與成本研究；保留 S14／S15 原始 Lineage，禁止研究條件升格交易准入。

## 開始閱讀

先讀本包 `ENGINEERING_SPECIFICATION.json`，再依下列 Unit 的 exact source／base plan／v9 companion／model closure／operation spec／fixture／negative oracle；不載無關整體架構。此處每個連結都是規劃文件，不是 Grant。

| Unit | UUID | 實作目的 | 原上游 |
|---|---|---|---|
| [MA05-U01](units/MA05-U01.md) | 2f7b9a7e-93eb-4f7a-a8c8-40c117209a0a | 原始Workbook Capture與Lineage | MA04-U01 |
| [MA05-U02](units/MA05-U02.md) | ee90d221-1760-4f91-b1c1-15315ab6e72b | PortfolioResearch weights／rebalance | MA05-U01, MA04-U01 |
| [MA05-U03](units/MA05-U03.md) | dd14d07c-7b22-4915-bf83-5366df74f34d | Macro Vintage／Interest Curve | MA05-U01, MA04-U01 |
| [MA05-U04](units/MA05-U04.md) | 86028405-7982-4b79-9413-6bcf4abd2776 | Stage／Scenario／Stress models | MA05-U01, MA04-U01 |
| [MA05-U05](units/MA05-U05.md) | 09eade78-0341-48b0-8d74-ba544f389675 | Cost／Cashflow／Grid Search metrics | MA05-U01, MA04-U01 |
| [MA05-U06](units/MA05-U06.md) | 262a192c-01ba-4b5c-ad9b-500a8a3e4090 | Future S14／S15與通用Lab隔離 | MA05-U01, MA04-U01, MA05-U02, MA05-U03, MA05-U04, MA05-U05 |

## 精確操作及驗收

各 Unit JSON 已保留原完整 row/base plan、Feature／Requirement revisions、input/output、API DTO欄位、唯一 Producer／Consumer mode、Mock 原文、negative cases、proposed path/preimage、protected blobs、qualification、具體 postcondition 與 Actual evidence要求。

本包直接負責的 API：createScenarioRun, listPortfolioResearch, queryMacroSnapshots, savePortfolioResearch

Frontend／BFF／Core／Persistence責任沿唯一Producer。Pure UI/UX可在合法範圍集中修正；API/DTO、資料完整性、Capital/Order/Fill或Authority漂移立即HOLD受影響路徑。

Finding Regression候選：按變更觸發器查既有64筆backlog，不創造無關新任務。

所有測試是規格，尚未實作或執行；原強制Full／Wave-final／Independent Review不能由影響選取免除。

取得有效授權後：Contract → Authorized Coding → Targeted Tests → Integration → Regression → 原Review/Intake/Acceptance → Re-entry。尚缺source assembly、Profile/Adapter、WO/Grant/Budget/Writer等，不能執行。
