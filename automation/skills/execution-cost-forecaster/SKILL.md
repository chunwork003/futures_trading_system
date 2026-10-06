# CURRENT PROCEDURE — Architecture1.2.2 / capacity2.2 FINAL

Active manifest/current pointers govern. automation/policies/execution_capacity_policy.v2_2.yaml supersedes older capacity/promotion/budget clauses only. Weekly PLANNING_AND_SCHEDULING_SIGNAL_ONLY neverstatisticalexecutionblocker. MANUAL exact-authorized allrisk uses PRIMARY_5H safeRemaining=max(0,100-used-1), rollingminimum/P25 last20 sameprovider/account/limit; compareP75, P90 advisory. UNKNOWN5H=>ALLOW_WITH_WATCH; fitP75=>ALLOW_WITH_WATCH; knownbelowP75=>WAIT_5H_CAPACITY. Actual ordinary/hard/rate/spend denial=>WAIT_PROVIDER_AVAILABLE. Model/task/workspace/executor/clientpolicy metadata, no calibrationbootstrap/probes. CONTROLLED_AUTO DISABLED; actualproviderPASS/usable5HP90/5recentacceptedmanualcurrentcontroller exacttokens/zero duplicate/fabricatedresume/writerconflict/no unresolvedHIGHCRITICAL/independentcontrollerPASS/Owneractivation. Weekly neverstatisticalCONTROLLED_AUTOgate.

Main WO-AUTO-GOV-PROGRAM-1_2-ORCH-01 implementationbudget2 and separate reviewfixbudget2 per automation/governance/decisions/EXECUTION-CAPACITY-FINAL-LIVENESS.owner.json. Ordinaryinscopeconformancefix usesremainingbudget; architecture/authority/scope/sideeffectexpansion or exhaustion=>STOP_TO_OWNER. Reviewfix usesboundfinding/effectivecandidate+fresh exact childsingleuse authority under existingOwnerconditionalgrant, same logicalWO; neverreuseCONSUMEDparent; targeted then atmostone finalfullwhenwarranted, narrowindependentre-review. Liveness complete5Hperiod/reset statisticalonlyblock+recordedproviderPASS=>non-authority recent5/20/forecast/context/retry optimization; no gateoverride/uniformquotapacing/authority. Lifecycle order and sameinvoked resume unchanged, no duplicatewriter/dispatch, queue/eventWAKEonly, review!=integration!=acceptance. Main evaluator/tests source update is materialized in the current cohesive candidate; operational controller acceptance still requires the frozen cohesive review/WORK acceptance barrier. HUMAN_DIALOGUE is a permanent supported MANUAL executor fallback under automation/governance/decisions/MANUAL-EXECUTOR-FALLBACK.owner.json; CODEX capacity gates are NOT_APPLICABLE to HUMAN_DIALOGUE, while authority/scope/review/safety remain identical. Executor switching requires a durable checkpoint with no concurrent writer; same execution multi-executor is DENIED. No automatic CODEX.

## HISTORICAL PREDECESSOR PROCEDURES — preserve noncapacity safety; final2.2 capacity/budget above prevails

# CURRENT PROCEDURE — Architecture1.2.1 / capacity2.1

Fresh manifest determines active policies. automation/policies/execution_capacity_policy.v2_1.yaml supersedes predecessor capacity/admission clauses only. Exact local reported tokens primary; provider percentages coarse proxy; derived total-token ratio is ROLLING_CAPACITY_ESTIMATE never EXACT task cost/billing. No fixed80%/40k or coefficient/probe/bootstrap gate. Quota pool provider/account/limit/window only; model/workspace/executor/clientpolicy/taskclass metadata. Same reset positive delta ratios, delta0/reset-crossing retain tokens exclude ratio; overlaps NOISY_SHARED_USAGE reducedconfidence. Last20 usable, n1-4minimum, n>=5linearP25, subtract1pp. Manual exactauthorized allrisk providerPASS unknown=>ALLOW_WITH_WATCH; anyknownwindow belowP90=>WAIT_PROVIDER_CAPACITY. Actual denial=>WAIT_PROVIDER_AVAILABLE. CONTROLLED_AUTO remains DISABLED; at least5 accepted manual currentcontroller executions with strict exacttokens, rolling evidence for both exposedwindows, zero duplicate/fabricatedresume/writerconflicts, no unresolvedgovernance anomaly, independentcontrollerPASS, explicitOwner activation.

Single-use lifecycle/resume/writer/scope/authority gates unchanged; queue/event creates noauthority; wakeonly. No newexecution/reservation/dispatch for alreadyinvoked sameexecution resume. Current predecessor execution_capacity source is not2.1 admission implementation yet; main21file candidate must update evaluator/tests and all current kernel pointers before cohesive source review/acceptance. WORK preexecution uses reviewed2.1 governance policy plus exact deterministic evidence; never reuses predecessor cost_gate projection. No automatic CODEX invocation.

## Predecessor procedure text — preserved navigation/history; capacity2.1 above prevails

# Skill: execution-cost-forecaster

Architecture1.2 ACTIVE after accepted fresh review and WORK materialization. Canonical active successor section below supersedes predecessor procedure pointers; historical artifacts grant no current execution authority. No automatic dispatch or next package authority.


Status: SHADOW / REQUIRED AT WORK-ORDER MATERIALIZATION

Purpose:
Make execution cost observable before execution, comparable after execution, and actionable before abnormal cost compounds across multiple work orders.

Canonical contract:
automation/telemetry/execution_cost_contract.v2.yaml

## WORK responsibilities — before handoff

Every new executable work order or correction work order must have an exact forecast artifact:

automation/work_orders/forecasts/<WORK_ORDER_ID>.json

The work order must point to it.

Forecast from, in order:
1. exact comparable completed executions;
2. same package/correction-family completed executions;
3. same risk/test-profile cohort;
4. package static p50/p75/p90 only as UNCALIBRATED_LEGACY fallback.

Never compare legacy package token forecasts directly with local Codex rollout reported-token totals unless a calibration explicitly establishes compatible units.

Forecast:
- local reported total tokens p50/p75/p90
- uncached input p50/p75/p90 when enough evidence exists
- expected cached-input ratio range
- output/reasoning bands when evidence exists
- 5H delta p50/p75/p90
- weekly delta p50/p75/p90
- actor elapsed seconds p50/p75/p90
- targeted/full test p90
- planned pre-fix/targeted/full-regression cycle counts

Also record:
- assumptions
- confidence
- comparable sample ids
- expected dominant cost driver
- early-watch thresholds

## CODEX responsibilities — during / at completion

CODEX does not estimate after the fact. It records actual observations.

At minimum record:
- actor start/end
- number of pre-fix cases actually run
- number of complete targeted passes
- number of full regression passes
- targeted/full seconds
- 5H/weekly start/end when available
- unexpected retries/tool failures
- local reported token status = PENDING_EXTERNAL_EXTRACTION unless exact local telemetry is already safely available outside the active session

At a safe milestone before another expensive full-suite/model cycle, compare observable proxies with the work-order forecast:
- test cycle count
- elapsed time
- 5H usage when available

If p90 has already been exceeded:
- do not start an additional unplanned full targeted/full regression cycle;
- record COST_GUARD_WATCH;
- finish only the minimum safe bounded step or STOP for WORK replan if another expensive cycle would be required.

Provider hard block still wins.

## WORK responsibilities — after result

1. Ingest CODEX actuals.
2. Enrich local reported tokens with scripts/codex_session_token_usage.ps1.
3. Materialize reconciliation:
   automation/work_orders/optimizations/<WORK_ORDER_ID>.cost-reconciliation.json
4. Compare actuals to p50/p75/p90.
5. Classify variance.
6. Apply cause rules from the canonical contract.
7. Return one bounded optimization recommendation into the next WORK forecast.

Do not wait for three bad runs before flagging a breach.
Three comparable samples are needed only to promote a cohort from PROVISIONAL to CALIBRATED.

## Forecast feedback loop

WORK_FORECAST
→ CODEX_ACTUAL
→ LOCAL_TOKEN_ENRICHMENT
→ VARIANCE
→ CAUSE_CLASSIFICATION
→ OPTIMIZATION_RECOMMENDATION
→ NEXT_WORK_FORECAST

Forecast error is itself telemetry.

Required accuracy fields:
- actual_to_p50_ratio
- actual_to_p90_ratio
- p50_absolute_percentage_error where meaningful
- band_result: NORMAL / WATCH / HIGH / CRITICAL
- dominant_cause
- recommendation_applied_to_next_forecast

## Anti-inflation

Do not grow forecast prose inside kernels.
Keep machine-readable detail in the forecast/reconciliation artifacts and link to them.

Do not add new metrics unless they can change a planning or optimization decision.


## V2 successor procedure — ACTIVE

Use execution_cost_contract.v2 and work_cost_accounting.v2 candidate pointers. Primary demand is per-WO P50/P75/P90 with cached/uncached/input/output/reasoning dimensions; no old static package forecast as admission authority. Capacity estimates need identity/attribution/reset/uncertainty qualification, never confidence by sample count alone. Running provider interruption requires WORK forecast/capacity review, not source-defect classification; legal same-execution resume can proceed after revalidation; durable feedback precedes new work after completion. Review cannot grant authority.
Architecture1.2 ACTIVE; policy presence grants no execution authority. Provider denial always wins.
