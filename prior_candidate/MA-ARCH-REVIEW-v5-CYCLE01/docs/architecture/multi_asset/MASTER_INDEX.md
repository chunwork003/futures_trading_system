# Multi-Asset Architecture — 統一候選交付索引

版本 `MA-ARCH-CANDIDATE-1`；Review Bundle successor `v4-RCG01-06`；Owner = existing Principal Architect；狀態 `COHESIVE_CORRECTION_COMPLETED_PENDING_INDEPENDENT_RE_REVIEW`。本索引是既有 `docs/V1_SYSTEM_BLUEPRINT.md` 的版本化擴充候選入口，沒有取代正式 Architecture／CURRENT／WORK／Acceptance Authority。

## 權威、來源與本次目的

正式 Git 分支為 `master`。2026-10-11 已重新核對 GitHub default branch 與遠端 HEAD 為 master@`9b5ab5fdd98744a7db45ec9f14b64ef1f324920f`；本機 master 同 SHA。架構作者工作樹仍在 `architecture/p00-v1-baseline`@`2634717b1443eb95fa0fde4d5d987347ef2160e8`；其六筆超前提交沒有合併或發布。原 main@`0cb0283b8c5f795f8da1672575cbb674945db73a` 原樣保存。

最新直接Human來源為本輪RCG01–06修正授權的具名條款捕捉（private_source_capture/OWNER_RCG_CORRECTION_20261012.md），取代先前candidate路由／長期主線方向：long-term main、B3完整LAB、CODEXSol6.1High主要Coding。2026-10-11 OWNER_FULL_PROGRAM仍是完整多資產產品來源前身，舊LM-first不作最新執行政策；明列selected-clause capture不是完整message export或正式採納Receipt。

已有正式來源、原始 LAB／URMS 需求及 STEP 1–7 完整原審查訊息先保全，再建立 Source-Bound Delta。原 accepted R01／R03／R04／R05／R07、ADR-001、GAP08 bounded closure 與 Program V2 preserved；R02／R06／R08 與 C3→C5→C6 不因本候選自動結案。

## 章節目錄與唯一責任

| ID | 章節 | 實作語義 Owner／正式前身 |
|---|---|---|
| MA01 | [範圍、來源、Authority](01_SCOPE_SOURCE_AUTHORITY.md) | Architect／Human／R05／R08；原 Roadmap／Blueprint |
| MA02 | [多資產 Domain](02_ASSET_DOMAIN.md) | Reference Data／D；accepted contract identity adapter |
| MA03 | [Market Data](03_MARKET_DATA.md) | B／C／D；MarketObservation、dataset contracts |
| MA04 | [Research & Strategy Lab](04_RESEARCH_STRATEGY_LAB.md) | E／F；Rev2／Rev3、existing strategy／backtest |
| MA05 | [Portfolio／Macro／Rate Lab](05_PORTFOLIO_MACRO_RATE_LAB.md) | E／F research；G/J 的唯讀輸入 |
| MA06 | [Portfolio／Capital／Accounting](06_PORTFOLIO_CAPITAL_ACCOUNTING.md) | G／J／K；account UoW、不可變歸屬 |
| MA07 | [Decision／Risk](07_DECISION_RISK.md) | G；Multi-Strategy Decision Layer、risk gates |
| MA08 | [OMS／PAPER／LIVE](08_OMS_PAPER_LIVE.md) | H／J／K；accepted execution／recovery |
| MA09 | [Broker／Shioaji](09_BROKER_SHIOAJI.md) | I；broker-neutral port＋具體 adapter |
| MA10 | [Web UI／API](10_WEB_UI_API.md) | L／M／N；existing BFF／DTO adapters |
| MA11 | [URMS Identity／Relations](11_URMS_IDENTITY_RELATIONS.md) | existing Registry／R05；雙樹、正規化代碼 |
| MA12 | [Git／SQL／Artifact Publication](12_PUBLICATION_AUTHORITY.md) | existing Reviewer／Intake／Publisher／Importer |
| MA13 | [Storage／Recovery／Security](13_STORAGE_RECOVERY_SECURITY.md) | O／K／Security；A/B、可驗證恢復 Cut |
| MA14 | [Engineering Execution](14_ENGINEERING_EXECUTION.md) | existing WORK／Compiler／R07；有界路由 successor |
| MA15 | [Integration／Acceptance](15_INTEGRATION_ACCEPTANCE.md) | original Domain Owners／Independent Reviewer |
| MA16 | [Deployment／Operations](16_DEPLOYMENT_OPERATIONS.md) | L／O；環境、版本、安裝與復原 |

每章固定 `candidate.4`，完成後與 machine companion 一起以 exact byte hashes 綁定。章節進度與恢復位置見 [DESIGN_STATE.json](DESIGN_STATE.json)，這是作者的設計工作狀態，不是新的 WORK Scheduler、accepted progress 或 canonical operational CURRENT。

## 共用設計契約

1. 物件永久身份與 revision、public code、alias 分開；引用 `ContractRef={entity_id,revision_id,owner,source_hash}`。Source hash 必須標 byte／semantic domain。既有 integer trading identity 經 immutable mapping 保留，禁止大改舊 constructor。
2. 環境 LAB／PAPER／LIVE 是命令、account、deployment、events、permissions、secret provider、storage partition 的必要 scope，缺失一律拒絕。環境不是畫面標籤。
3. Financial Account 不等於 Operator Login Identity；Draft／Artifact publication／Library Approval／Runtime Admission 分開。
4. Operational Decimal 固定點字串＋currency／unit；UTC instant、exchange trading date、sequence／revision 不混用。Unknown 不能變成 0、empty、FLAT 或 ACCEPTED。
5. Append-only revision／event／receipt；mutable head 使用 generation CAS。Idempotency scope 和 payload hash 固定，同 ID 異內容 conflict；timeout 先 query receipt，不能盲重送經濟動作。
6. Economic Fill／position／cash truth 維持 accepted G/H/J/K owners；SQL／UI／URMS 只保存或投影，不能接管它們的決策與 Acceptance。
7. source、接口、budget、weight、Acceptance 不因切換 executor 或拆成 N units 而重置。所有 units authority=DESIGN_ONLY，後續施工必須編譯合法工作單。
8. 候選新 API 使用 `/api/v2/`；v1 契約與 closed schemas 保護。Consumer migration 走 versioned companion／adapter，禁止暗改 enum 或 constructor。

## 設計狀態與審查屏障

`DESIGN_DRAFTED → AUTHOR_CHECKED → INDEPENDENTLY_REVIEWED → OWNER_ACCEPTED → IMPLEMENTATION_AUTHORIZED → RUNTIME_QUALIFIED → RELEASE_READY` 各軸分開。文件檢查、model simulation、真實 PostgreSQL／filesystem／Broker／restore 測試不得互相冒充。

全部已確認需求必須在 Requirement Registry 中有永久 candidate ID、source、Owner、reuse/delta、release scope、dependencies、design／implementation status、Acceptance Gate。歷史92/603/2137、26/113、37/127 各自保持原 revision；本次新增需求沒有新總權重或產品百分比。

完整架構就緒還需要 exact source binding、完整章節與跨章節接口、客觀 unit contracts、immutable review bundle、open findings／remaining qualification matrix，以及真實來源保全證據。不存在 source 或測試時，明列受影響 Gate，不宣稱整體 ready。

## Machine／契約／持久交付

| 入口 | 實際內容／用途 |
|---|---|
| [SOURCE_MANIFEST.json](SOURCE_MANIFEST.json)／[SOURCE_DECISION_LEDGER.json](SOURCE_DECISION_LEDGER.json) | 91 source bindings，75 Git blobs本輪raw bytes重新核對；16 private captures，Owner來源與接受前身分開 |
| [REQUIREMENT_REGISTRY.json](REQUIREMENT_REGISTRY.json)／[SOURCE_COVERAGE_CROSSWALK.json](SOURCE_COVERAGE_CROSSWALK.json) | 87新增原子需求、92cap、603leaves、13M／13P、24GAP、8原LABwave、8P00streams；source→feature→chapter→unit |
| [ROADMAP_RELEASE_CROSSWALK.json](ROADMAP_RELEASE_CROSSWALK.json) | source-bound phase mappings、三項reverse修正、FinancialAccount/login分離、完整scope及first usable slice、獨立分母 |
| [MODEL_CATALOG.json](MODEL_CATALOG.json)／[TYPE_VARIANTS.json](TYPE_VARIANTS.json) | logical/wire models、typed asset variants/enums、plan/runtime DTO分離 |
| [API_CATALOG.json](API_CATALOG.json)／[EVENT_CATALOG.json](EVENT_CATALOG.json)／[CROSS_CHAPTER_CONTRACTS.json](CROSS_CHAPTER_CONTRACTS.json) | 65 API、34event、12critical interfaces；19UI頁，exactmodel/cardinality/owner/error/gates |
| [LOGICAL_SCHEMA_CONTRACT.md](LOGICAL_SCHEMA_CONTRACT.md)／[CONTRACT_INVARIANTS.md](CONTRACT_INVARIANTS.md) | 3NF/FK/unique/immutableversions/wholegraphCAS、hashdomain／backupclosure／重複欄位約束；無DDL |
| [ALGORITHM_AND_SERVICE_CONTRACTS.md](ALGORITHM_AND_SERVICE_CONTRACTS.md)／[MONEY_SUBMISSION_CUT_PROTOCOL.md](MONEY_SUBMISSION_CUT_PROTOCOL.md) | 資產估值/研究方法／service責任、預留C0→C1→C2、externalfill／sealedterminal／repricing／nointernalmatch |
| [IDENTITY_REGISTRY.candidate.v1.json](IDENTITY_REGISTRY.candidate.v1.json)／[CODE_ALIAS_REGISTRY.candidate.v1.json](CODE_ALIAS_REGISTRY.candidate.v1.json)／[RELATION_RULES.json](RELATION_RULES.json) | permanent candidate IDs、927normalized code/alias records、scopedC01、dual-tree typedrelations，不替換歷史WO/EXEC/Evidence IDs |
| [GIT_REGISTRY_REBUILD.candidate.v1.json](GIT_REGISTRY_REBUILD.candidate.v1.json) | 正式採納前的Git Registry rebuild contract/sample；same-ID／relations／codes／private missing；不是已發布Registry |
| [EXECUTION_UNITS.json](EXECUTION_UNITS.json)／[EXECUTION_UNIT_PLAN_SCHEMA.json](EXECUTION_UNIT_PLAN_SCHEMA.json)／[EXECUTION_UNIT_COMPILER_ADAPTER.md](EXECUTION_UNIT_COMPILER_ADAPTER.md) | 96logical plans、18fields、exactsource/companion bindings、existingWORK唯一compiler adapter；不是96份施工授權 |
| [FINDING_LEDGER.json](FINDING_LEDGER.json)／[FINDING_DISPOSITION.json](FINDING_DISPOSITION.json) | 40原finding exact原文/source lineage，CG1–6cohesivecontracts；不自行關閉 |
| [AUTHOR_CHECKS.json](AUTHOR_CHECKS.json)／[REMAINING_QUALIFICATION_MATRIX.json](REMAINING_QUALIFICATION_MATRIX.json) | 真正已做source/modelchecks與20剩餘Gate；SQL／Broker／Windows／Restore皆NOT_RUN |
| [GATE_AND_EXECUTION_PLAN.md](GATE_AND_EXECUTION_PLAN.md)／[REVIEWER_HANDOFF.md](REVIEWER_HANDOFF.md) | C3→C5→C6、LaneA–E、exact reviewer入口，formaladoption與後續WO分開 |

S14/S15三本原始活頁簿已read-only取得並hash/cell capture；original baseline及後續research candidates保存於私有source witness。依最新Owner只屬FuturePortfolioResearchLab，不改原acceptedmainline。原始聊天message-level全文／最初日期尚未取得；Excel建立metadata本輪為2026-10-11，不能充當2026-10-02訊息證據。

## 下一個合法工作

16章及machinecompanion均已實際保存，v1/v2隔離來源審查的修正已形成v3精確候選；44項作者來源／模型一致性檢查完成。接續原流程formal Fresh Independent Review exact S1–S9 subjects；沒有單章Owner確認屏障，也不假設聊天結束後背景自動繼續。

完成作者一致性檢核後，交 fresh isolated Independent Reviewer，原 P00 C3/C5/C6 與新增多資產 Scope Adoption 分別進行。此索引不能啟動 Coding、SQL、migration、LIVE、controller 或 Git publication。

## v3 新增精確 companion 與完成狀態

[ECONOMIC_RESOURCE_CONTRACTS.md](ECONOMIC_RESOURCE_CONTRACTS.md) 固定 lot／entitlement／settlement 與原 economic writer；[REGISTRY_EXPORT_ADAPTER.md](REGISTRY_EXPORT_ADAPTER.md) 固定檔案與 wire adapter、typed code validity／catalog／policy、267 dependencies。候選含108 logical/wire models、77 structs、65 API、34events、12跨章契約、19頁、96 plans及1630 typed relations；不等於同數量SQL表或Work Orders。

[READINESS_CHECKLIST.json](READINESS_CHECKLIST.json) 為12項候選交付標準的客觀入口。[FRESH_INDEPENDENT_REVIEW_PROMPT.md](FRESH_INDEPENDENT_REVIEW_PROMPT.md) 可直接複製交付原流程指定Reviewer。[ISOLATED_REVIEW_FINDINGS.json](ISOLATED_REVIEW_FINDINGS.json) 留原18項及v2新窄範圍缺口的來源修訂軌跡；v3不是正式獨立接受。

目前沒有需另問產品方向才能繼續設計的重大未決事項；formalreview、原P00 C3/C5/C6、新scope/Registry/policy採納、publicpublication審核與合法執行授權仍各別未完成。S14原聊天日期來源限制及實際runtime資格均明列，不是全部產品架構的停止條件。


## RCG01 candidate.4 source-bound successor

Currentformal/default仍master；Human長期main目標與受控雙歷史遷移PLANNED_NOT_EXECUTED見[MAIN_MASTER_MIGRATION_CONTRACT.md](MAIN_MASTER_MIGRATION_CONTRACT.md)。最新完整B3要求以[B3_RELEASE_SLICE.json](B3_RELEASE_SLICE.json) exact requiredset為準，包含OOS/WFO/MC/benchmark/ablation/AIAnalyst，不採舊薄firstslice。CODEXSol6.1High主要Coding、GPT+VSCode/LMquotafallback見../ENGINEERING_EXECUTION_POLICY.candidate.v3.md；旧政策與原接受source保留。舊段落只表示priorcandidate/historicalsource，不可拿來覆蓋此source-boundcurrent/target successor。原P00C3→C5→C6、0/8、所有runtime與發布授權不變。


## RCG01–06 fixed successor delivery

Exactsubject `MA-ARCH-REVIEW-v4-RCG01-06`。原65API保留，30必要增補→95；149models／139structs／40events；16chapters／19UI／96units永久ID不變。前輪freshHOLD及全部finding保留；FIXED_CANDIDATE只是原作者修正提案。MASTER_INDEX是候選navigation，不是正式CURRENT或第二WORK。最新唯一完整輸出與exact re-review envelope由isolatedcorrectionworkspace reports/提供，不把舊v3進度或44check當新結論。


## Candidate.5 bounded loop successor

Exact Subject: `MA-ARCH-REVIEW-v5-CYCLE01`. 16 chapters /19 UI /95 stable API operation IDs /96 stable Unit IDs. 五個共同根因，沒有新Work/Controller/Progress/Acceptance Owner。

- `BODY_CAPTURE_READBACK_CONTRACTS.md`
- `BODY_SOURCE_ROW_SCHEMAS.candidate.v5.json`
- `BODY_TYPE_CATALOG.candidate.v5.json`
- `CAPITAL_TRANSPORT_VERSIONED_ADDENDUM.candidate.5.md`
- `CC03_CC05_GOLDEN_FIXTURES.candidate.5.json`
- `EXECUTION_UNIT_COMPILER_ADAPTER_ADDENDUM.candidate.v5.md`
- `OPERATION_EXPECTED_MODEL_ORACLES.candidate.v5.json`
- `OPERATION_PRODUCER_CONSUMER_MAP.candidate.v5.json`
- `REVISION_HISTORY_REPAIR.candidate.5.md`
