# GAP-08 W4R-D2 Tooling Blocker 01

Blocked execution HEAD:

`9cdcf9ba432104330dfd89355f541df3af148641`

Disposition:

`BLOCKED_TOOLING_ROUTE_CONTRADICTION / NO_RUNTIME_CHANGE`

This blocker is not a D2 semantic or architecture failure.

## Observed result

- user-observed 5HR: `9%`
- files changed: `0`
- diff: `0`
- staged files: `0`
- tests: not executed
- semantic corrections: `0`
- tooling retries: `2`
- commit/push: NO
- final worktree: only `data/`

## Root cause

The D2 human-readable authorization states:

`CONTROLLED_STAGING_ROOT_FIRST`

but the machine ACTIVE block stated:

`REPOSITORY_LOCAL_DIRECT_ONLY`

Scheduler V2 correctly propagated the ACTIVE value into the transient CODEX handoff.

The checkout is protected by a workspace reparse-point guard. Repository-local `apply_patch` was rejected for both absolute and relative paths. The handoff simultaneously prohibited the already-proven controlled-staging fallback.

Therefore Codex correctly stopped rather than bypassing the machine authorization.

## Correction

Do not change the D2 semantic package.

Keep the exact four-file write scope:

- `persistence/recovery.py`
- `persistence/postgres/recovery.py`
- `tests/unit/test_c15_account_recovery_readiness.py`
- `tests/unit/test_operational_postgres.py`

Replace the single-route machine rule with:

`CONTROLLED_ROUTE_SET`

The authorized route set is:

1. repository-local direct edit/patch when accepted by the workspace;
2. if rejected by reparse/workspace guard, immediately switch to controlled staging root;
3. modify only exact authorized files in staging;
4. verify staging diff is exact authorized scope;
5. copy back only exact authorized files once;
6. verify repository diff/scope immediately after copy-back;
7. run pytest only from the repository-local checkout with repository-local `--basetemp`.

A route switch inside this set:

- is a tooling event;
- does not consume semantic correction budget;
- does not require reauthorization;
- does not require STOP.

STOP only when all authorized routes fail, the exact write scope must expand, or frozen semantics/authority must change.

## Governance

- W4R-D1A/D1B remain ACCEPTED/FROZEN.
- W4R-D2 remains the same semantic leaf and is not restarted from architecture.
- W4R-D3 remains NOT_AUTHORIZED.
- internal W4R accepted weight remains `13/18`.
- official correction core remains `75/113`.
- W4 weight remains `18 / NOT_CREDITED`.
