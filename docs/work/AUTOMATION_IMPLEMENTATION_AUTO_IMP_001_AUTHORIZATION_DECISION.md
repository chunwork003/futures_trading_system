# AUTO-IMP-001 Explicit Authorization Decision

```text
AUTHORIZATION_ID = AUTH-AUTO-IMP-001-01
AUTHORIZATION_REVISION = 1
WORK_PACKAGE_ID = AUTO-IMP-001
DECISION = APPROVE
AUTHORIZATION_STATE = AUTHORIZED
MATERIALIZATION_BASELINE = 026d69161a1ac6c6972cf7b870893c446faffc7d
```

Authorized exact write scope:

- `automation/engine/contracts.py`
- `automation/engine/yaml_io.py`
- `tests/automation/test_contracts.py`

Program-binding rule:

- planning-baseline Program full hash is provenance;
- immutable Program semantic core must remain unchanged;
- `authorization_compilation` routing metadata may change without invalidating package authority;
- executable authority remains the Frozen AuthorizationLifecycleV1 package-level exact binding.

This approval grants bounded automation-tooling source modification and bounded test execution only after execution eligibility passes.

It does not grant Runtime Authorization, product runtime source modification, DB/migration execution, broker network access, LIVE, production activation, AUTO-IMP-002+, or automatic progression.

`AUTHORIZED != EXECUTABLE`.

Next route: `AUTOMATION_IMPLEMENTATION_AUTO_IMP_001_EXECUTION_ELIGIBILITY`.
