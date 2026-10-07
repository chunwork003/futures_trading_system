# Operating Model — candidate, not controller activation

## Ownership and authority

WORK reads fresh accepted repository truth, intakes results, prepares independent review, checks integration/acceptance evidence under a bounded grant and selects the next legal package. CODEX executes exactly one granted package and reports COMPLETED_PENDING_REVIEW. Reviewer uses fresh isolated context and cannot implement its own acceptance evidence. Integrator applies reviewed changes under exact scope and revalidates semantic drift. Controller performs only approved effects, with durable idempotency and one-writer enforcement. Architect owns public semantics; Owner owns major scope/authority changes and production permission.

No Skill, registry, timer, quota reset, PASS report or source document independently grants authority. Current user authorizes architect materialization only for this P00; future product dispatch requires its own current bindings. A proposed bounded-wave delegation may remove routine Owner roundtrips, but it must enumerate scope, budget, gates, revocation and expiry before activation.

## Adaptive cycle

1. Rehydrate exact master/current policy/package/result/STOP pointers; record baseline and actual provider capabilities.
2. Resolve safety incidents and unfinished invocation first. Missing invocation evidence is not resumable work.
3. Intake durable result, review, corrections and integration before unrelated new work. Release writer only under accepted lifecycle semantics.
4. Filter candidates by exact authority, dependencies, no conflicting writer, external requirements and capacity. No legal candidate means wait or prepare allowed read-only evidence, never invent a grant.
5. Rank only eligible candidates; dispatch at most one exact package. Persist the decision inputs, reasons, idempotency key and next wake.
6. Reforecast after completion, capacity/provider change, review result or blocker change. Time-triggered wake only starts re-entry.

Candidate score uses normalized [0,1] versioned factors: benefit = 4×critical_path + 3×engineering_value + context_reuse + bounded_wait_age. Cost = expected_tokens/token_budget + expected_time/time_budget + 2×correction_risk. Score = benefit / max(cost,0.1). Ties: older legal-ready timestamp, then stable package ID. Hard gates never become weighted penalties. Missing cost/capacity means UNKNOWN, not free work; use conservative measured class bound or do not dispatch. Waiting age cannot override safety or result-first precedence.

Wake at earliest meaningful event among result/review availability, lease revalidation, provider reset, external-blocker check and configured maximum idle interval. Clamp retry frequency, backoff unchanged blockers, and coalesce duplicate events. Exact bounds, provider adapters and persisted scheduler schema remain to be specified/tested before activation.

## Automation sequencing

Do not require AUTO-IMP-003 through 009 all completed before product work. Proposed replacement grouping: A1 exact lifecycle and negative tests; A2 result/review/integration/acceptance; A3 controlled dispatch/wake/adaptive ranking. Map each existing package requirement before merging/deprecating anything; accepted components remain intact. This mapping is still pending, so current accepted program is not silently superseded.

Product-first budget target: at least 80% accepted engineering effort toward V1 until measured automation savings justify change. This is a planning allocation, not an authorization bypass. Human-directed product packages can proceed after baseline/own authorization with zero new automation packages as prerequisite. A1–A3 can be interleaved where they remove observed bottlenecks.

## Reusable execution contract

Package must bind baseline, goal/non-goals, deliverable IDs, dependencies, owned contracts, exact allowlist/protected paths, input fixtures, acceptance predicates, test impact, review risk class, estimated cost, stop conditions and source hashes. Context resolver loads current authority + package + directly referenced contracts; optional history only for an unresolved contradiction. Forbidden context means unrelated historical prompts and secrets, never suppression of relevant adverse evidence.

Design gaps stop the affected semantic slice and return to Architect. Ordinary scope-internal defects use a bounded correction budget. Governance errors are repaired in governance scope; context failures add resolver/eval tests; fragmented packages are recombined at a legal package boundary. Never rename a new public semantic decision as a bug fix.

Risk-based validation: targeted tests per changed contract; integration tests for changed boundaries; full product regression at integration/release or demonstrable shared impact. Changing the existing required regression policy requires an accepted amendment; this candidate does not waive current gates. Review once per cohesive outcome with focused correction re-review bound to changed evidence, not repeated whole-history narration.

## Qualification and measurement

Track accepted deliverable weight per token/day; first-pass review acceptance; corrections classified as defect/design/governance/context/fragmentation; time awaiting review/Owner/external evidence; context tokens; stale dispatch/duplicate effects (must be zero). Distinguish observed zero from missing telemetry. Model routing uses demonstrated task/eval performance and risk, not unsupported provider claims. Escalate unresolved safety/semantic contradictions; retry cheaper models only within the same contract and correction budget.

Golden evaluations must include clean re-entry, stale hash, revoked authority, missing invocation, duplicate result, candidate drift after PASS, unavailable provider, exhausted quota and external-blocked work with independent legal alternative. Positive and negative fixtures plus evidence are required before increasing maturity; artifact existence alone never qualifies autonomous operation.
