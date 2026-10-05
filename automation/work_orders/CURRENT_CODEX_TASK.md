# AUTO-IMP-002 RF02 — READY_FOR_CODEX / MANUAL ONLY

Work order: WO-AUTO-IMP-002-RF02-01
Execution: EXEC-AUTO-IMP-002-RF02-20261005T125807Z
Authorization: AUTH-AUTO-IMP-002-RF02-01 / CONSUMED
Source candidate: 0c64a9f509ba27c1bc1bad139681951e2f8c2775
Branch: auto/WO-AUTO-IMP-002-RF02-01
Consumed lifecycle commit: 50184f062ad3eb6522ff7717cfe9915a8152bbc9
Handoff: automation/runs/EXEC-AUTO-IMP-002-RF02-20261005T125807Z/handoff.yaml
Work Order: automation/work_orders/WO-AUTO-IMP-002-RF02-01.yaml
Eligibility: automation/work_orders/AUTO-IMP-002-RF02.eligibility.json
Forecast: automation/work_orders/forecasts/AUTO-IMP-002-RF02.planning.json (unchanged)
Writer lock: automation/runs/EXEC-AUTO-IMP-002-RF02-20261005T125807Z/writer_lock.yaml / HELD

Manual CODEX invocation only. WORK has NOT invoked CODEX. This is the first invocation of the existing consumed reservation, not redispatch. Fresh fetch origin/master; re-read exact pointers and canonical lifecycle guard. Verify reservation, dispatch committed, CONSUMED, lock ownership and source candidate. If evidence/branch already exists, follow same execution resume rules; never duplicate claim or start another writer. Recheck provider hard block: STOP on refusal. Quota waiver ended at consumption; admission was recorded in this execution's reservation, and waiver reuse is DENIED.

Create exact execution branch from source_candidate_sha, using current master as control-plane evidence only. Do not merge candidate or any unrelated source into master. Implementation writes only:
- automation/engine/reentry.py
- tests/automation/test_reentry.py

Correct only:
- WORK side_effects runtime/broker/db/migration/live/production must remain DENIED
- CURRENT auto_imp_003_authorized=false must agree with WORK next_package package_id=AUTO-IMP-003 and authorization=NOT_AUTHORIZED
- CURRENT and WORK quota_gate.provider_hard_block must both remain STOP

Preserve RF01 checks, read-only/status-only behavior, manifest behavior and supplemental metadata compatibility. No source/scope/architecture expansion.

Efficiency: only 3 minimum pre-fix counterexamples; no full negative matrix or new Git-backed semantic matrix before fix. Impacted subset until clean, then one complete test_reentry pass, then one full regression. git diff --check; exact two-file scope and protected manifest blobs unchanged. No unplanned expensive cycle without bounded WORK rationale.

Record exact SHAs/lifecycle identity, actor start/end, raw 5H/weekly before/after evidence when available, test commands/exit codes/timings/cycles, scope and cost actuals. Telemetry unavailable => NOT_AVAILABLE; no percentage-to-token conversion or billing claim. Publish durable completion evidence under exact work-order/execution metadata paths. COMPLETED_PENDING_REVIEW -> STOP. No acceptance, auto merge, RF03 or AUTO-IMP-003. Budget remains 1, source edits not started.
