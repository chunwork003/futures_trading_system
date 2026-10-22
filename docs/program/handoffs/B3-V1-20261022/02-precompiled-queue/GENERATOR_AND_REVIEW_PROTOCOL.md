# 預編規格、接單與待審影響契約

狀態：設計候選／無執行效果。Lane A、Lane B、PENDING、R0～R3 與本補充標籤均非新 Machine State。原 CURRENT_STATE、Program V2、WORK、單 Writer、Review／Intake／Acceptance 繼續是唯一權威。

## 原始來源與 Generator

沿用 `automation/work_orders/planning/B3-V1-12-PACKAGES.inputs.candidate.v1.json#/unit_compilation_inputs/<alias>`，不是重寫 96 份 B3 設計。每張規格保存整份原 Unit 契約 value、其 raw source＋JSON Pointer＋canonical body Hash，以及已閉合 B-TRACE-01 的完整 effective Consumer rows。13 張受影響摘要另外保留其 `affected_unit_companions/<i>/after`；其餘 83 張沿用原契約，578 mappings 不截成 primary IO 摘要。

`BUILD_SPEC_PROJECTION.py` 只是一次性隔離文件投影工具：原件唯讀、CREATE_NEW 輸出；`--verify` 精確比較 deterministic UTF-8 bytes。不呼叫既有 Compiler、不操作 Grant／Writer／Git／SQL、不 import 執行引擎，不負責挑選可執行工作。它不是第二套 Compiler 或 Controller。

原 `scripts/p00_compile.py:59–67` 即使編譯成功仍輸出非執行候選；`automation/platform/package.schema.v1.json:4,11–15` 的 closed Pxx ID 不接受 PKxx／MAxx；`automation/engine/contracts.py:63–66,113,134` 的 strict closed native records 不可任意加欄。96 張 `.spec.json` 是 navigation companions，最後仍交既有 WORK 的受支持 Unit／Profile／Source binding 轉成 native WO，不能把 JSON 改名成 WO 就執行。

Hash 分工沿既有規則：原檔用 raw bytes SHA256；選取正文用既有 canonical JSON（UTF-8、sorted keys、compact、ensure_ascii=False、allow_nan=False）；Git blob 與 CRLF worktree raw 分開。Result 仍依既有 RR-01 規則對排除頂層 ref 的完整正文計 Hash，不因本補充新增另一種 Result Identity。

96 個規格的 `execution_evidence` 全為要求／空值；U01 舊 Accepted Result 以外，不填入任何未發生的 WO、Invocation、Grant、Writer、結果、審查或接受。規劃路徑不是實際 Allowlist，CREATE_NEW／MODIFY、preimage、toolchain／schema／DTO、test／generated／control-plane 寫入必須由當次精確 WO 固定。

`PRECOMPILED_WORK_QUEUE.index.json` 排序先放 57 個 MVP 必要 Unit，再放其餘 39 個完整 B3 Unit；全序仍滿足 364 條原 DAG。MA01-U01 是 Accepted reuse-only，不可重派。Queue rank／MVP wave 都不是 READY；每次從原 Current Authority 和原生工作單挑選，不以本 Index 改寫原 Queue。第一張 MVP 準備候選是 MA02-U01，不是已授權工單。

## 雙層施工

| 條件 | Lane A：AUTHORIZED IMPLEMENTATION | Lane B：ISOLATED CANDIDATE DEVELOPMENT |
|---|---|---|
| 資格／權限 | 每單 current native WO、Grant、qualified route／Source／Context／Result／Intake、cost／capacity、安全 Gate | 另外的精確 candidate 開發 Grant、受支持 Profile／政策與所有適用安全條件；本輪並未建立它 |
| 上游 | Exact Accepted Result＋外部 Acceptance 或合法 qualified scoped reuse | 不冒充 accepted dependency；既有義務仍適用。若要使用未審上游或越過 pending barrier，先取得正式 reviewed policy successor；高風險未驗證語義不能用於正式下游 |
| 寫入 | 原精確允許路徑／preimage；單 Writer | 精確隔離根目錄／Worktree與受限 Allowlist，但仍同一全域單 Writer；Worktree 不是授權 |
| 結果 | 作者 Result → 必要 Independent Review → Intake → 原接受程序 | Candidate／未接受，禁止主線合併、自動 Authority 提升或正式依賴 credit |
| 沒有權限 | 只讀、候選規劃、已明示允許的非實作工作 | 同左；不能以「隔離」自行 Coding |

## 現行連續施工邊界

直接依據：

- `development_entry_protocol.v2.yaml:18–28`：安全／unfinished／pending review 優先，`unfinished_blocks_new_dispatch:true`，review feedback 不授權。
- `CODEX_EXECUTOR_KERNEL.md:162–171`：不得自 ACCEPTED／NEXT_PACKAGE_AUTHORIZED，固定 bounded result 後 STOP at Review Barrier。
- `AGENTS.md:234–240`：依賴滿足的 READY 才可施工；每 autonomous run 最多一個 mainline Package；每 failing test 的最多兩次 scope-internal correction 與當次 Grant 取較嚴限制。
- Guide Annex C02／C04：單 Writer；影響選取不可移除原強制 Full Regression／Independent Review。
- `authorization_lifecycle.v1_1.yaml:18–50`：fresh exact lifecycle、CONSUMED 不得重派、真正已 invoked 的 same-execution resume 需重新驗證，缺 Invocation STOP_NO_BACKFILL。

因此，現行制度下可以持續**選取及準備候選**、執行合法同 WO 有界修正與真正 resume；完成原 mandatory review／acceptance 後才依新權限推進。沒有來源支持的一般「Review 缺席就做別張」放行規則；不得把設計要求冒充已啟用例外。也不能杜撰原政策逐字規定「任何 pending 永久阻擋所有不相干工作」；遇無明確例外時 fail closed，提出精確可審的 successor。

唯一現有明示可延後而不阻合法 resume 的 cost review，在 `execution_cost_contract.v2.yaml:46–49` 明訂為 WORK_FORECAST_CAPACITY_REVIEW_NOT_SOURCE_DEFECT_OR_SEMANTIC_REVIEW，且 completion 後開始新工作前仍須 materialize；不是產品 Independent Review 豁免。

## Deferred Ledger 與影響閉包

`DEFERRED_REVIEW_LEDGER.json` 是原生紀錄的衍生觀察檔，不是新 Review Database。現在實際待審產品 entries 為 **0**，因本輪沒有新產品執行；不產生 96 筆幽靈待審資料。U02-QF01 是原支線已返回的 Qualification FIX_REQUIRED，不假裝成 Ultra 缺席待審。

待真實結果存在且原授權涵蓋 evidence write，才保存 template 要求的 WO／Execution／Grant、exact source、Git／Diff、Result ref／body hash、測試、risk、未驗證上游、consumer、review type、required-before Gate、延期原因、優先序與 revalidation。原生 review status 以 reference 指向，不另簽結果；補充觀察採新版本／事件，保留歷史 bytes。即使工具或模型缺席，也只能 PENDING，不能 PASS。

`REVIEW_DEPENDENCY_IMPACT.json` 已保存所有 96 Unit 的 direct／transitive consumers 及 578 個接口暴露。由 364 條原 DAG 計算影響，不增加整個 Package completion barrier。191 個 DESIGN_CHECK_SOURCE 保持 source-only，不能增加 runtime edge 或冒充 Producer Result。

失敗／正文或版本變更時，先找最早未審共享前置條件。所有真正依賴者列為需重驗的候選；共享 Contract Consumer 的額外影響另外列明，不能只因在同 Package 就全部作廢。原 accepted receipt 保留歷史效力；是否適用新來源必須再核對，不覆寫舊接受。修正只產生候選 Scope，無新 Grant 不改程式，不自動 RF02。

## Catch-up Batch

先處理 unresolved 共享 ancestor，再在當前可審根節點間比較安全／L3-L4／影響數／等待時間，保持依賴順序。Contract Owner、來源版本、環境／Profile、review type 與授權可相容的 exact subjects 才可合成 Cohesive Batch；Batch envelope 仍保留每張 Unit 的獨立 Subject、結果與判定。不能合併後省掉某個 Counterexample 或 Human Gate。

依資格選擇獨立 Reviewer，工具不必永久 Ultra；作者與 Reviewer 不得同一工作上下文冒充獨立。判定由 exact immutable inputs 出發，不依作者 PASS／計數。重驗 Source／Revision／Hash／DTO／Profile／Environment／Source Closure、測試與 Applicable Grant，再依原制度 Review → Integration → Acceptance。補審不追認過去未授權的施工，也不重審未受影響且仍適用的 Accepted Result。

## 六個 Mock PoC 與限制

Expected 在 `POC_CONTRACT.json` 先固定；`poc/test_six_mock_contracts.py` 用真實 Unit 身份與原 DAG，但 Grant／Result／Reviewer／Execution 全為不可進入原生系統的 MOCK_ONLY fixture。只回傳記憶體判定，沒有實作控制器、發出 Invocation 或改 Repository。

P1 新單須 fresh authority且 Package-run 邊界停止；P2 same invocation resume、不補造證據；P3 current pending barrier 拒絕，另在明示未啟用的 prospective policy fixture 展示獨立工作；P4 無 Grant／來源／資格／預算／Writer 不通過；P5 未審或同 ref 換內文拒絕且追蹤下游；P6 根節點優先、拒同作者／Hash drift、影響重驗而不自接受。

PoC PASS 只證明此受測合成模型的六個情境。不代表現有政策已接受新例外、96 Units 已具資格、真實 HOST／PostgreSQL／Broker／Controller 合格，或正式 Coding 已授權。結果與成本／時間在 `poc/POC_RESULTS.json`；產品測試仍 NOT_RUN。

## 權限差額

| 項目 | 目前可做 | 後續真正需要 |
|---|---|---|
| 預編規格／唯讀規劃 | 已完成，可按 Hash 讀取及 verify | 有 Source Delta 才產新投影版本，不改既有 Source |
| Review 記錄／補審準備 | 讀取原生 Evidence、分類／影響、準備 exact Batch | 實際 Review 仍依原資格與必要授權；接受由原制度決定 |
| pending Review 時的獨立新施工／LaneB例外 | 本輪只有候選設計和 Mock 驗證 | `MINIMUM_POLICY_DECISION_REQUEST.json` 所列的精確 successor 程序＋必要 Review／Owner Acceptance；不能僅憑下一張 Grant 覆蓋原政策 |
| 新 Unit Qualification | 可準備差額與申請 | 各 Unit intended-use 的適用真實證據／Grant；無 API 資源不重複要求不存在 Trace |
| 產品／候選 Coding | 無新增權限 | 每單 native WO、finite Budget、適用資格、fresh Grant／Writer／Invocation與控制面範圍 |
| Git Publication | 本包仍本機隔離 | 另行 Exact Allowlist／Scope／Privacy／Source Binding／Git Baseline 授權；不可加入原已消耗 Publication Grant |
| Runtime／SQL／Broker／Restore／Controller | 不執行 | 原適用階段的專屬資格及授權；不無差別前移至無關 Unit |
