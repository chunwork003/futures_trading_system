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
