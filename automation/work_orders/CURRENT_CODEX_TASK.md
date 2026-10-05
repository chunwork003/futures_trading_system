# AUTO-IMP-002 — READY_FOR_CODEX

Work order: WO-AUTO-IMP-002-01  
Authorization: AUTH-AUTO-IMP-002-01  
Quota amendment: AMEND-AUTO-IMP-002-QUOTA-01  
Eligibility: automation/work_orders/AUTO-IMP-002.eligibility.json  
Branch: auto/WO-AUTO-IMP-002-01

Exact source scope:
- automation/engine/manifest.py
- automation/engine/reentry.py
- tests/automation/test_manifest.py
- tests/automation/test_reentry.py

Goal:
Implement Git-blob manifest integrity verification and read-only unified re-entry snapshot resolution.

Quota:
- exact package-specific pilot waiver is active
- fixed 80% fallback does not apply
- no invented replacement threshold
- record actor start/end time plus raw 5H/weekly before/after snapshots when available
- provider hard block still STOP
- telemetry unavailable alone does not block this exact pilot

Before claim:
- fresh fetch origin/master
- re-read authorization, amendment, CURRENT_CODEX, work order and eligibility
- verify no existing execution branch/evidence or conflicting writer
- verify only bounded control-plane drift since authorization
- revalidate all non-quota gates
- create one non-force durable claim only after gates PASS

Required verification:
- Git blob hash verification
- CRLF counterexample
- status-only no execution
- repository answer prevents re-ask
- targeted tests
- full regression
- git diff --check
- exact four-file scope

Finish:
- per-work-order completion evidence
- raw quota telemetry/timestamps if available
- COMPLETED_PENDING_REVIEW
- STOP
- AUTO-IMP-003 remains NOT_AUTHORIZED
