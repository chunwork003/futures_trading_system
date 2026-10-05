# AUTO-IMP-002 RF01 — AUTHORIZED / ELIGIBILITY PENDING

Current bounded correction:
- correction: AUTO-IMP-002-RF01
- work order: WO-AUTO-IMP-002-RF01-01
- authorization: AUTH-AUTO-IMP-002-RF01-01
- finding: AUTO-IMP-002-REVIEW-BINDING-01
- source candidate: eccbe997fe4f9f2a9da06026d75df11af9c3a937

Exact source scope:
- automation/engine/reentry.py
- tests/automation/test_reentry.py

Protected unchanged:
- automation/engine/manifest.py
- tests/automation/test_manifest.py

Correction goal:
Make resolve_reentry fail closed for the full reviewed cross-artifact pointer/identity/revision/state/effect/profile/dependency binding matrix.

Current blocker:
Fresh quota / execution eligibility is unresolved.

Important lifecycle rule:
NO source edit and NO Codex invocation before durable:
reservation → RESERVED → dispatch committed → CONSUMED.

A branch/claim alone is insufficient.

Do not:
- reuse the previous AUTO-IMP-002 quota waiver
- reserve or dispatch before eligibility PASS
- edit source now
- start AUTO-IMP-003

Next:
AUTO_IMP_002_RF01_EXECUTION_ELIGIBILITY
