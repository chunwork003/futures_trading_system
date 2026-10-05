# AUTO-IMP-002 — AUTHORIZED / EXECUTION ELIGIBILITY PENDING

Work order: WO-AUTO-IMP-002-01  
Authorization: AUTH-AUTO-IMP-002-01  
Package: AUTO-IMP-002  
Branch: auto/WO-AUTO-IMP-002-01

Exact source scope:
- automation/engine/manifest.py
- automation/engine/reentry.py
- tests/automation/test_manifest.py
- tests/automation/test_reentry.py

Goal:
Implement Git-blob manifest integrity verification and read-only unified re-entry snapshot resolution.

Required verification:
- Git blob hash verification
- CRLF counterexample
- status-only no execution
- repository answer prevents re-ask
- targeted tests
- full regression
- git diff --check
- exact four-file scope

Stability rules:
- strict order
- resume before new
- no quota backfill
- no queue reorder
- no parallel execution
- no runtime/broker/DB/migration/LIVE/production

Current blocker:
Fresh execution eligibility is required before claim. Check BOTH 5H and weekly quota windows using current provider-native evidence. The frozen 80% normalized fallback is not applicable to this MEDIUM-risk / P90 44k package. Do not invent a replacement threshold and do not convert token forecast to provider percentage.

If no compatible provider-native quota forecast/gate exists:
STOP and route quota decision. Do not claim the branch.

If all execution gates later become PASS:
create one durable claim, execute exact scope, record per-work-order evidence/telemetry, end at COMPLETED_PENDING_REVIEW. AUTO-IMP-003 remains NOT_AUTHORIZED.
