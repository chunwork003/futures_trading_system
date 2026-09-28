# GAP-08 W4R-D1A RF01 Blocker / Reauthorization Note

Remote governance baseline:

`a9f8f6763f0619a9440a4f1e0a48a0f703412b35`

D1A runtime candidate under review:

`34960db79b9d2732d23af260dfeb1131c368d9e1`

Disposition:

`BLOCKED_COMPATIBILITY_FAKE / REAUTHORIZATION_REQUIRED`

This is not a production semantic failure.

## What happened

RF01 correctly removed the optional `getattr(...)` readiness-fence fallback from `AccountAuthorityCommitService`.

The new mandatory contract was proven by targeted tests:

`20 passed`

The compatibility gate then failed:

`78 passed / 16 failed`

All failures originate from the existing test double:

`tests/unit/test_c06_broker_action_safety.py::AuthorityRepo`

That fake implements the pre-D1A AccountAuthority repository surface and does not implement:

- `lock_active_readiness_fence(...)`
- `advance_locked_readiness_fence(...)`

The production contract is intentionally mandatory/fail-closed, so restoring an optional fallback or weakening the compatibility gate is forbidden.

## Correct resolution

Expand RF01 write scope by exactly one compatibility-test file:

`tests/unit/test_c06_broker_action_safety.py`

The fake must positively model the scenario used by those tests:

- no active recovery control;
- `lock_active_readiness_fence(account)` returns `None`;
- `advance_locked_readiness_fence(token)` must be unreachable and should fail if called.

No production behavior change is required beyond the already completed mandatory direct-call correction.

## Preserve completed RF01 work

Before reauthorization materialization, the local working tree contains the already completed RF01 changes in:

- `persistence/account_authority.py`
- `tests/unit/test_c04_account_authority_commit.py`

The reauthorization materializer saves those exact unstaged changes to:

`.tmp/GAP08_W4R_D1A_RF01_BLOCKED.patch`

and restores the working tree to the remote governance baseline before committing docs.

The resumed CODEX run should reuse that patch rather than rediscover/rewrite the correction.

## Result Intake V1 note

`codex_level3a_result_intake_v1.ps1` returned:

`FAIL - no runtime commit found after dispatch`

That is expected for this blocked path because V1 models only completed runs that created one runtime commit.

No runtime commit or push existed at the time of the intake call.

Do not interpret this as lost Git work or repository corruption.

A later workflow-tooling revision should add an explicit `BLOCKED_NO_RUNTIME_COMMIT` intake state.

## Governance

- W4R-D1A remains unaccepted.
- W4R-D1B/D2/D3 remain NOT_AUTHORIZED.
- Internal W4R accepted weight remains 13/18.
- Official correction core remains 75/113.
- No GPT-6 escalation is required.
