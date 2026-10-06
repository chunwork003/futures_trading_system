# CURRENT PROCEDURE — Architecture1.2.2 / capacity2.2 FINAL

Active manifest/current pointers govern. automation/policies/execution_capacity_policy.v2_2.yaml supersedes older capacity/promotion/budget clauses only. Weekly PLANNING_AND_SCHEDULING_SIGNAL_ONLY neverstatisticalexecutionblocker. MANUAL exact-authorized allrisk uses PRIMARY_5H safeRemaining=max(0,100-used-1), rollingminimum/P25 last20 sameprovider/account/limit; compareP75, P90 advisory. UNKNOWN5H=>ALLOW_WITH_WATCH; fitP75=>ALLOW_WITH_WATCH; knownbelowP75=>WAIT_5H_CAPACITY. Actual ordinary/hard/rate/spend denial=>WAIT_PROVIDER_AVAILABLE. Model/task/workspace/executor/clientpolicy metadata, no calibrationbootstrap/probes. CONTROLLED_AUTO DISABLED; actualproviderPASS/usable5HP90/5recentacceptedmanualcurrentcontroller exacttokens/zero duplicate/fabricatedresume/writerconflict/no unresolvedHIGHCRITICAL/independentcontrollerPASS/Owneractivation. Weekly neverstatisticalCONTROLLED_AUTOgate.

Main WO-AUTO-GOV-PROGRAM-1_2-ORCH-01 implementationbudget2 and separate reviewfixbudget2 per automation/governance/decisions/EXECUTION-CAPACITY-FINAL-LIVENESS.owner.json. Ordinaryinscopeconformancefix usesremainingbudget; architecture/authority/scope/sideeffectexpansion or exhaustion=>STOP_TO_OWNER. Reviewfix usesboundfinding/effectivecandidate+fresh exact childsingleuse authority under existingOwnerconditionalgrant, same logicalWO; neverreuseCONSUMEDparent; targeted then atmostone finalfullwhenwarranted, narrowindependentre-review. Liveness complete5Hperiod/reset statisticalonlyblock+recordedproviderPASS=>non-authority recent5/20/forecast/context/retry optimization; no gateoverride/uniformquotapacing/authority. Lifecycle order and sameinvoked resume unchanged, no duplicatewriter/dispatch, queue/eventWAKEonly, review!=integration!=acceptance. Main evaluator/tests source update pending in same21files, previoussource not2.2 admission authority; WORK governedfinalpolicyfreshdecisionevidence allowsbounded implementationbootstrap. No automaticCODEX.

## HISTORICAL PREDECESSOR PROCEDURES — preserve noncapacity safety; final2.2 capacity/budget above prevails

# CURRENT PROCEDURE — Architecture1.2.1 / capacity2.1

Fresh manifest determines active policies. automation/policies/execution_capacity_policy.v2_1.yaml supersedes predecessor capacity/admission clauses only. Exact local reported tokens primary; provider percentages coarse proxy; derived total-token ratio is ROLLING_CAPACITY_ESTIMATE never EXACT task cost/billing. No fixed80%/40k or coefficient/probe/bootstrap gate. Quota pool provider/account/limit/window only; model/workspace/executor/clientpolicy/taskclass metadata. Same reset positive delta ratios, delta0/reset-crossing retain tokens exclude ratio; overlaps NOISY_SHARED_USAGE reducedconfidence. Last20 usable, n1-4minimum, n>=5linearP25, subtract1pp. Manual exactauthorized allrisk providerPASS unknown=>ALLOW_WITH_WATCH; anyknownwindow belowP90=>WAIT_PROVIDER_CAPACITY. Actual denial=>WAIT_PROVIDER_AVAILABLE. CONTROLLED_AUTO remains DISABLED; at least5 accepted manual currentcontroller executions with strict exacttokens, rolling evidence for both exposedwindows, zero duplicate/fabricatedresume/writerconflicts, no unresolvedgovernance anomaly, independentcontrollerPASS, explicitOwner activation.

Single-use lifecycle/resume/writer/scope/authority gates unchanged; queue/event creates noauthority; wakeonly. No newexecution/reservation/dispatch for alreadyinvoked sameexecution resume. Current predecessor execution_capacity source is not2.1 admission implementation yet; main21file candidate must update evaluator/tests and all current kernel pointers before cohesive source review/acceptance. WORK preexecution uses reviewed2.1 governance policy plus exact deterministic evidence; never reuses predecessor cost_gate projection. No automatic CODEX invocation.

## Predecessor procedure text — preserved navigation/history; capacity2.1 above prevails

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


## Historical predecessor capacity procedure — superseded ONLY for capacity by2.1

### Historical1.2 procedure, current capacity clauses below prevail

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
