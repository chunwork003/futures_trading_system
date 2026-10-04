# AUTO-IMP-001 Authorization Candidate RF01 Rebind

Baseline: `e96876de83da3282fb2a5a63b76b9d73c14937ad`

The previous `AUTH-AUTO-IMP-W1-01` remains `NOT_AUTHORIZED` and is superseded as a candidate only.

Reasons:

1. Its bound Program hash represented the pre-review Program while the current Program artifact changed during review materialization.
2. Frozen AuthorizationLifecycleV1 requires package-level exact binding fields for an executable authorization.

Current candidate:

```text
work_package_id = AUTO-IMP-001
authorization_id = AUTH-AUTO-IMP-001-01
authorization_revision = 1
authorization_state = NOT_AUTHORIZED
automatic_dispatch = DENIED
automatic_next_package_progression = DENIED
```

No implementation or CODEX execution is authorized by this correction.
