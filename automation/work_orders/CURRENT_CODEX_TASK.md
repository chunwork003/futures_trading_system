# AUTO-IMP-001 bounded correction — Codex handoff

此文件只交接 WO-AUTO-IMP-001-CORR-01，不啟動 Codex、不重授權、不重派原 authorization、不授權 AUTO-IMP-002。

## Exact goal / authority
所有 mapping depth 的 duplicate YAML key 必須 fail closed 並拋出 AutomationYamlError。
Reviewer verdict = REVIEW_FIX_REQUIRED；來源為使用者本次明確提供的 authoritative reviewer verdict。
原 implementation = 21a5a66e03e9918d0a4ddd631707a29979b29949。
Result intake = d09ce94692c27bf844c3d0ce245710941ddf1294。
Rehydrated master = a0ca84d4744e7fde78d3215f24ba5e89914f6784。
AUTH-AUTO-IMP-001-01 = CONSUMED，禁止 reauthorize / redispatch。
Repository 先前 observation 尚標示 reviewer MISSING；本交接保存新 verdict 的來源，不宣稱 reviewer PASS 或 package accepted。

## Execution start rules
先讀 GitHub 最新 master、CURRENT_STATE、manifest/policies、work orders、run/result/handoff/telemetry 與 open branches/PRs。
本次 code_base_sha 加上只修改 work-order 文件的發布 commit，必須能精確連結；記錄實際 execution_start_sha。
若後續 master 或 authority 改變，須重新 bounded revalidation，禁止盲目沿用。
Publisher 必須先將同一工作單 durable claim 為 RUNNING 並確認 exclusive writer；任一其他 RUNNING 或 READY 工作單立即 STOP。
開始前重新檢查 frozen quota policy、fresh quota evidence、execution binding、writer ownership、telemetry gate；舊 snapshot 不可當 admission。
READY_FOR_CODEX / handoff_ready 代表交接完成，不代表已執行 admission 或 automatic dispatch。
Executor 不得為執行本單修改原 authorization 或 protected evidence。

## Exact implementation write scope
- automation/engine/yaml_io.py
- tests/automation/test_contracts.py

其他檔案均不得由 correction executor 修改。工作單 claim/result metadata 由 Planner / Publisher 另行處理，僅在 automation/work_orders/**。

## Exact tests
- top-level duplicate mapping key：assert AutomationYamlError。
- nested duplicate mapping key：assert AutomationYamlError。
- 驗證任意深度 mapping（含容器中的 mapping）仍套用相同 rejection boundary；維持 safe YAML 與既有 loader contracts。
- Targeted: python -m pytest tests/automation/test_contracts.py -q -p no:cacheprovider
- Full regression: python -m pytest -q -p no:cacheprovider
- git diff --check
- git diff --name-only <execution_start_sha> HEAD：只允許上述兩檔。
不得把環境限制描述成程式缺陷，亦不得把未執行測試描述成 PASS。

## Correction budget
原上限 2、已用 semantic cycle 1、剩餘 1；本單最多使用剩餘 1 次。
不得自行重設預算；耗盡或需要再一輪時 STOP，交回 HUMAN_DECISION_REQUIRED。

## Protected scope / side effects
automation/engine/contracts.py 明確禁止修改。
原 authorizations、Master Architecture、manifest、policies、packages、run artifacts、docs、其他 implementation source 均 protected。
只允許 bounded source edit、offline local tests、單一 correction branch commit/push/draft PR。
禁止 broker、DB access/migration、LIVE、production、credentials、runtime operation、自動 dispatch、下一 package。

## STOP conditions
任一 concurrent writer / RUNNING / second READY；預算不明或耗盡；verdict 改變；
任何 architecture / authority / scope / side-effect expansion；fresh gates 未通過；
需 redispatch CONSUMED authorization；required tests 在剩餘 cycle 後失敗；
修改 protected scope；涉及未決 YAML 公開語意；master 漂移未重新驗證。
Known AUTO-IMP-001-SUPERVISOR-QHASH-01 為歷史 quota digest 的 CRLF/Git blob 差異，保留未解決。
不得修補 authorization 或 reservation；若該問題阻止 fresh execution binding，STOP 並回報 HUMAN_DECISION_REQUIRED。

## Git / branch / PR rules
由 verified master 建立 codex/auto-imp-001-dupkey-rf01，乾淨 isolated checkout。
只提交上述兩檔，一個 bounded correction commit；push branch，建立 draft PR，base=master。
禁止 force push / rewrite history / executor direct master push / automatic merge。
完成後交回 Planner / Publisher 進行 result intake，狀態 COMPLETED_PENDING_REVIEW；STOP 等待 independent review。
不得開始 AUTO-IMP-002，不得宣稱 accepted、production ready 或 runtime conformance。

## Required completion evidence
exact execution_start_sha、implementation commit SHA、exact changed files、contracts.py blob unchanged；
duplicate tests、targeted/full results 與 exit codes；diff check；worktree evidence；
semantic cycles used / remaining；fresh quota before/after / available telemetry（缺漏標示 unavailable）；
draft PR URL、review handoff、未解決限制。
完成證據由 result intake 保存於 automation/work_orders/**，不覆寫歷史 runs 或原 authorization。
