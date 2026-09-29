# GAP-08 W4R-D1A RF01 Resume Blocker 02

Remote governance baseline:

`0c2ae2fffb6de09662aba22cd9f8ee2db25b3eff`

Disposition:

`BLOCKED_FULL_REGRESSION_FAKE_DRIFT / REAUTHORIZATION_REQUIRED`

This is not a production semantic failure.

## Completed evidence before STOP

The resumed RF01 run reused the saved blocked patch and added the authorized C06 compatibility fake.

Results:

- targeted: `20 passed`
- compatibility: `94 passed`
- full regression: `1334 passed / 4 skipped / 9 failed`
- semantic correction cycles: `0`
- tooling retries: `1`
- user-observed 5HR: `5%`
- commit: NO
- push: NO

Current local WIP is limited to:

- `persistence/account_authority.py`
- `tests/unit/test_c04_account_authority_commit.py`
- `tests/unit/test_c06_broker_action_safety.py`

Approximate diff:

`+42 / -6`

## Full-regression blocker

The remaining 9 failures are compatibility-test double drift in exactly two existing files:

- `tests/unit/test_c03_expected_state_initialization.py`
- `tests/unit/test_c05_durable_pending_submission.py`

Both define an `AuthorityRepo` fake that implements the pre-D1A AccountAuthority repository surface but not the mandatory readiness-fence operations.

These test scenarios do not model an active recovery control.

Therefore the correct fake contract is:

- `lock_active_readiness_fence(account) -> None`
- `advance_locked_readiness_fence(token)` must never be called and should fail fast if invoked.

## Forbidden workaround

Do not:

- restore `getattr`/optional production fallback;
- weaken the full regression gate;
- create synthetic active recovery tokens in C03/C05;
- alter initialization or pending-submission business semantics.

## Preserve current WIP

Before docs reauthorization, preserve the current exact 3-file unstaged WIP as:

`.tmp/GAP08_W4R_D1A_RF01_RESUME_BLOCKED.patch`

The reauthorization materializer then restores those three files to the remote baseline using raw HEAD blobs, verifies the saved patch applies cleanly, commits/pushes governance only, and leaves the patch for resumed CODEX execution.

## Governance

- W4R-D1A remains unaccepted.
- W4R-D1B/D2/D3 remain NOT_AUTHORIZED.
- internal W4R accepted weight remains 13/18.
- official accepted correction core remains 75/113.
- no GPT-6 escalation is required.

This is the final known test-double compatibility expansion discovered by a complete full-regression run.
