# Skill: single-use-lifecycle-guard

Status: SHADOW / MANDATORY PROCEDURE MEMORY

Purpose:
Prevent executor start unless the frozen AuthorizationLifecycleV1 single-use sequence has been durably materialized.

Trigger:
BEFORE_HANDOFF / BEFORE_CLAIM / BEFORE_EXECUTOR_START / BEFORE_RESULT_INTAKE

Canonical policy:
automation/policies/authorization_lifecycle.v1.yaml

Required ordered proof:
1. FRESH_AUTHORITY_RESOLUTION
2. FRESH_ELIGIBILITY_EVALUATION
3. ACQUIRE_GLOBAL_RUNTIME_WRITER_LOCK
4. ALLOCATE_EXECUTION_ID
5. DURABLY_CREATE_EXECUTION_RESERVATION
6. STATE_TO_RESERVED
7. RECHECK_LOCK_HEAD_AND_BINDING
8. MARK_DISPATCH_COMMITTED
9. STATE_TO_CONSUMED
10. INVOKE_EXECUTOR

Hard rules:
- A branch or claim commit alone is NOT a substitute for reservation / RESERVED / dispatch committed / CONSUMED.
- Manual trigger is only a wake event; it does NOT bypass the lifecycle.
- No implementation source edit may begin before durable proof of steps 1-9 exists.
- If the current mechanism cannot materialize the required lifecycle, STOP and route to governance/control-plane work.
- Do not fabricate missing historical lifecycle events after execution.
- Existing execution with ambiguous lifecycle => RECONCILIATION_REQUIRED.
- CONSUMED execution => NO_REDISPATCH.

Inputs:
- current authorization
- work order
- execution identity if allocated
- reservation artifact/pointer
- dispatch artifact/pointer
- current lifecycle state
- writer-lock evidence
- current master HEAD

Output:
PASS_READY_TO_INVOKE_EXECUTOR
or
FAIL_CLOSED_<REASON>

Must not:
- grant authority
- create substitute authority
- rewrite a nonconforming historical run as conforming
- auto-reexecute
- expand source scope
