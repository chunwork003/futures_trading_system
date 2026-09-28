# GAP-08 W4R-D1A Independent Review — RF01 Required

Reviewed runtime candidate:

`34960db79b9d2732d23af260dfeb1131c368d9e1`

Execution baseline:

`c03399a4b5fb848370f1cec645212eb832573fce`

Disposition:

`HOLD / W4R_D1A_RF01_REQUIRED`

Official correction-core acceptance remains:

`75 / 113`

W4 weight remains:

`18 / NOT_CREDITED`

Internal W4R accepted weight remains:

`13 / 18`

W4R-A / W4R-B / W4R-C remain:

`ACCEPTED / FROZEN / READ_ONLY`

## Mechanical result

PASS:

- exactly one D1A runtime commit;
- master == runtime candidate;
- exactly seven authorized files changed;
- no migration changes;
- no actual PostgreSQL/V07/A08/broker I/O;
- no D1B/D2/D3 or final handoff work.

Executor evidence:

- targeted = 54 passed;
- compatibility = 123 passed;
- full regression = 1340 passed / 4 skipped;
- semantic correction cycles = 1 (test-only SQL verb classification);
- tooling retries = 0;
- diff = +215 / -0;
- user-observed 5HR consumption = 18%.

## Accepted D1A work retained

Retain:

- broker-neutral `RecoveryReadinessFenceToken`;
- broker-neutral fence repository contract;
- PostgreSQL exact BrokerAccount `FOR UPDATE` lock;
- inactive/missing control => no active token;
- exact CAS on account/generation/cut/readiness/active;
- readiness-only increment;
- `ingress_version` untouched;
- no repository commit/rollback;
- AccountAuthority material ordering:
  - duplicate precheck;
  - fence lock;
  - account head lock;
  - participants;
  - checkpoint/head/receipt;
  - authority closure validation;
  - readiness advance;
  - commit;
- broker observation ordering:
  - fence lock;
  - observation + items;
  - readiness advance;
- no READY/finalize/handoff surface.

## Material blocker — AccountAuthority fence participation is optional / fail-open

`AccountAuthorityRepository` now explicitly includes:

- `lock_active_readiness_fence(...)`
- `advance_locked_readiness_fence(...)`

However `AccountAuthorityCommitService.commit()` currently uses:

`getattr(repository, "lock_active_readiness_fence", None)`

and only participates in the fence when that attribute happens to exist.

Therefore a repository/composition that does not implement the newly required D1A fence contract can still perform a successful new material AccountAuthorityCommit with no readiness invalidation.

That silently reintroduces the TOCTOU hole D1A exists to close.

This is especially material because AccountAuthorityCommit is the outer transaction for:

- Order;
- Fill;
- OrderEvent;
- expected snapshot;
- BrokerAction reserve/resolve participants.

A missing fence implementation must never degrade to an unfenced successful material commit.

## Required correction

For every new material AccountAuthorityCommit:

- invoke `repository.lock_active_readiness_fence(account)` as a mandatory protocol operation;
- do not feature-detect it;
- do not silently substitute `None` because the method is absent;
- returned `None` remains valid only when the repository positively reports that no active recovery control exists;
- if repository composition does not implement the fence contract, fail before AccountStateHead lock and before any material participant.

Exact duplicate/conflicting receipt handling remains before the fence call.

## Required counterexamples first

1. repository missing the required fence operation cannot perform a new material commit;
2. failure occurs before head lock/participants/material writes;
3. repository implementing the operation and returning `None` (positively no active recovery) still permits the ordinary commit;
4. active token still locks before head and advances exactly once;
5. exact duplicate/conflicting stable receipt still never locks or advances;
6. readiness advance failure rolls back the UoW and does not commit authority material;
7. no READY/finalize/handoff surface appears.

## Reviewer state

W4R-D1A remains unaccepted.

W4R-D1B/D2/D3 remain NOT_AUTHORIZED.

No GPT-6 escalation is required.

This is a narrow D1A fail-closed contract correction.
