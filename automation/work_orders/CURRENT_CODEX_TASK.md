# READY — 新授權之 AUTO-IMP-001 bounded correction

Work order: WO-AUTO-IMP-001-CORR-02
Correction: AUTO-IMP-001-YAML-COMPAT-RF02
Fresh authority: automation/work_orders/AUTH-AUTO-IMP-001-CORR-02-01.yaml
Control-plane / code baseline: db82001369017f42acd1887320f6350fa34634f1
Branch: auto/WO-AUTO-IMP-001-CORR-02
Status: READY_FOR_CODEX
handoff_ready: true
New semantic correction budget: 1

Codex scheduled Executor 必須自行 fetch origin/master，讀取 CURRENT_CODEX.yaml、此 exact work order 與 fresh authority。READY 只代表 handoff 已發布；claim 前重新驗證所有適用 execution gates。不得使用舊 CONSUMED authorization、舊 pilot 或其 quota exemption。本次 quota admission 僅依下述新 exact amendment。

修正 RF01-REVIEW-MERGE-01 與 RF01-REVIEW-SAFE-TAG-02，保留合法 YAML merge-key、merge precedence、alias 與 recursive alias 相容性；所有 SafeLoader mapping construction（含 nested !!set）拒絕 duplicate explicit keys。不得把合法 merge-derived precedence collisions 當成 explicit duplicate keys，也不得重新設計 YAML contract。

唯一 implementation write scope：
- automation/engine/yaml_io.py
- tests/automation/test_contracts.py

Current master 尚未合入 RF01 source。從新 baseline 完成完整修正；既有 RF01 implementation 2a8974acbb7319ce55b3d7fb88737ad027061244 僅供 source reference，禁止 merge／cherry-pick 舊 branch metadata。

Required verification：
- valid YAML merge without duplicate explicit keys
- legal merge precedence, including explicit override and merge sequence precedence
- duplicate explicit keys rejected with AutomationYamlError
- nested duplicate mappings rejected, including mappings in sequences
- alias keys compatibility
- recursive aliases compatibility preserved without YAML contract redesign
- nested !!set duplicate entries rejected
- unsafe-tag regression (unsafe object construction rejected)
- representative canonical contract loading
- targeted tests
- full regression
- git diff --check
- exact implementation and metadata scope verification

Claim：重新確認新 branch/evidence 不存在、沒有 competing writer、authority exact binding 與 fresh gates PASS；成功 non-force push 一個 unique empty claim commit 才能開始 source edit，該 durable claim 單次 consume 新授權。已存在 branch 或 push rejected 必須 STOP，不得 redispatch。

完成：one implementation commit → required tests/scope/diff checks → completion JSON automation/work_orders/executions/WO-AUTO-IMP-001-CORR-02.json → evidence commit/push → COMPLETED_PENDING_REVIEW → STOP。Completion 記錄 exact SHAs、commands/exit codes、protected blobs、semantic cycle、tooling retries、token usage 或 NOT_AVAILABLE。任何 verification failure／budget exhaustion → HUMAN_DECISION_REQUIRED。不得 ACCEPTED、auto merge、再開 RF 或啟動 AUTO-IMP-002。

## Exact bounded quota amendment — AMEND-AUTO-IMP-001-CORR-02-QUOTA-01

Authority: automation/work_orders/AMEND-AUTO-IMP-001-CORR-02-QUOTA-01.yaml
quota_admission_gate: WAIVED_FOR_BOUNDED_AUTOMATION_PILOT
Updated at: 2026-10-05T05:05:48Z

下次 wake-up 必須重新 fetch origin/master 並重新讀取 amendment、CURRENT_CODEX 與 exact work order。僅本 scheduled executor / work order 不套用 manual-executor 80% normalized fallback；不得將 29% < 80% 判為本 work order policy failure。不要求 fresh human Usage confirmation 或 minimum remaining percentage。Quota/token telemetry 可取得則記錄，否則 NOT_AVAILABLE；不得因此阻塞 admission。

Frozen quota policy 不變；provider 實際強制限制仍有效。舊 quota STOP 不是新 eligibility snapshot。重新驗證 branch/evidence/writer/baseline/scope/authority/single-use 等所有其他 gates 後才可 claim。Correction budget 仍為 1，未消耗；未授權下一 package、額外 RF 或 side effects。
