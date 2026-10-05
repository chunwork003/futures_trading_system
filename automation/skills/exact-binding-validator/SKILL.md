# Skill: exact-binding-validator

Status: SHADOW

Trigger:
BEFORE_CLAIM / BEFORE_RESUME / BEFORE_DISPATCH / BEFORE_RESULT_INTAKE

Inputs:
work order, authorization, package, current master HEAD, execution identity if present

Validate:
- authorization id/revision
- package id/revision
- architecture id/revision
- planning baseline
- exact scope
- side-effect class
- governance effect
- executor profile
- review barrier
- existing branch
- existing completion evidence
- lifecycle reservation / RESERVED / dispatch committed / CONSUMED proof when trigger is BEFORE_DISPATCH or BEFORE_EXECUTOR_START

Lifecycle rule:
- validate against automation/policies/authorization_lifecycle.v1.yaml
- branch/claim evidence alone is insufficient
- missing or ambiguous lifecycle proof => FAIL_CLOSED / RECONCILIATION_REQUIRED
- validator never fabricates or retroactively repairs lifecycle events

Output:
PASS or FAIL_CLOSED

Any mismatch or ambiguity => FAIL_CLOSED.

Must not:
repair bindings, modify authority, expand scope, consume authorization, create claims.


Cross-artifact minimum matrix:
- CURRENT work_order_id/package_id/package_revision/authorization_id/authorization_revision/exact_write_scope/execution_branch MUST equal WORK
- CURRENT authorization_path MUST equal WORK authorization_path and the loaded authorization document identity
- CURRENT/WORK authorization_state MUST be compatible with the loaded authorization_state
- CURRENT quota_amendment.amendment_id/path/status/effect MUST equal the loaded amendment identity/path/status/effect
- amendment exact_binding work_order_id/package_id/package_revision/work_order_path MUST equal canonical CURRENT/WORK
- amendment exact_binding base_authorization_id/revision/path MUST equal the loaded/current authorization
- amendment exact_binding executor_profile MUST equal authorization exact_binding.allowed_executor_profile
- CURRENT eligibility_path MUST equal WORK eligibility_path and the loaded eligibility document
- eligibility work_order_id/package_id/authorization_id/status/trigger mode MUST match canonical CURRENT/WORK/AUTH expectations
- authorization package_binding path/revision/scope MUST match the loaded package; package identity/revision and planned scope must match CURRENT/WORK
- authorization program_binding dependency pointer MUST resolve to the expected dependency package identity and ACCEPTED_MATERIALIZED state
- any contradictory pointer, identity, revision, state, effect, executor profile, or dependency identity MUST FAIL_CLOSED

Negative-test rule:
For every binding class above, keep at least one mutation test that changes only that field while preserving otherwise-valid documents. The resolver must return STOP/FAIL_CLOSED and must never return an execution candidate.


Execution-effect restrictions:
- WORK side_effects.runtime/broker/db/migration/live/production MUST remain DENIED when those surfaces are outside the exact authority.
- CURRENT auto_imp_003_authorized MUST be false while WORK next_package identifies AUTO-IMP-003 as NOT_AUTHORIZED.
- CURRENT and WORK quota_gate.provider_hard_block MUST both remain STOP.
- Any contradiction that weakens a DENY/STOP/NOT_AUTHORIZED effect MUST FAIL_CLOSED before candidate routing.
- Effect restrictions are first-class bindings; do not limit validation to identity/pointer/revision fields.

Negative-test minimum:
- one mutation that expands a protected side effect;
- one mutation that authorizes the next package;
- one mutation that weakens provider hard block.
