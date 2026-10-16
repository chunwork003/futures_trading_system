# Git 主線 Reconciliation — 2026-10-11

狀態 `VERIFIED_CANONICAL_MASTER_ALIGNMENT`，僅指 branch／default／tracking；不表示 P00 或產品 Architecture Acceptance。

## Current Source Witness

| 項目 | before | after／核對 |
|---|---|---|
| GitHub default | main | Human 已修改；repository GET 確認 master |
| 遠端 HEAD | main@0cb0283… | `git ls-remote --symref` 確認 master@9b5ab5f… |
| 遠端 master | 9b5ab5fdd98744a7db45ec9f14b64ef1f324920f | 不變 |
| 本機 master | b36e9bc253a13a3a361b3861e607455658df524b；behind78 | 經 ancestry／expected-old CAS fast-forward 至 9b5ab5f…；ahead0/behind0 |
| 本機 origin/HEAD | 非 symbolic ref | 綁 origin/master；重新解析為 9b5ab5f… |
| main | 0cb0283b8c5f795f8da1672575cbb674945db73a | 本機／遠端均保留，不合併、不刪除 |
| 遠端 P00 | d2bd7e9f24d339894b9f559030d1f78b1c78dca7 | 不變，尚未合併 |
| 作者工作樹 | 2634717b1443eb95fa0fde4d5d987347ef2160e8 | 同 branch／HEAD；ahead遠端候選6；不切換、不 Push |
| SQL-PREFLIGHT worktree | master base 9b5ab5f…；untracked experiments | 保留待審；沒有升級 Acceptance |
| detached worktree | main@0cb0283… | 保留，沒有刪除或移動 |

main/master graph 的 merge-base exit1；其 split 為 1/628 commits。禁止以 unrelated-histories merge、reset、force push 解決入口問題。Git ref 修改只限不在任何 worktree checkout 的 local master 與 origin/HEAD，先保全、證明 ancestry、核對遠端 SHA，再 CAS 更新。filesystem 沙箱額外批准不擴大產品／SQL／發布權限。

## 來源保全與核對

外部私有 preservation ID `source-preservation-20261011T063952Z`，不在 Public repository 中。`SOURCE_PRESERVATION_WITNESS.json` SHA256=`982e2fa4ce32c459e0a292e84a7d4388af4ad3361113f0990bfbd016f26dfa04`。

Git bundle 保存當時全部50 refs與完整可達歷史；bundle verify 成功。另在隔離新 bare 目錄從 bundle 重建，確認原 main、舊 local master、local P00 六筆、兩個 origin refs 的相同 SHA。這是 Git 來源恢復檢查，不是產品 Restore Test。

另捕捉7份 explicit allowlisted SQL-PREFLIGHT bootstrap source及上一版 execution policy，共8份 source copies。沒有複製或讀取真實 Secrets、行情、SQL database、dump或 private logs。未追蹤 `data/` 保護不變。SQL-PREFLIGHT 的完整待審 Evidence 留原 private completion 路徑，本 source copy 不冒充完整工程／資料備份。

STEP1–7 原始完整 reviewer messages 及本次 Owner 原始請求已從本 chat 保存於外部 `review-conversation/`，各訊息有 turn/message ID、UTF-8內容與 hash來源。它們是 source material；其中候選交接指令不自動取得新執行權。

## 入口、CI、設定與限制

AGENTS、WORK/CODEX kernels、startup 已明列 master/origin/master；正式 Master為 `docs/V1_SYSTEM_BLUEPRINT.md`。此輪沒有把舊 main 的 README當產品規格來源，也沒有改寫 accepted Manifest／Receipt。

branch collection GET取得17 branches，master/main/P00與本機cached遠端SHA匹配。沒有 `.github/` tracked目錄觀察；不推導為 GitHub Actions一定沒有其他設定。workflow collection工具拒絕該endpoint；open PR collection回404；branch-protection回403 `Resource not accessible by integration`。因此 CI設定、openPR完整性、ruleset／protection細節為 `NOT_VERIFIED`。branch-list protected=false只限其回傳值，不代表能完整排除 repository rulesets。

Repository仍為 Public；沒有新檔案或私有內容發布。新的完整架構文件為本機候選，須經內容分類／source allowlist／secret filtering／exact review與合法publication後才能送GitHub。

## 安全恢復與未完成操作

1. 需恢復舊來源時，用 preservation witness核對bundle hash，在新的隔離目錄重建；不覆寫現有checkout／data／DB。先比較refs和完整parent graph，再由原Owner决定是否重接工作線。
2. local master若再漂移，先fresh remote witness與ancestor proof；不要反覆reset或假裝同步。source SHA不符就STOP受影響整合。
3. 若default branch意外改回，Human可在GitHub Settings→Default branch重新選master；再次GET＋remoteHEAD核對。這是設定變更，不動main歷史。
4. 要整合P00及其六筆提交，另需精確源閉包、C3/C5/C6、獨立review、Human採納與bounded integration authority；本輪不採merge。
5. CI／protection驗證於可用admin設定介面一次集中補查；不需為章節設計新建token或擴權。

`GAP-REPO-001` 的原記錄保留，本報告提供修正證據；本輪沒有自行修改其正式接受狀態或重寫 CURRENT。


## RCG01 candidate.4 source-bound successor

Currentformal/default仍master；Human長期main目標與受控雙歷史遷移PLANNED_NOT_EXECUTED見[MAIN_MASTER_MIGRATION_CONTRACT.md](MAIN_MASTER_MIGRATION_CONTRACT.md)。最新完整B3要求以[B3_RELEASE_SLICE.json](B3_RELEASE_SLICE.json) exact requiredset為準，包含OOS/WFO/MC/benchmark/ablation/AIAnalyst，不採舊薄firstslice。CODEXSol6.1High主要Coding、GPT+VSCode/LMquotafallback見../ENGINEERING_EXECUTION_POLICY.candidate.v3.md；旧政策與原接受source保留。舊段落只表示priorcandidate/historicalsource，不可拿來覆蓋此source-boundcurrent/target successor。原P00C3→C5→C6、0/8、所有runtime與發布授權不變。
