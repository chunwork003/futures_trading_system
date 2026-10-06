# Skill: execution-cost-forecaster

Status: SHADOW / REQUIRED AT WORK-ORDER MATERIALIZATION

Purpose:
Make execution cost observable before execution, comparable after execution, and actionable before abnormal cost compounds across multiple work orders.

Canonical contract:
automation/telemetry/execution_cost_contract.v1.yaml

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


## V2 successor procedure — candidate only

Use execution_cost_contract.v2 and work_cost_accounting.v2 candidate pointers. Primary demand is per-WO P50/P75/P90 with cached/uncached/input/output/reasoning dimensions; no old static package forecast as admission authority. Capacity estimates need identity/attribution/reset/uncertainty qualification, never confidence by sample count alone. Running provider interruption requires WORK forecast/capacity review, not source-defect classification; legal same-execution resume can proceed after revalidation; durable feedback precedes new work after completion. Review cannot grant authority.
Architecture1.1 remains ACTIVE until fresh governance review and WORK materialization; candidate presence grants no authority. Provider denial always wins.
