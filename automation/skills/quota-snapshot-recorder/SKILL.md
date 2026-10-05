# Skill: quota-snapshot-recorder

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
- exact task token/cost evidence when the client exposes it

## Token-cost resolution order

1. Provider-native per-task token/cost telemetry, if exposed and exactly bound to this execution.
2. Local Codex session/thread telemetry, only when the session can be unambiguously bound to this execution.
   - Typical Codex local session data may exist under the user's Codex session directory.
   - Never scrape/attribute an unrelated session merely because timestamps overlap.
3. If exact token cost is unavailable, record TOKEN_COST_NOT_AVAILABLE and use percentage-window deltas only as an anomaly estimate.

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
- never convert percentage consumption into literal tokens
- percentage estimates are for relative anomaly detection only
- this Skill records evidence; it never changes admission policy
