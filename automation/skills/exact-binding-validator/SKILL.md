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

Output:
PASS or FAIL_CLOSED

Any mismatch or ambiguity => FAIL_CLOSED.

Must not:
repair bindings, modify authority, expand scope, consume authorization, create claims.
