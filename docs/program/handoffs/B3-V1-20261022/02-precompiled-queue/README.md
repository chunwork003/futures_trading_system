# B3 V1 預編工作佇列與延後審查補充

Subject：`ULTRA-B3-PRECOMPILED-QUEUE-ADDENDUM-V1`。

**總裁決：`DESIGN_COMPLETE_PENDING_AUTHORITY`。** `PRECOMPILED_QUEUE_READY=true` 僅表示 96 張來源綁定施工規格已備妥，不表示 96 張 native WO／有效 Grant 已存在。這是已凍結 B3 的導航補充，不是新的 Architecture Review、Program、Machine State、Compiler 或 Controller。

## 實際完成

- `unit_specs/` 已有 **96 張**真實 Unit 預編 JSON；保留完整 immutable 原契約 value、UUID／Revision／Source Hash、原需求／依賴、實作範圍、完整 Consumer／DTO／Schema／Producer／Consumer／UI、允許路徑提案與保護範圍、所有 required test IDs／positive／negative、Qualification、Review、cost／evidence／recovery及下一個候選。
- Index 先排 **57 張 MVP**，仍為 `MA10-U06` 的 **184 條依賴／11 Waves**；再排完整 B3 其餘 39 張。整體 **12 Packages／96 Units／364 Edges／95 API／19 UI／578 Consumer** 不變。
- 原六份交接文件 Hash 全保留，僅用 `SIX_FILE_SUPPLEMENT_MAP.json` 指向本補充；不覆寫原件，不建立另一份 CURRENT_STATE。
- 六個獨立 Expected／Actual Mock 情境 **6 passed／0 failed／0 errors／0 skipped**。僅為離線合成模型；沒有產品 Coding、正式 Compiler／Qualification、Grant、Writer、Git、SQL 或 Controller 效果。
- 實際 Deferred Product Review entries **0**；這次沒有新產品結果，不製造虛構待審／執行紀錄。原 Accepted Units 維持 **1／96**。

## 現行政策限制與最小處置

`development_entry_protocol.v2.yaml:18–28` 的 unfinished／pending-review 優先、`CODEX_EXECUTOR_KERNEL.md:168` 的 Review Barrier，以及 `AGENTS.md:234–240` 的每 autonomous run 單 mainline Package，均仍有效。沒有現成的一般「Reviewer 缺席即可開始另一張」放行權；候選 Worktree 與下一張 Grant 也不能默默覆寫政策。

本設計預設保留 fail-closed：可登錄 PENDING、保存證據、做不需新執行權的唯讀分析和候選編製；真正新施工仍先符合現行 Gate。若需要結果固定後、已釋放 Writer 的 pending Review 項目不阻擋精確不相依工作，先走 `MINIMUM_POLICY_DECISION_REQUEST.json` 的限定 successor／Review／Owner Decision，不能現在啟用。它不涉及重開 B3、不放行未審高風險上游、不把任何 pending 改 PASS。

Lane A 逐單 native Grant；Lane B 另有明確 candidate 開發授權、受支持政策／Profile、隔離 Allowlist與同一全域 Writer。沒有適用權限只有非實作準備。未審上游不能成為正式 Accepted Dependency；191 source-only 關聯不是新 DAG 邊。

## 入口與使用順序

| 檔案 | 用途 |
|---|---|
| `ADDENDUM_MANIFEST.json` | 固定本包所有檔案／Hash；self-excluded，避免循環 Hash |
| `PRECOMPILED_WORK_QUEUE.index.json` | 96張規格、57 MVP priority、原364 edges、精確身份與spec Hash |
| `PRECOMPILED_MVP_ROUTE.json` | 57／184／11、結構Frontier、完整B3後續39張；actual executable frontier為空 |
| `unit_specs/MAxx-Uxx.spec.json` | 當次 Unit 所需原契約、Source Closure、interfaces、tests、權限／資格差額；不是 native WO |
| `GENERATOR_AND_REVIEW_PROTOCOL.md` | 投影器對既有WORK/native schema的分工、Lane A/B、Review Gate、impact及成本契約 |
| `VS_CODE_CONTINUOUS_CODING_KERNEL.md` | 可直接複製的新對話／持續接單 Prompt |
| `DEFERRED_REVIEW_LEDGER.json` | 原生review的衍生觀察及未填入實際紀錄的template |
| `REVIEW_DEPENDENCY_IMPACT.json` | 96節點的direct/transitive/interface exposure與補審排序／重驗規則 |
| `ULTRA_CATCHUP_REVIEW_PROMPT.md` | 共享前置優先、風險排序、Cohesive Batch、精確Source再驗證與失敗影響 |
| `POC_CONTRACT.json`、`poc/POC_RESULTS.json` | 先固定的6個Expected、實際Actual／時間／工具／結果與限制 |
| `INPUT_SOURCE_WITNESS.json`、`DURABLE_CHECKPOINT.json` | 開始Source／Git現場與最終恢復／未完Gate |

新對話先沿 AGENTS／CURRENT_STATE／manifest／policies／CURRENT_WORK／latest unfinished result review STOP，再核本包 Manifest 與當選 Unit。只按必要完整 source／companion／reverse closure 讀取，不把整個 96-spec 資料集塞入 Context；也不可截斷原 semantic obligations 或假稱符合未變更的 128 KiB Gate。

`BUILD_SPEC_PROJECTION.py --verify` 可唯讀重驗投影。它只做文件 currentness／bytes／身份／DAG／case mapping 比對，不是 Source／Context／Result／Intake qualification。`--build` 只供尚未存在的新隔離投影，不重寫凍結內容；中斷優先從本包 Checkpoint＋原native state恢復，不重派既有Execution。

## 驗證與失敗紀錄

所有96張spec精確重建 byte 比對通過；原 Source Body／Revision／入邊、578 Consumer四種角色及 required case IDs 保留。六個PoC的Expected先獨立寫入 `POC_CONTRACT.json`，不是從 Actual selector反向生成。

第一次投影 verifier 在 Index 失敗，原因是 Python edge tuple 與 JSON edge list 的比較，不是 Source Drift。修正為**更嚴格的 deterministic UTF-8 bytes 比較**後通過，原96張spec／Index未改；失敗與修正紀錄保存在 `AUTHOR_VALIDATION_FAILURES.json`。不隱藏初次失敗，也不把作者檢查冒充正式 Independent Review。

P3 同時保存 current-policy拒絕與明示 `PROPOSED_NOT_ACTIVE` 的未來政策fixture。後者通過不代表政策已生效。模型缺席不等於結果通過，不代表一般 Worker 或 LM 已取得使用資格。

## 下一個合法工作與 Human Gate

可由一般 WORK／VS Code 現在接手：讀取 Source、挑選已授權候選、編製 native WO／Source Assembly／Qualification差額與 finite Budget、整理真實 Review Evidence及依賴影響。首個 MVP 準備候選為 **MA02-U01**，U01 Accepted上游須精確讀回；U02限定資格與QF01支線不自動轉授或阻擋此MVP DAG。

尚不可 Coding：未有 MA02-U01 專屬使用資格／新 Grant／Writer；即使未來有 Grant，也必須通過其適用 Source／Context／Result／Intake／Budget／review barrier 等條件。完整96個規格不等於96張正式授權。原 C3 NOT_QUALIFIED、C5 未授權／未執行、C6 待 Human、P00 0/8及 runtime Gate不變。

下一個與本次「Review Deferred 時持續施工」直接相關的最小決策，是**是否接受並進入限定 deferred-review continuation policy successor 的正式審查／採納程序**，不是核准產品 Coding。申請的精確來源、限制與固定檔在 `MINIMUM_POLICY_DECISION_REQUEST.json`。若不採納此補充，仍可用現有合格替代Reviewer完成原強制Review後逐單施工；不是必須等待Ultra。

Git Publication／Qualification／產品或候選Coding均另有精確權限，未由本包代授。正式 Git 發布前還需私密／Secrets／Allowlist／來源可逆承載／Git Baseline檢查；本包留在本機隔離目錄。完整 Repository重整仍待 B3 Code Complete與另行授權。

## Ultra 收尾

Ultra 不再負責每日96張工作單重拆。普通工作由合格工具按原制度執行，必要 Unit Review交獨立合格Reviewer；高階模型只處理完整R1/R2/R3 Stage Review、Catch-up Batch與新重大架構／Authority／安全矛盾。沒有必要新增控制器；本包明確不啟用自動化執行。
