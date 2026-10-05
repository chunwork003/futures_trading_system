# Exact IC01 CODEX handoff — manual trigger only

Fetch origin/master fresh. Execute only the first invocation bound to:
- Work Order: WO-AUTO-IMP-002-IC01-01
- Execution: EXEC-AUTO-IMP-002-IC01-20261005T150733Z
- Authorization: AUTH-AUTO-IMP-002-IC01-01
- Branch: auto/WO-AUTO-IMP-002-IC01-01
- Consumed commit: 8a4222d79f257c7e8b1311ffcf43d0b6df7a3e1b

Read CURRENT_CODEX.yaml and its exact work-order/authorization/eligibility/reservation/writer-lock/dispatch pointers. Prove steps 1–9, owner identity, clean worktree, no existing completion/conflicting claim, baseline chain, scope, provider hard-block and forecast before editing. CONSUMED is binding for this reserved first invocation only, never redispatch permission. Stop on provider denial/spend control/model or executor identity drift.

Assemble branch from fresh master plus ONLY four exact blobs in baseline_assembly; do not copy old control-plane artifacts. Record assembly commit SHA. This is baseline assembly, not correction. Only automation/engine/reentry.py and tests/automation/test_reentry.py may differ from assembled baseline. Manifest/test_manifest must retain exact blobs.

Goal: Separate non-candidate state/status resolution from READY deep binding validation; stabilize candidate tests independently of mutable CURRENT while preserving all RF01/RF02 fail-closed checks.
Read routing_contract and stable_fixture_strategy. Do not weaken RF01/RF02 checks or mutate consumed authority. Build self-contained valid READY fixture; prove positive route=CODEX_EXECUTION_CANDIDATE and execution_allowed=false before negative matrices. Separate current/post-execution state cases; missing candidate-only bindings must STOP.

Run minimum three pre-fix compatibility groups, implement, impacted subset until clean, one complete reentry+manifest targeted pass, one full regression with actual DB/broker disabled, diff-check, exact two-file correction/protected blobs verification. Budget=1 bounded impacted-test correction cycle; unplanned expensive cycle => STOP to WORK.

Record all exact SHAs, test commands/exits/timings, scope, retries/correction cycles, raw provider before/after when available, execution_cost_actual and execution task_profile/context_profile (planning context profile is provenance, not actual CODEX reads). Token telemetry unavailable => NOT_AVAILABLE/PENDING external extraction under existing contract, never fabricated EXACT. Forecast PROVISIONAL P50 350k/P75 900k/P90 2.5M; KEEP_COHESIVE.

Push durable completion evidence; status COMPLETED_PENDING_REVIEW. STOP. No merge/acceptance/RF03/AUTO-IMP-003 or next package. WORK intake→token finalization→reconciliation→fresh-context compatibility review→fresh-master integration verification→acceptance→closure.
