# Skill: execution-efficiency-guard

Architecture1.2 ACTIVE after accepted fresh review and WORK materialization. Canonical active successor section below supersedes predecessor procedure pointers; historical artifacts grant no current execution authority. No automatic dispatch or next package authority.


Status: SHADOW / MANDATORY OPTIMIZATION PROCEDURE

Purpose:
Prevent context, test, and quota cost from growing faster than accepted engineering value.

Triggers:
- BEFORE_CORRECTION_EXECUTION
- BEFORE_TEST_PLAN_EXPANSION
- AFTER_COMPLETED_PENDING_REVIEW
- OPTIMIZATION_CHECKPOINT

## 1. Kernel / context growth guard

Stable role kernels contain only cross-package invariants and pointers.

Must not add to WORK/CODEX kernels:
- package-specific findings
- current SHA/status/quota values
- one-off exception handling
- copied procedures already owned by a Skill

If a procedure needs more than a short invariant/pointer, put it in a Skill or exact work order.

No full-history preload.
Use CURRENT -> exact pointers -> exact delta.

## 2. Counterexample-first cost guard

"Counterexample first" means minimum sufficient failing evidence, not full-suite-before-fix.

Before a fix:
- run the canonical reviewer counterexample first;
- add only the minimum representative cases needed to prove distinct failure classes;
- default maximum pre-fix representative cases: 5 unless a reviewer explicitly requires more.

After the fix:
- run the complete targeted matrix once;
- if targeted fails, rerun only failed/impacted tests while correcting;
- rerun the complete targeted matrix only after known failures are resolved;
- run full regression once after targeted PASS.

Do not rerun a full matrix/full regression without a new code or fixture delta that could change its result.

## 3. Integration-test admission guard

Repository/Git integration tests are allowed only when the behavior actually depends on:
- Git blob/commit identity
- pointer/path resolution
- CRLF/worktree-vs-blob behavior
- symlink/tree/file mode
- canonical CURRENT extraction
- real repository traversal

Pure semantic binding contradictions such as id/revision/state/effect/profile/dependency comparisons should use a pure/table-driven validator test without cloning/committing a repository per case.

If a semantic mutation matrix causes repository clone/commit per row, mark:
TEST_ARCHITECTURE_OPTIMIZATION_REQUIRED.

## 4. Test growth signal

Preserve semantic coverage, but compare each run with the most relevant accepted baseline.

Record:
- targeted_seconds
- full_regression_seconds
- targeted_case_count
- full_case_count
- repository_fixture_case_count

Provisional anomaly signals:
- WATCH when targeted or full runtime > 1.5x comparable baseline;
- HIGH when > 2.0x comparable baseline;
- if a new matrix causes HIGH, do not add more Git-backed cases until an optimization checkpoint decides whether they can become pure tests.

These are efficiency signals, not authorization gates.

## 5. Quota-cost anomaly estimate

Prefer exact provider-native task token/cost data when available.

If exact token cost is unavailable, use percentage telemetry without pretending it is tokens.

For the same reset window:
raw_5h_delta_pct = end_used_pct - start_used_pct
raw_weekly_delta_pct = end_used_pct - start_used_pct

If no reset/overlap/other known consumer, delayed END->next START settlement may be attributed to the previous actor and labeled ESTIMATED.

Never silently add ambiguous shared usage.

Cohort key should include when available:
- model
- executor profile
- task class
- risk/correction class
- test profile

With <3 comparable samples:
classification = PROVISIONAL.

Relative 5H cost ratio against the closest comparable accepted baseline/cohort median:
- <1.5x: NORMAL
- 1.5x to <2.0x: WATCH
- >=2.0x: HIGH

Corroborate HIGH with wall time/test runtime/context reload/tool retry data:
- HIGH + corroborating runtime/test growth = EXPLAINED_HIGH_COST
- HIGH without corroborating work growth = SUSPICIOUS_HIGH_COST

Percentage estimates are for anomaly detection only, never token billing/accounting.

## 6. Materialization rule

At each optimization checkpoint, record:
- observed cost
- comparable baseline
- anomaly classification
- dominant cost driver
- one bounded optimization action
- whether a new Skill/rule is justified

Do not grow the framework for a one-off event.


Reported-token diagnostics:
- record input_tokens, cached_input_tokens, uncached_input_tokens, output_tokens, reasoning_output_tokens, total_tokens when exact local attribution is available;
- cached_input_ratio = cached_input_tokens / input_tokens;
- a very high cached_input_ratio with small uncached_input_tokens indicates context replay/tool-cycle cost, not equivalent fresh-context growth;
- treat local total_token_usage as reported usage telemetry, not billing cost;
- if one execution has >90% cached input and HIGH 5H/runtime signals, classify CONTEXT_REPLAY_DOMINATED unless stronger evidence shows another cause;
- optimize number of model/tool/test turns before shrinking stable cache-friendly kernels blindly.


## 7. Forecast variance early warning

Canonical forecast procedure:
automation/skills/execution-cost-forecaster/SKILL.md

Every executable work order must carry a forecast pointer before handoff.

Do not wait for a later optimization checkpoint when the current run already breaches plan:
- test cycle count over plan => immediate COST_GUARD_WATCH;
- actor elapsed > p75 => WATCH;
- actor elapsed > p90 => HIGH;
- 5H delta > p75 when observable => WATCH;
- 5H delta > p90 => HIGH;
- an extra complete targeted/full-regression pass not in plan => HIGH before starting that extra pass.

A HIGH signal does not revoke authority, but it blocks starting another unplanned expensive cycle until WORK has a bounded reason/replan.

After completion, reconcile actual vs forecast and feed the dominant cause plus one bounded recommendation into the next WORK forecast.


## V2 successor procedure — ACTIVE

Separate provider availability from execution cost under execution_capacity_policy.v2. Active V2 has no fixed remaining-percent floor/token fallback. Provider actual denial checkpoints same execution; preserve completed tests and accumulated telemetry, no additional full suites just because capacity recovers. Forecast-capacity review is WORK feedback, no authority or automatic source failure. Keep initial test debugging distinct from separately authorized semantic correction.
Architecture1.2 ACTIVE; policy presence grants no execution authority. Provider denial always wins.
