# Skill: single-use-lifecycle-guard

Architecture1.2 ACTIVE after accepted fresh review and WORK materialization. Canonical active successor section below supersedes predecessor procedure pointers; historical artifacts grant no current execution authority. No automatic dispatch or next package authority.


Status: SHADOW / MANDATORY PROCEDURE MEMORY

Purpose:
Prevent executor start unless the reviewed AuthorizationLifecycleV1_1 single-use sequence has been durably materialized.

Trigger:
BEFORE_HANDOFF / BEFORE_CLAIM / BEFORE_EXECUTOR_START / BEFORE_RESULT_INTAKE

Canonical policy:
automation/policies/authorization_lifecycle.v1_1.yaml

Required ordered proof:
1. FRESH_AUTHORITY_RESOLUTION
2. FRESH_ELIGIBILITY_EVALUATION
3. ACQUIRE_GLOBAL_RUNTIME_WRITER_LOCK
4. ALLOCATE_EXECUTION_ID
5. DURABLY_CREATE_EXECUTION_RESERVATION
6. STATE_TO_RESERVED
7. RECHECK_LOCK_HEAD_AND_BINDING
8. MARK_DISPATCH_COMMITTED
9. STATE_TO_CONSUMED
10. INVOKE_EXECUTOR

Hard rules:
- A branch or claim commit alone is NOT a substitute for reservation / RESERVED / dispatch committed / CONSUMED.
- Manual trigger is only a wake event; it does NOT bypass the lifecycle.
- No implementation source edit may begin before durable proof of steps 1-9 exists.
- If the current mechanism cannot materialize the required lifecycle, STOP and route to governance/control-plane work.
- Do not fabricate missing historical lifecycle events after execution.
- Existing execution with ambiguous lifecycle => RECONCILIATION_REQUIRED.
- CONSUMED execution => NO_REDISPATCH.

Inputs:
- current authorization
- work order
- execution identity if allocated
- reservation artifact/pointer
- dispatch artifact/pointer
- current lifecycle state
- writer-lock evidence
- current master HEAD

Output:
PASS_READY_TO_INVOKE_EXECUTOR
or
FAIL_CLOSED_<REASON>

Must not:
- grant authority
- create substitute authority
- rewrite a nonconforming historical run as conforming
- auto-reexecute
- expand source scope


## Execution Capacity / Resume V2 — ACTIVE procedure

Successor policy pointers (ACTIVE after accepted review and WORK materialization):
- automation/policies/execution_capacity_policy.v2.yaml
- automation/policies/authorization_lifecycle.v1_1.yaml
- automation/policies/development_state_machine.v2.yaml
- automation/policies/development_entry_protocol.v2.yaml
- automation/telemetry/execution_cost_contract.v2.yaml
- automation/specs/work_cost_accounting.v2.yaml
- automation/specs/negative_assertions.v2.yaml

Active master architecture is1.2 after reviewed materialization; presence of these files grants no execution authority. V2 evaluation surface: automation.engine.execution_capacity. Control plane assembles exact fresh evidence; evaluator performs no IO/invocation or authority mutation.

EXECUTION_COST_GATE != PROVIDER_AVAILABILITY_GATE. Per-WO P50/P75/P90 demand is primary; legacy static package forecasts are historical planning inputs. V2 has no fixed remaining-percent floor or normalized token fallback. Preserve cached/uncached/input/output/reasoning features. Exact task-bound local usage remains EXACT actual usage, not billing. Provider percentages are immutable shared-account proxy and may inform qualified capacity calibration. Derived capacity/token values are PROVISIONAL_ESTIMATE or CALIBRATED_ESTIMATE, never EXACT; no unsupported constant linear conversion or identical feature weights. Require minimum comparable samples plus identity, attribution, reset and uncertainty qualification; count alone never upgrades confidence.

Actual provider denial wins. Running denial checkpoints SAME execution as PAUSED_PROVIDER_LIMIT with WO/authorization/reservation/dispatch/branch/delta/budget/tests/telemetry/writer lineage. Pause is not source failure or correction-budget consumption. Recovery wakes only: RESUME_PENDING_REVALIDATION -> fresh head, scope, policy, authority, invocation, reservation, dispatch and writer/provider checks -> RESUME_SAME_EXECUTION or STOP_TO_WORK. Safe lock reacquisition needs verified ownership lineage and no competing owner. No new WO/execution/authorization/reservation/dispatch/budget for resume. CONSUMED redispatch remains DENIED; already-invoked same-execution continuation is distinct.

HISTORICAL_PHASE_SNAPSHOT != CURRENT_LIFECYCLE_PROJECTION. Never reinterpret pre-reservation snapshot flags as current truth. Current projection must agree with all durable lifecycle fields; contradiction -> FAIL_CLOSED_RECONCILIATION_REQUIRED; no event fabrication or historical rewriting.

Safety/governance -> unfinished resumable execution -> pending result/review/integration -> exact authorized new work. Unfinished execution blocks new dispatch. Every provider interruption triggers WORK_FORECAST_CAPACITY_REVIEW; this feedback grants no authority, does not block legal resume, and must be materialized before new work after interrupted completion. Review PASS != Integration PASS != materialized acceptance. IVF01 Rev1 stays BLOCKED_NO_EXECUTION_NO_WAIVER; after this reviewed Architecture1.2 activation its projection is ARCHITECTURE_BASELINE_CHANGED_RECOMPILE_REQUIRED; never rewrite/reuse Rev1. AUTO-IMP-003 remains NOT_AUTHORIZED. All runtime/broker/DB/migration/LIVE/production effects DENIED.
