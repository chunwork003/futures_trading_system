# AUTO-IMP-002 RF01 — READY_FOR_CODEX

Current bounded correction:
- work order: WO-AUTO-IMP-002-RF01-01
- authorization: AUTH-AUTO-IMP-002-RF01-01
- correction: AUTO-IMP-002-RF01
- finding: AUTO-IMP-002-REVIEW-BINDING-01
- execution: EXEC-AUTO-IMP-002-RF01-20261005T093900Z
- source candidate: eccbe997fe4f9f2a9da06026d75df11af9c3a937

Exact source scope:
- automation/engine/reentry.py
- tests/automation/test_reentry.py

Protected unchanged:
- automation/engine/manifest.py
- tests/automation/test_manifest.py

Single-use lifecycle is already durably materialized:

eligibility:
automation/work_orders/AUTO-IMP-002-RF01.eligibility.json

writer lock:
automation/runs/EXEC-AUTO-IMP-002-RF01-20261005T093900Z/writer_lock.yaml

reservation:
automation/runs/EXEC-AUTO-IMP-002-RF01-20261005T093900Z/reservation.yaml

pre-dispatch recheck:
automation/runs/EXEC-AUTO-IMP-002-RF01-20261005T093900Z/pre_dispatch_recheck.json

dispatch:
automation/runs/EXEC-AUTO-IMP-002-RF01-20261005T093900Z/dispatch.yaml

handoff:
automation/runs/EXEC-AUTO-IMP-002-RF01-20261005T093900Z/handoff.yaml

Authorization state:
CONSUMED

Quota:
exact RF01 bounded pilot waiver applies.
Telemetry is record-if-available.
Provider hard block still STOP at executor entry.

Executor requirements:
- fresh fetch origin/master
- verify CURRENT == this execution and authorization is CONSUMED
- verify no existing RF01 branch/evidence, or resume only the same execution
- create the exact execution branch from source candidate SHA if absent
- edit only the two authorized files
- counterexample-first negative binding matrix
- targeted tests
- full regression
- git diff --check
- exact two-file scope
- completion evidence
- STOP at COMPLETED_PENDING_REVIEW

Do not:
- modify manifest.py or test_manifest.py
- rerun original AUTO-IMP-002
- create another execution identity
- self-accept or merge
- start AUTO-IMP-003
