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
   - Canonical helper: scripts/codex_session_token_usage.ps1
   - Typical session data lives under CODEX_HOME/sessions or ~/.codex/sessions and archived_sessions.
   - Bind by execution/work-order identity plus the actor start/end time window.
   - Read token_count metadata only; never print raw transcript/tool outputs into an active Codex conversation.
   - Never attribute an unrelated session merely because timestamps overlap.
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


## Local Codex safety guard

Do NOT ask the active Codex agent to cat/sed/rg its raw rollout JSONL history. Raw self-session ingestion can itself inflate context/token usage.

Preferred flow:
- operator or external control-plane PowerShell runs scripts/codex_session_token_usage.ps1;
- helper scans metadata only and emits a small JSON summary;
- WORK may materialize that summary as telemetry evidence;
- raw rollout files remain local/untracked and must never be committed.
