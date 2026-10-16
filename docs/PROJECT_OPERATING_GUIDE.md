# Project Operating Guide — B3 V1 穩定工程SOP入口

版本：`accepted-entry.v1`。Human雙項採納已批准並於本機物化；此SOP是有效政策的導航與有界摘要，不建立第二套Current State、Compiler、Controller、Progress Engine或Acceptance Owner。

依 [Owner Receipt](<D:/00_Learn/量化交易/Code/futures_trading_system/docs/program/decisions/B3-V1-DUAL-ADOPTION-20261015-v1.owner.v1.json>) 及 [B3 Accepted Baseline](<D:/00_Learn/量化交易/Code/futures_trading_system/docs/architecture/adopted/B3_V1_ACCEPTED_BASELINE.v1.json>) 採納：

| 必須共同閱讀的政策來源 | 原始raw SHA256 |
|---|---|
| [原Guide v2精確副本](<D:/00_Learn/量化交易/Code/futures_trading_system/docs/architecture/adopted/B3_V1_PROJECT_OPERATING_GUIDE.source.v2.md>) | `dae411b42acba4471307d6291b93c3df7e5f5bb5293ee8b202328e72661803ba` |
| [C01～C07必要附件精確副本](<D:/00_Learn/量化交易/Code/futures_trading_system/docs/architecture/adopted/GUIDE_V2_COMPATIBILITY_ANNEX.source.v1.md>) | `a83fb8c9c79f447349892da7bae0dc6fdbff675e7a6712ac868b0b86ba414f82` |

原文candidate/pending標籤是不可變歷史正文；本次外部Human Receipt建立相同bytes的正式政策採納，不覆寫舊狀態或假用原Hash代表新正文。本入口自己的bytes／Hash與原Guide分開記錄。

## 每次工作先重進入

`AGENTS.md → docs/CURRENT_STATE.md → automation/governance/master_manifest.v1.yaml與active machine policies → docs/CURRENT_WORK.md → 最新handoff/delta/result/review/STOP`。原治理仍是Current／授權／生命週期的唯一責任；本SOP不複製動態NEXT、Quota或Writer狀態。

## 固定責任與可替換工具

Architecture／Contract Ownership、WORK Planning／Orchestration／Intake／Cost、Implementation、Integration、Independent Review、Human Acceptance責任固定，工具不永久綁前後端。CODEX Sol6.1 High為目前主要Coding路線；合格VS Code＋Human＋GPT／LM可依原WORK能力、成本及Quota政策替代。切換保持同Unit／Source／Revision／AllowedScope／Test Oracle／Evidence／成本lineage；先有durable checkpoint與合法writer／grant／capacity再驗，不重派consumed grant，不重置身份／進度。原研究Local LM權限不變成Coding Writer。

## Contract-First與Writer

跨層責任：`React → ASP.NET BFF → Python API → Quant／Trading Core → Persistence`。施工前固定同Unit、API Operation、UI、DTO／Schema／Revision／SourceHash、唯一Producer、Auth／Error／Retry／Idempotency／CAS／Unknown、Mock Oracle／Fixtures、Contract Tests與Integration條件。Mock不能另造業務語義或繞BFF。

當前維持global single writer、NO_PARALLEL_EXECUTION、same_execution_multi_executor DENIED。不同工具／Branch／Worktree不提供並行權；未來多Writer要由原Owner採納並qualification的scoped successor，明定互斥scope、共享Contract／Migration序列、Lease／CAS／撤權／Crash／Unknown／Resume。沒有該資格就由原WORK序列施工，不新建第二個調度器。

## 交付、檢核與永久Regression

MVP→Normal Development→Complete B3 V1；MVP僅內部垂直里程碑，不減少完整B3義務。L1～L4是B3_CHANGE_RISK顯示映射，不改AGENTS層級或closed enums；資金／身份／Order／Fill／Source／Authority Consumer按真實影響升級。原明定Full／Wave-final Regression與Independent Review不因影響選取而免除。

沿用原Finding ID及64筆既有crosswalk：Finding→RootCause→Counterexample→Correction→Test→Trigger→Gate→Run/Evidence。真正有執行證據才PASS；沒有則NOT_RUN／UNVERIFIED／MANUAL_OR_ENVIRONMENT_GATE。按影響選檢查，不把工具全數未實作當所有低風險工作的總阻斷，也不放行依賴必要高風險防線的變更。

## 採納不等執行；CodeComplete後重整另授權

本次Human批准的是B3設計與Guide政策，不是P00 Closure、正式Compiler qualification、Work Order／Dispatch、SQL／Restore／Broker／Runtime／Controller／Release。工作包需要逐項合法依賴、current authority及具名Gate。

完整B3 V1_CODE_COMPLETE才觸發獨立全面重整提案；現在可唯讀Inventory／Map準備，不能先搬資料。首個異動前已有授權、單Writer、保全、Dry-run與批准Rollback；完成後驗Build／Regression／E2E／FreshReview／回退覆蓋，再進Release。未引用不等可刪；歷史bytes/path/hash/receipt與不可再生私有原文保護。main/master整合、SQL／Artifact移動及Git發布另授權。
