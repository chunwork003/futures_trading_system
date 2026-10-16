# PK04 — 私人 Capture、備份與部署基礎

狀態：SPEC_READY（文件可讀）／PLANNING_COMPLETE／QUALIFICATION_PENDING／IMPLEMENTATION_NOT_AUTHORIZED。EXECUTION_READY=false。

私人原文 Capture／Readback、Provider／Volume／Path、Same-Cut／A-B Catalog；配置、版本與 Migration Plan。

## 開始閱讀

先讀本包 `ENGINEERING_SPECIFICATION.json`，再依下列 Unit 的 exact source／base plan／v9 companion／model closure／operation spec／fixture／negative oracle；不載無關整體架構。此處每個連結都是規劃文件，不是 Grant。

| Unit | UUID | 實作目的 | 原上游 |
|---|---|---|---|
| [MA13-U01](units/MA13-U01.md) | 8127078d-3263-47d4-a1c5-59390da7224d | Critical Artifact Capture／Availability | MA11-U01, MA12-U01 |
| [MA13-U02](units/MA13-U02.md) | edf14ff8-839f-44f4-a1b0-166c024f1515 | Provider／Volume／Path／Encryption | MA13-U01, MA11-U01, MA12-U01 |
| [MA13-U03](units/MA13-U03.md) | 2049e68d-c38a-459f-a0d1-f1df2eda8299 | SQL Dump／Artifact Same-Cut Set | MA13-U01, MA11-U01, MA12-U01 |
| [MA13-U04](units/MA13-U04.md) | ddb418b7-65aa-4166-8b9f-e61ba66e6268 | A Incremental／B Independent Retention | MA13-U01, MA11-U01, MA12-U01 |
| [MA13-U05](units/MA13-U05.md) | 7dda8b7f-82d2-46d4-b6c5-7e0c960d0e64 | External Catalog／Historical／Trust | MA13-U01, MA11-U01, MA12-U01 |
| [MA16-U01](units/MA16-U01.md) | a74efbae-fd8d-4684-ab41-2d769263f5d8 | DeploymentManifest／Toolchain Pins | MA13-U01 |
| [MA16-U02](units/MA16-U02.md) | 417a48ca-cd02-4682-8099-6b22cb9347d6 | Config／Auth／Environment isolation | MA16-U01, MA13-U01 |
| [MA16-U03](units/MA16-U03.md) | ffcf094e-f8ac-4ea4-b8b0-45e90063d3cc | Migration Plan／Expand Adapter／Rollback | MA16-U01, MA13-U01 |

## 精確操作及驗收

各 Unit JSON 已保留原完整 row/base plan、Feature／Requirement revisions、input/output、API DTO欄位、唯一 Producer／Consumer mode、Mock 原文、negative cases、proposed path/preimage、protected blobs、qualification、具體 postcondition 與 Actual evidence要求。

本包直接負責的 API：getArtifactBytes, getArtifactContent, getBackupCatalog, getConfig, listArtifacts, saveConfigCandidate

Frontend／BFF／Core／Persistence責任沿唯一Producer。Pure UI/UX可在合法範圍集中修正；API/DTO、資料完整性、Capital/Order/Fill或Authority漂移立即HOLD受影響路徑。

Finding Regression候選：F3-04, F4-01, F4-02, F4-03, F4-04, F4-05, F5-02, F6-06, F2-06, F4-06, F5-01, F5-03, F5-04, F5-05, F5-06, F5-07, F5-08, F6-07, S6-COV-01, PRODUCT-S4-01, PRODUCT-S4-02, PRODUCT-S4-03, PRODUCT-S4-04, PRODUCT-S4-05, PRODUCT-S4-06

所有測試是規格，尚未實作或執行；原強制Full／Wave-final／Independent Review不能由影響選取免除。

取得有效授權後：Contract → Authorized Coding → Targeted Tests → Integration → Regression → 原Review/Intake/Acceptance → Re-entry。尚缺source assembly、Profile/Adapter、WO/Grant/Budget/Writer等，不能執行。
