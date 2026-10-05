# Skill: quota-snapshot-recorder

Status: SHADOW

Trigger:
ACTOR_START / ACTOR_END

Record when available:
- actor
- work_order_id
- execution_id
- timestamp
- five_hour_remaining
- weekly_remaining
- reset metadata
- provider evidence source

Rules:
- preserve raw observations exactly
- never replace raw values with reconciled values
- never infer a threshold
- never convert tokens to provider percentage unless explicit compatible-unit policy exists

Delayed settlement:
If previous END → next START has no reset, overlap, or known competing consumer, later attribution may assign delta to previous actor.
Otherwise classify as UNALLOCATED_SHARED_DELTA or ATTRIBUTION_ESTIMATED.

This Skill records evidence only; it never changes admission policy.
