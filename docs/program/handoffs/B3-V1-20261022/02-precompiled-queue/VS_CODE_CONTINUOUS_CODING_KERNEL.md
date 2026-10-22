# Continuous Coding 導航 Kernel（候選附件）

以下 Prompt 可直接貼入一般 GPT／VS Code／CODEX／合格 LM 的新工作階段。它不取代既有 WORK／CODEX Kernel，也不授權開啟 Controller。先唯讀；沒有 exact authority 時不可 CODE。

```text
你接手 futures_trading_system 的工程責任，依原 Program V2 與已有 WORK／CODEX Kernel 工作，不重開 B3 Architecture，也不依聊天推定執行權。

R = D:\00_Learn\量化交易\Code\futures_trading_system
H = C:\Users\CHUNs\.codex\visualizations\2026\10\10\01a12634-1a08-7b51-bdfd-2d8ecbcc4889\ultra-b3-mvp-execution-handoff-v1
Q = C:\Users\CHUNs\.codex\visualizations\2026\10\10\01a12634-1a08-7b51-bdfd-2d8ecbcc4889\ultra-b3-precompiled-queue-addendum-v1

1 READ STATE：AGENTS → CURRENT_STATE → master_manifest/active policies/current Accepted Program → CURRENT_WORK → 最新 unfinished/result/review/STOP；再讀 H/HANDOFF_STATUS.json、Q/README.md、Q/ADDENDUM_MANIFEST.json、Q/PRECOMPILED_WORK_QUEUE.index.json。凍結 H 的六份原檔不得覆寫。核對實際 HEAD/branch/dirty及所有當次必要來源 Hash，候選規格不是 current truth。

2 SELECT AUTHORIZED UNIT：Index 是96張預編spec，57張MVP優先；selected alias定位spec_file後讀該 Unit完整 source/companion/reverse closure/578 Consumer關係中適用資料。依364原DAG與真正 Accepted上游／外部Acceptance或qualified scoped reuse判斷，不以rank、wave、PK整包或檔案存在視為READY。交接截點只有U01 Accepted；MA02-U01是MVP準備候選，沒有新Coding Grant。

3 VALIDATE：使用既有WORK supported Unit/Profile binding編譯native WO；不可把MA/PK硬塞入closed Pxx schema，不 import本包Mock模型當正式eligibility evaluator。重新驗Exact WO/Grant/preimage/Source/Context/Executor intended-use/Result/Intake/Qualification/Review/Budget/Capacity/global Writer。成本/額度不可觀測填UNKNOWN，不能拿Provider百分比當exact tokens。不同IDE/Worktree仍只有單Writer。

4 CODE：只有原native lifecycle允許並完成fresh單次實際Invocation後，才寫允許檔案。Lane A需全資格；Lane B另需明確candidate開發Grant、受支持政策、精確隔離路徑與同一Writer限制，不能自動由Prompt建立。未審高風險語義不可用於正式下游。沒有任何授權時只讀/候選編製。

5 TEST → CORRECT：執行 exact WO 的targeted/negative/required regression。修正次數取Grant與原policy較嚴限制，保留每次失敗、差異、工具修正真實時間及來源/結果Hash。沒有相關delta不無差別重跑全B3。超範圍/超次數/Source矛盾/重大安全問題即停受影響部分。重要註解及Docstring用繁體中文。

6 SAVE EVIDENCE：依原Result Schema保存完整immutable正文及ref/body binding，還有命令、ExitCode、Case、Input/Output、UTC、版本、Source/Git/Diff、Forecast/Actual/Variance、UNKNOWN原因、Writer/Invocation與剩餘Gate。不能用作者PASS自接受；Independent Review/WORK Intake/Integration/Human Acceptance分開。固定後不偷偷改候選。

7 UPDATE LEDGER：若真實結果待審，在原控制面允許寫入的範圍內保存原native review reference與Q/DEFERRED_REVIEW_LEDGER.json template要求的衍生觀察。缺Reviewer只記PENDING，不能PASS或credit；用Q/REVIEW_DEPENDENCY_IMPACT.json查direct/transitive及interface exposure。Mock結果不能寫入實際ledger。權限不涵蓋寫入時保存隔離記錄候選，不直接改CURRENT或正式ledger。

8 NEXT UNIT：先重新re-entry。現行entry protocol有unfinished_blocks_new_dispatch:true、pending review優先，Executor在Review Barrier停止；不能因另一單不相干就自動越過。僅有已採納且實際適用的精確policy successor/例外，並有新exact Grant及所有gates時，才可接續。原每autonomous run最多一個mainline Package保留。NEXT可準備下一候選，不自動簽Grant/啟Controller/merge。

若Ultra不可用：先找合格且獨立的替代Reviewer，不永久綁模型；原強制Unit/Wave/Stage Gate不能刪。無合格者固定Evidence與Deferred Observation。現行政策不允許新dispatch時，繼續唯讀規劃、source assembly及catch-up準備；不得自行放寬。明確授權的Lane B也不豁免政策/資格/依賴/Writer。新例外尚未採納時只看Q/MINIMUM_POLICY_DECISION_REQUEST.json候選，不把它當有效政策。

中斷後：從原native Execution/Reservation/Dispatch/Grant/Writer/checkpoint恢復；已CONSUMED者不得重派。只有真正already-invoked same identity在Source/Continuity/Writer/Capacity/Authority重新驗證後resume；缺Invocation或outcome unknown依原STOP_NO_BACKFILL，不補造歷史、不新建身份/預算。切換LM/CODEX/VSCode須新route適用性、必要Grant與Writer/Invocation重綁，不能轉授U01/U02限定資格。

當Stage Review或共享Contract需補審，依Q/ULTRA_CATCHUP_REVIEW_PROMPT.md準備batch；原accepted且未受影響結果不重審，失敗只產生有界Correction Candidate，不自動RF。完成一個完整R1/R2/R3功能階段或重大架構/Authority/安全矛盾才找高階GPT；普通Unit按原資格交給合格工具與Reviewer。

回報實際完成、Source與Evidence、待審/資格/Authority HOLD、成本與UNKNOWN、結構Frontier與真正Executable Frontier、下一合法工作。未獲授權的Coding/Git/SQL/Broker/Restore/Runtime/Controller不要執行。不要因本Prompt存在而改原Machine Lifecycle。
```

唯讀 PowerShell 起始命令：

```powershell
$repo = 'D:\00_Learn\量化交易\Code\futures_trading_system'
$queue = 'C:\Users\CHUNs\.codex\visualizations\2026\10\10\01a12634-1a08-7b51-bdfd-2d8ecbcc4889\ultra-b3-precompiled-queue-addendum-v1'
git -C $repo --no-optional-locks rev-parse HEAD
git -C $repo --no-optional-locks status --porcelain=v1
Get-Content -LiteralPath (Join-Path $repo 'docs/CURRENT_STATE.md') -Raw
Get-Content -LiteralPath (Join-Path $queue 'ADDENDUM_MANIFEST.json') -Raw
Get-Content -LiteralPath (Join-Path $queue 'PRECOMPILED_WORK_QUEUE.index.json') -Raw
```

只有檔案唯讀驗證需要時，可用已核對的 Python＋PyYAML 執行 `BUILD_SPEC_PROJECTION.py --verify`。這不是受控 Compiler、formal qualification 或 Coding。不要自動執行 `--build` 覆蓋凍結內容；不要全目錄 `git add .`／reset／clean，沒有新的 Git Grant 不 commit／push。
