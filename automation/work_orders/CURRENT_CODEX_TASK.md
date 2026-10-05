# AUTO-IMP-002 RF02 — AUTHORIZED / QUOTA BLOCKED

Work order: WO-AUTO-IMP-002-RF02-01
Authority: automation/authorizations/AUTH-AUTO-IMP-002-RF02-01.v1.yaml
Eligibility: automation/work_orders/AUTO-IMP-002-RF02.eligibility.json
Source candidate: 0c64a9f509ba27c1bc1bad139681951e2f8c2775
Forecast: automation/work_orders/forecasts/AUTO-IMP-002-RF02.planning.json (unchanged)
Status: BLOCKED
handoff_ready: false

No CODEX invocation or source edit is permitted yet.
Remaining blocker: RF02_QUOTA_ADMISSION_UNRESOLVED.
The RF01 exact waiver is consumed and cannot be reused. Resolve fresh compatible quota admission or a new explicit exact RF02 quota decision first.

Exact source scope:
- automation/engine/reentry.py
- tests/automation/test_reentry.py

Prepared checks:
- WORK side_effects runtime/broker/db/migration/live/production must remain DENIED
- CURRENT auto_imp_003_authorized=false must agree with WORK next_package package_id=AUTO-IMP-003 and authorization=NOT_AUTHORIZED
- CURRENT and WORK quota_gate.provider_hard_block must both remain STOP

Preserve RF02 preparation efficiency contract and forecast bytes. Only 3 pre-fix counterexamples; impacted subset until clean; one complete targeted pass; one full regression. Required lifecycle guard steps 1-9 must be durable before any source edit. No branch-only substitute. Do not invoke CODEX, redispatch RF01, authorize AUTO-IMP-003 or expand scope.
Next: AUTO_IMP_002_RF02_QUOTA_ADMISSION_DECISION
