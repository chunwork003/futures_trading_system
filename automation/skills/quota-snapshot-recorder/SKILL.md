# Skill: quota-snapshot-recorder

Architecture1.2 ACTIVE after accepted fresh review and WORK materialization. Canonical active successor section below supersedes predecessor procedure pointers; historical artifacts grant no current execution authority. No automatic dispatch or next package authority.


Status: SHADOW

Trigger:
ACTOR_START / ACTOR_END / OPTIMIZATION_CHECKPOINT

Record when available:
- actor
- work_order_id
- execution_id
- model / executor profile
- timestamp
- five_hour used/remaining percentage
- weekly used/remaining percentage
- reset metadata
- provider evidence source
- exact task reported-token evidence when the client exposes it
- provider-native billing/cost evidence only when explicitly exposed

## Token-cost resolution order

1. Provider-native per-task billing/cost telemetry, if explicitly exposed and exactly bound to this execution.
2. Local Codex session/thread reported-token telemetry, only when the session can be unambiguously bound to this execution.
   - Canonical helper: scripts/codex_session_token_usage.ps1
   - Typical session data lives under CODEX_HOME/sessions or ~/.codex/sessions and archived_sessions.
   - Bind by execution/work-order identity plus the actor start/end time window.
   - Read token_count metadata only; never print raw transcript/tool outputs into an active Codex conversation.
   - Never attribute an unrelated session merely because timestamps overlap.
3. If exact billing/cost is unavailable, record BILLING_COST_NOT_AVAILABLE. Local rollout token deltas may still be used as reported-token telemetry; percentage-window deltas remain the quota anomaly estimate.

Do not fabricate a token count from percentage limits.

## Percentage anomaly estimate

When start/end belong to the same reset window:

raw_5h_delta_pct = end_used_pct - start_used_pct
raw_weekly_delta_pct = end_used_pct - start_used_pct

Preserve raw observations exactly.

If previous END -> next START has:
- no reset
- no overlap
- no known competing consumer

the settlement delta may later be attributed to the previous actor as ESTIMATED_DELAYED_SETTLEMENT.

Otherwise classify:
UNALLOCATED_SHARED_DELTA
or
ATTRIBUTION_ESTIMATED.

Use automation/skills/execution-efficiency-guard/SKILL.md for relative anomaly classification.

## Hard rules

- raw observations are immutable evidence
- never replace raw values with reconciled values
- never infer an admission threshold from historical percentages
- never label percentage-derived capacity/token estimates EXACT
- percentage proxy telemetry may support qualified capacity calibration
- this Skill records evidence; it never changes admission policy


## Local Codex safety guard

Do NOT ask the active Codex agent to cat/sed/rg its raw rollout JSONL history. Raw self-session ingestion can itself inflate context/token usage.

Preferred flow:
- operator or external control-plane PowerShell runs scripts/codex_session_token_usage.ps1;
- helper scans metadata only and emits a small JSON summary;
- WORK may materialize that summary as telemetry evidence;
- raw rollout files remain local/untracked and must never be committed.


Telemetry semantics:
- Local rollout total_token_usage is usage telemetry, not a guaranteed billing ledger.
- cached_input_tokens is reported separately inside input usage and must not be double-counted.
- Never equate total_tokens, cached tokens, or a local token delta directly to ChatGPT 5H/weekly percentage consumption.
- If client/version omits a token category, preserve that limitation instead of synthesizing it.


## V2 successor procedure — ACTIVE

Record immutable provider raw observations and all identity/window/reset/competing-consumer limitations. Percentages are PROVIDER_REPORTED_SHARED_ACCOUNT_USAGE_PROXY, usable for qualified capacity calibration; derived values are PROVISIONAL_ESTIMATE/CALIBRATED_ESTIMATE never EXACT. Keep local exact-bound feature dimensions separate; no fixed weights or constant total-token conversion. Use execution_capacity_policy.v2 and execution_cost_contract.v2 after reviewed activation. Pauses retain SAME execution telemetry; no raw mutation.
Architecture1.2 ACTIVE; policy presence grants no execution authority. Provider denial always wins.
