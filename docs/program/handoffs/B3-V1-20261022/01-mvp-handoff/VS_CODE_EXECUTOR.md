# VS Code／CODEX／LM 施工交接手冊

識別 `ULTRA-B3-MVP-EXECUTION-HANDOFF-V1`；版本 handoff.v1。本文件是導航候選，不授權修改產品、建立 Writer、Dispatch、Qualification、Git、SQL 或 Controller。正式規則仍由 Repository Current Authority 決定。所有「執行」步驟均以該次精確 Grant／資格有效為前提。

## 可直接貼入新對話的啟動 Prompt

```text
你接手 futures_trading_system 的 WORK／Executor 責任。不要重開 B3 全域架構審查；不要依聊天記憶或本 Prompt 推定有執行權。

Repository：D:\00_Learn\量化交易\Code\futures_trading_system
交接包：C:\Users\CHUNs\.codex\visualizations\2026\10\10\01a12634-1a08-7b51-bdfd-2d8ecbcc4889\ultra-b3-mvp-execution-handoff-v1

先唯讀依序解析 AGENTS.md → docs/CURRENT_STATE.md → automation/governance/master_manifest.v1.yaml → 其有效 Machine Policies／Accepted Program → docs/CURRENT_WORK.md → 最新 handoff/delta/result/review/STOP；再讀交接包 HANDOFF_STATUS.json、MVP_SCOPE.md、MVP_ROUTE.yaml、WORK_ORDER_CONTRACT.yaml、STAGE_GATES.yaml、VS_CODE_EXECUTOR.md。不要將 handoff 狀態快照覆蓋 CURRENT_STATE。

核對實際 Git HEAD／branch／dirty 狀態與固定 Hash。交接截點本機 HEAD 2634717b1443eb95fa0fde4d5d987347ef2160e8；GitHub master 9b5ab5fdd98744a7db45ec9f14b64ef1f324920f；已發布 B3／NAV 在 codex/b3-v1-accepted-baseline-publication 的 e287f6ac0744875e8d4bca103a6b73b4cf53416d，不在 master。這些是截點，不是要求 reset 或 checkout。遇 drift 只停止受影響使用，保留現場，不自動修檔、fetch、切分支或清理。

採納基線是 MA-ARCH-REVIEW-v9-SOURCE-CLOSURE-PAIR01，須與已閉合 B-TRACE-01 固定 companion 一起讀。原 96 Units／364 依賴／95 API／19 UI／578 Consumer／64 Findings 保留。目標 MA10-U06 的 MVP 祖先閉包 57 Units／184 依賴，不是 Unit 編號順序，也不是全部已獲授權。

交接截點 MA01-U01 已 Accepted，其他 Units 未有新 Coding Grant。C3 NOT_QUALIFIED、C5 未授權／未執行、C6 待 Human、P00 0/8；適用 Gate 逐路線從正式來源核對，不無差別豁免或全部前移。U01/U02 限定 Manual 資格不能轉授新 Unit。U02-QF01 為 U02 專屬 HOLD，不是本次 MVP 的上游依賴。

優先準備 MA02-U01（資料基礎）：唯讀確認真實 Unit UUID／Revision／Source／U01 Accepted Dependency，依現有原生 WORK 準備 intended-use 適用性與資格差額、WO／Budget／Allowlist／Test Oracle 候選。尚無該 Unit 資格／Coding Grant；不可自行實作。當 Current Authority 已另有有效授權時，以精確最新 WO 為準，別重用舊 Grant／Invocation／Writer。

工作迴圈 READ → SELECT → CODE → TEST → FIX → RECORD → NEXT。CODE 前必須完整符合原 Work Order、Source／Context／Result／Intake／Executor intended-use 資格、Accepted Dependencies、預算、容量、全域單 Writer、單次執行授權與允許檔案。SELECT／NEXT 只能挑選合法候選；不能自行建立或簽署 Grant。既有一個 autonomous run 最多一個 mainline Package 規則保留，Controller 不自動啟用。

保留 React → ASP.NET BFF → Python API → Quant Core → Persistence。接口只由正式 API／DTO／Schema／Source／Revision 決定，Mock 不分叉語義。重要註解、Docstring、資料流說明用繁體中文。檔案位置／工具版本／資料精度等未在當次 WO 固定時，先修該次候選，不臨時擴檔案或降 Oracle。

每 Unit 執行已授權的 Targeted／Negative／Regression，修正次數取當次 Grant 與適用政策較嚴限制；原 AGENTS Level 3A 每個 failing test 最多兩次 scope-internal correction 的規則仍保留，並非另給每 Unit 兩次預算。超過即 STOP。測試規格、合成工具測試、作者 PASS、Independent Review、WORK Intake 與 Human Acceptance 分開記錄。需 Independent Review 時交給合格且隔離上下文的 Reviewer，不自己接受自己的結果。階段 R1／R2／R3 完整功能後才請高階 GPT 作階段檢核；不能取消原有強制 Unit Review。

每次修改／執行保留 UTC 時間、精確工具版本與命令、輸入／輸出、ExitCode、Source／Result Hash、Case 結果及修正原因。無法量測 Token／成本標 UNKNOWN 並寫原因，不假造。外部 API 資源未獲授權就不用。不要執行需要 DSN／Migration／Broker／Restore／Runtime 的測試，只因它叫 test 不代表沒有副作用。

中斷後重新 re-entry，依法檢查原 Execution／Reservation／Grant／Writer／Continuity，再決定可否恢復；不可重複 dispatch 已消耗的執行。換成 LM／CODEX／VS Code 不繼承舊 Executor 的 Invocation／Writer／限定資格。所有下一步均以 fresh authority、dependency frontier 和真實 Accepted Result 為準。

現在執行可合法完成的唯讀核對與候選準備。只有新的精確 Grant、受保護契約／政策更動、必要資源或正式接受需要 Human 時，集中提出最小決策；不反覆請 Ultra 解釋已固定架構。回報實際完成、NOT_RUN／HOLD、下一合法工作及精確證據入口。沒有有效 Coding Grant 時停止在申請之前。
```

## 讀取與 Context

讀一次 Current Authority，再只載入當選 Unit 的必要完整閉包：Accepted Source／正文、Chapter／Feature／Unit、v9 pair companions、B-TRACE Consumer 補充、完整 incoming DAG、required reverse semantics、Producer／Consumer、DTO／Schema、Fixture／negative Oracle、適用 Finding Trigger、Profile／Result／Intake、實際 Grant。

不得只讀 `MVP_ROUTE.yaml` 的摘要就實作。其 JSON Pointer／Raw Hash 定位原文；Hash、摘要、檔名與壓縮後 bytes 都不能代替必要語意。原 128 KiB Context Gate 未概括變更，僅能沿已正式核准的 route／Unit 限定 Amendment 使用；不截斷 required sources 或假稱所有 Manual 都豁免。

公開網頁只能取得某些發布截點。Canonical gzip／分段承載需驗證 transport hash 及重建後原始 bytes hash；公開 Derived Index 是導讀，若必要 Private Source 不可讀，HOLD 該次 Source Assembly。不要下載或印出 Secrets／真實帳戶資料，不讀 `.env`、DSN 或憑證來湊資格。

## Windows 唯讀起始核對

以下命令只讀狀態。不要加入自動 checkout、pull、fetch、reset、clean、commit 或 push。

```powershell
$repo = 'D:\00_Learn\量化交易\Code\futures_trading_system'
$handoff = 'C:\Users\CHUNs\.codex\visualizations\2026\10\10\01a12634-1a08-7b51-bdfd-2d8ecbcc4889\ultra-b3-mvp-execution-handoff-v1'
if (-not (Test-Path -LiteralPath $repo -PathType Container)) { throw 'REPOSITORY_NOT_FOUND' }
git -C $repo --no-optional-locks rev-parse HEAD
git -C $repo --no-optional-locks branch --show-current
git -C $repo --no-optional-locks rev-parse master
git -C $repo --no-optional-locks status --porcelain=v1
Get-Content -LiteralPath (Join-Path $repo 'AGENTS.md') -Raw
Get-Content -LiteralPath (Join-Path $repo 'docs/CURRENT_STATE.md') -Raw
Get-Content -LiteralPath (Join-Path $repo 'automation/governance/master_manifest.v1.yaml') -Raw
Get-Content -LiteralPath (Join-Path $repo 'docs/CURRENT_WORK.md') -Raw
Get-Content -LiteralPath (Join-Path $handoff 'HANDOFF_STATUS.json') -Raw
Get-FileHash -LiteralPath (Join-Path $repo 'docs/CURRENT_STATE.md') -Algorithm SHA256
```

先讀 manifest 指定的有效 policies 及最新紀錄，才將本包 status 作比較。不要自動列印整個 private archive。必要搜尋用 `rg`，先 `Test-Path -LiteralPath` 確認目錄，依 Unit／契約限制搜尋範圍。Raw file SHA 與 Git blob SHA 分開記錄；CRLF 差異不能混用驗證。

## 每一張 Work Order 的七步

| 步驟 | 實際工作 | 必須拒絕／停止的情況 |
|---|---|---|
| READ | current／manifest／policy／latest delta／Source Assembly；核對 raw／canonical／Git 各 Hash domain | 缺正文、版本錯誤、同身份不同內容、過期 profile／權限 |
| SELECT | 依原 364-edge DAG 的真實 Accepted 上游挑選已授權 WO；只在合法範圍預編下一張 | missing dependency、未審 Result、只憑 package queue／結構波次視為 READY |
| CODE | 重新取得 global Writer／capacity／fresh execution，精確 Allowlist／Preimage，Contract-First 施工 | consumed Grant 重用、其他 Writer、額外檔案、Program／Authority 擴權 |
| TEST | 執行當次 WO 精確命令與全強制 Case IDs、negative／targeted／必要 regression | 測試檔不存在仍視為 PASS、部分 case 代替完整 case、未授權 DB／Migration |
| FIX | 只做範圍內有限次符合性修正，先分析同一失敗根因，保留失敗與修正前後證據 | 超次數、降低 assertion、需受保護契約改動、範圍外 Reader／Producer |
| RECORD | 凍結結果正文／Hash，exact Review Subject → 合格 Reviewer → WORK Intake → 原正式接受程序 | 作者自 ACCEPTED、同 result.ref 接受不同 body、UNKNOWN 成本／測試裝成 0／PASS |
| NEXT | 更新依法可寫的狀態，重算 dependency frontier，準備下一候選 | 沒新授權／適用資格即繼續 Coding，或跨 autonomous package 邊界 |

表格是程序導讀；正式 single-use reservation／consume／writer 次序見 `WORK_ORDER_CONTRACT.yaml` 引用的原政策。它不是一支自動執行腳本。當 Current Authority 不允許某狀態寫入，先保存隔離候選，不直接修改 `CURRENT_STATE.md`。

## 測試、Evidence 與成本

測試命令由正式 WO 固定，不能在此用一個通用 `pytest` 代替所有 Unit。`MVP_ROUTE.yaml` 的 command_proposal 須先確認實際 executable／test path／case 對應；部分模組尚未建立。`pytest -p no:cacheprovider` 可減少無關 cache 寫入，但不因此豁免測試的實際副作用。沒有別的授權時不啟動 Postgres、跑 migrations 或開 browser/server。

R1 保留市場資料版本、OHLC 型別與缺值、分頁／Cursor、權限／錯誤、重送及 DB／query／Chart 一致性。R2 保留資料 snapshot、策略 immutable revision、無未來資料、成交／成本政策、equity／drawdown 與結果 Artifact。R3 保留 MA10-U06 全 428 個必要 Case ID 及既有旅程，不只一支 happy-path smoke。確切 Positive／Must-Reject Oracle 由來源 Pointer 取得。

64 筆 Finding 的 `Finding → Root Cause → Counterexample → Test → Trigger → Gate → Evidence` 沿既有 Regression Plan。先區分 PLANNED／NOT_RUN／實測／Manual／Environment／Independent Review，這些是報告標籤，不另創 Machine enum。舊 U01 測試可重用於精確 unchanged 依賴，不能當新 Unit 的測試結果。

每次工具操作記錄起訖 UTC、Operator／Producer／Consumer／工具版本、精確命令與輸入參照、ExitCode、stdout／stderr 保存位置／Hash、Case IDs 與各結果。工具或 Fixture 曾修正時，將真實修正時間與前後檔案綁定納入正式 Case Result；不要事後猜時間、只在另一份說明補敘，或覆寫已凍結試驗（U02-QF01 的保留教訓）。無真實 telemetry 就填 UNKNOWN／原因／取得方式。

token／wall time／外部費用／本機資源依原成本表分開記錄；預估 UNKNOWN 需由該次 Grant 的政策處理，不能沿用 U01 的 Owner UNKNOWN 同意。沒有費用的外部呼叫也須有資源授權；本包沒有真實模型 API 授權。

結果必須用既有 Result Schema 與 canonical hash 規則：`result.ref.source_hash` 綁定排除頂層 `ref` 後的完整正文。Consumer、Dependency、Reuse、Intake／Review 全部驗證同一可信綁定；缺 hash／來源／接受收據時不能補成 READY。Result.body 的原 outcome 與外部 Acceptance 分開保存，不為了 Accepted 改寫舊正文。

## Writer、恢復與 Executor 切換

所有本機工具都受單 Writer 約束；開第二個 Worktree／VS Code 視窗不增加權限。保留使用者 dirty／untracked，不 `git add .`、不批次覆寫、不刪歷史／data。適用時只暫存精確 allowlisted 檔案；沒有具名 Git Grant 不 commit／merge／push。

中斷後先讀原 run／reservation／writer／result／STOP 和 fresh authority。尚未 commit dispatch、已消耗但未呼叫、已呼叫結果未知、可恢復同 invocation 等情況依原政策分辨；不建立第二個 Execution 來掩蓋 unknown outcome。重新確認 HEAD／source／capacity／profile／continuity，不可假稱先前 Context 一直存在。

換 LM Studio／CODEX／其他工具時，只可重用 source-bound 契約與接受成果。新 Operator／Consumer／Producer、profile/intended use、Context 限制、Result／Intake Adapter、capacity、預算與單 Writer／Invocation 重新驗證。LM 專用資格可在真正移交前取得，不阻擋未使用 LM 的合法路線；目前沒有證據可將 U01／U02 Manual 限定 receipt 直接轉授。

## Review 時機與返回 WORK

一般單元由合格 Executor 自行 Targeted／有限 FIX，必要 Review 用符合獨立性與資格的 Reviewer；不要求 Ultra 每張日常 Coding。高階 Stage Review 在 R1、R2、R3 功能整合後，讀 exact stage bundle／差異／失敗反例／未取得資格，不重讀全部歷史；重大 Source／Authority／capital/order/fill 安全矛盾即停止受影響範圍並升級。

Stage Review 不等於原 Unit／Owner Acceptance，不替代 PostgreSQL／Restore／Broker／Release 資格。Reviewer 不能改被審 Subject 來取得 PASS；作者不能自行簽 Reviewer／Human Gate。

回交 WORK 使用既有 Result／Intake 欄位及原生 adapter，至少提供下列真實內容（清單不是新 JSON schema）：

- Unit／WO／Execution／Grant／Writer／Profile 的實際身份與 Raw／Canonical／Git Hash domain。
- Exact input Source／dependencies／Context／工具版本與 Operator／Consumer／Producer。
- Allowlist Diff／原 preimage／實作正文與結果 Hash；未改受保護來源的證據。
- 測試命令／Case／失敗／有限修正／結果 Evidence／NOT_RUN 與理由。
- 成本預估與 actual、UNKNOWN 欄位；停止／恢復資訊。
- Independent Review exact Subject／verdict；原 Owner／Intake Acceptance 的實際收據，尚無則 pending。
- 下一個結構 Frontier、可執行 Frontier、資格／Grant 差額；不以列表位置授權。

## 本截點的第一個合法任務

**不是產品 Coding 工作單。** MA01-U01 已正式 Accepted，已消耗權限不可重用。MA02-U01 只具備結構上的 U01 上游接受條件，尚無該路線實際資格、新 Grant／Writer。

先唯讀準備 MA02-U01 的 intended-use 適用性／Qualification 差額與精確申請，引用 `MVP_ROUTE.yaml` 的真實 UUID／Revision、原始 source body、U01 Accepted Result／外部 receipt、既有 WORK Profile 規則，並完成 native WO、scope／preimage、case-to-test、Budget 候選。必要固定申請與 Human 決策完成前，只準備不執行。

U02 的 QF01 已有別張待決精確申請，屬不在本次 MVP 閉包的支線，不重跑、修復或標為 Qualified。所有 Current 狀態若已更新，先沿新權威做 Delta 判斷，不機械重做此截點。

## 程序是否需要新 Controller

不需要。本文件只將既有 WORK／CODEX Kernel、單 Writer、Grant 與 Intake 規則整理為可讀介面。NEXT 可以提前準備，原制度尚未授權的 autonomous progression／Controller／parallel writer 都維持停用。若未來確有原機制無法解決的證據，再提出精確 Amendment；不為執行這份 Prompt 新建平台。
