# Automation Implementation Program V1 — Compiled Candidate

```text
PROGRAM_ID = AUTO-IMP-PROGRAM-V1
SOURCE_FREEZE_HEAD = 52921ae3f205ef2eec4306e84ff92d4cd9cdeab3
STATUS = COMPILED_CANDIDATE_NOT_AUTHORIZED
IMPLEMENTATION_AUTHORIZATION = NOT_AUTHORIZED
CODEX_EXECUTION = NOT_AUTHORIZED
NEXT_ROUTE = AUTOMATION_IMPLEMENTATION_PROGRAM_REVIEW
```

## Strategy

Use strangler / dual-run migration. Preserve existing `codex_level3a_scheduler_v0/v1/v2.ps1` and `codex_level3a_result_intake_v1.ps1` as reference/regression fixtures. New automation is shadow/read-only first. No package in this program is authorized by compilation.

## Near-horizon exact packages

- `AUTO-IMP-001` — Machine Contract Models and YAML Loader — wave `W1_FOUNDATION_SHADOW` — depends `NONE` — P90 `36000` tokens — `PLANNED_NOT_AUTHORIZED`.
- `AUTO-IMP-002` — Manifest Integrity and Unified Re-entry Snapshot Resolver — wave `W1_FOUNDATION_SHADOW` — depends `AUTO-IMP-001` — P90 `44000` tokens — `PLANNED_NOT_AUTHORIZED`.
- `AUTO-IMP-003` — Authorization Lifecycle Resolver and State Transition Guard — wave `W1_FOUNDATION_SHADOW` — depends `AUTO-IMP-001` — P90 `52000` tokens — `PLANNED_NOT_AUTHORIZED`.
- `AUTO-IMP-004` — Quota Admission Evaluator and Forecast Fallback — wave `W1_FOUNDATION_SHADOW` — depends `AUTO-IMP-001` — P90 `50000` tokens — `PLANNED_NOT_AUTHORIZED`.
- `AUTO-IMP-005` — Negative Assertion Harness — wave `W1_FOUNDATION_SHADOW` — depends `AUTO-IMP-002, AUTO-IMP-003, AUTO-IMP-004` — P90 `34000` tokens — `PLANNED_NOT_AUTHORIZED`.
- `AUTO-IMP-006` — Historical GAP-08 Replay Harness — wave `W2_REPLAY_AND_DUAL_RUN` — depends `AUTO-IMP-005` — P90 `60000` tokens — `PLANNED_NOT_AUTHORIZED`.
- `AUTO-IMP-007` — Legacy Scheduler V2 Dual-Preflight Comparator — wave `W2_REPLAY_AND_DUAL_RUN` — depends `AUTO-IMP-002, AUTO-IMP-003, AUTO-IMP-004, AUTO-IMP-006` — P90 `58000` tokens — `PLANNED_NOT_AUTHORIZED`.
- `AUTO-IMP-008` — Result Intake, Execution Identity and Telemetry Normalization — wave `W2_REPLAY_AND_DUAL_RUN` — depends `AUTO-IMP-001, AUTO-IMP-003` — P90 `58000` tokens — `PLANNED_NOT_AUTHORIZED`.
- `AUTO-IMP-009` — Canonical Shadow Preflight CLI — wave `W3_CANONICAL_SHADOW_PREFLIGHT` — depends `AUTO-IMP-007, AUTO-IMP-008` — P90 `48000` tokens — `PLANNED_NOT_AUTHORIZED`.

## DAG

```text
001 -> 002
001 -> 003
001 -> 004
002 + 003 + 004 -> 005
005 -> 006
002 + 003 + 004 + 006 -> 007
001 + 003 -> 008
007 + 008 -> 009
```

## Deferred milestones

After `AUTO-IMP-009` acceptance only: canonical result-intake migration -> controlled Level 3A-2 single-use dispatch -> 2–3 stable packages/cohort -> Level 3B -> Level 3C -> Level 4 shadow -> Level 4 controlled -> Level 5 observe/analyze -> Level 5 controlled improvement.

## Hard boundaries

- Runtime Authorization remains `NOT_AUTHORIZED`.
- Next trading mainline GAP remains `NOT_AUTHORIZED`.
- No DB/migration execution.
- No broker network or LIVE/production action.
- No unattended AUTO-3 path.
- Automated CODEX dispatch requires a measurable execution channel and exact telemetry binding.
- Quota reset/time does not directly resume execution.
- Metrics may propose policy changes but may not activate them.
- One active runtime writer only.

## Review

This materialization compiles the program but does not authorize implementation. Independent review should verify frozen-architecture traceability, DAG/dependencies, package boundaries, side-effect envelopes, telemetry/quota gates, replay plan, and absence of implicit CODEX/runtime authorization.
