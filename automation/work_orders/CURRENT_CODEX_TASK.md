# CURRENT CODEX Task — BLOCKED / DO NOT INVOKE

Work Order: WO-AUTO-GOV-PROGRAM-1_2-ORCH-01
Package: AUTO-GOV-PROGRAM-1_2-ORCHESTRATION
Architecture: 1.2 ACTIVE
Authority: AUTH-AUTO-GOV-PROGRAM-1_2-ORCH-01 AUTHORIZED, not consumed
State: BLOCKED
handoff_ready: false
Sole blocker: QUALIFIED_CAPACITY_REQUIRED
Route: WORK_CAPACITY_REVIEW

Read exact CURRENT -> automation/work_orders/WO-AUTO-GOV-PROGRAM-1_2-ORCH-01.yaml -> automation/packages/AUTO-GOV-PROGRAM-1_2-ORCHESTRATION.plan.yaml -> automation/governance/decisions/AUTO-GOV-PROGRAM-1_2-ORCHESTRATION.owner.json and exact forecast/eligibility pointers. Complete19-file scope and49-case matrix are in WO. This is one cohesive Program V2 / queue / event / deterministic route / dedupe / forecast / promotion implementation; no separate architecture discussion remains.

No writer/execution/reservation/dispatch exists. This document is status-only, not executable handoff. Do not claim, invoke CODEX, consume authority, reuse any previous execution, execute IVF01 or authorize003. Only after qualified capacity and fresh all normal1.2 gates may WORK materialize new exact lifecycle for a manual trigger. Provider denial always STOP. MANUAL active; CONTROLLED_AUTO DISABLED; all runtime/broker/DB/migration/LIVE/production DENIED.
