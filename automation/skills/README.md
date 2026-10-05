# Automation Skills

Status: SHADOW SPECIFICATION

Precedence:
Governance > Work > Skill > Codex / Tool

Skills must not:
- grant authority
- expand implementation scope
- infer runtime authorization
- mutate quota or authorization policy
- auto-advance packages
- override canonical CURRENT state

Dynamic state sources:
- docs/CURRENT_STATE.md
- automation/work_orders/CURRENT_CODEX.yaml

Initial Shadow Skills:
- repo-reentry
- exact-binding-validator
- single-use-lifecycle-guard
- execution-efficiency-guard
- execution-cost-forecaster
- quota-snapshot-recorder
- reviewer-packet-builder

Deferred until lifecycle foundation is stable:
- queue-resolver
- resume-resolver

Later:
- context-compiler
- work-cluster
- quota-calibrator
- optimization-analyzer

Critical execution rule:
- single-use-lifecycle-guard is mandatory procedural memory before any bounded executor start.
- a claim branch/commit alone never proves AuthorizationLifecycleV1 conformance.

Efficiency rule:
- execution-efficiency-guard is the canonical home for test/context/quota growth controls; do not duplicate those procedures into role kernels.


Forecast loop:
- WORK creates the exact cost forecast before executable handoff.
- CODEX records actual runtime/test/quota observations.
- WORK enriches local token telemetry, reconciles variance, and feeds one bounded optimization back into the next forecast.
