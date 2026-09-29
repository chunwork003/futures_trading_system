# GAP-08 W4R-D1A Closure

Final accepted runtime:

`af794f5895c41925cfe007da7e1f522fcd189920`

Disposition:

`W4R-D1A ACCEPTED / FROZEN / READ_ONLY`

Parent W4R-D:

`PARTIAL / D1B NEXT`

Internal W4R accepted weight remains:

`13 / 18`

Official correction-core acceptance remains:

`75 / 113`

W4 weight remains:

`18 / NOT_CREDITED`

## Accepted D1A authority

D1A establishes one broker-neutral transaction-local readiness currentness fence:

- immutable `RecoveryReadinessFenceToken`;
- exact BrokerAccount binding;
- recovery generation;
- recovery cut revision;
- captured readiness revision;
- PostgreSQL `FOR UPDATE` active-control lock;
- exact readiness-only CAS;
- `ingress_version` remains untouched;
- repository never commits or rolls back.

Accepted AccountAuthority ordering for new material commits:

1. stable receipt duplicate/conflict handling;
2. mandatory readiness-fence protocol call;
3. exact AccountStateHead lock/bootstrap;
4. material participants;
5. checkpoint/head/receipt writes;
6. authority-closure validation;
7. exactly one readiness advance when active;
8. caller-owned UoW commit.

Fail-closed properties:

- missing fence contract cannot silently degrade to unfenced material commit;
- missing contract fails before head lock/material participants;
- explicit `None` is the only no-active-recovery path;
- participant/material failure never advances;
- readiness advance failure prevents commit and rolls back the UoW;
- exact duplicate/conflicting stable receipt never locks/advances the fence.

Broker position observation now participates in the same neutral readiness fence:

`lock -> observation/items -> readiness advance`

with no repository commit.

BrokerAction receives D1A coverage through its existing AccountAuthorityCommit participants; no second BrokerAction readiness increment exists.

## Final verification

Final RF01 Resume-2 runtime commit:

`fix(recovery): require W4R-D1A readiness fence contract`

Changed files:

- `persistence/account_authority.py`
- `tests/unit/test_c03_expected_state_initialization.py`
- `tests/unit/test_c04_account_authority_commit.py`
- `tests/unit/test_c05_durable_pending_submission.py`
- `tests/unit/test_c06_broker_action_safety.py`

Final execution evidence:

- focused: `51 passed`
- compatibility: `75 passed`
- full regression: `1343 passed / 4 skipped`
- `git diff --check`: PASS
- exact scope: PASS
- semantic correction cycles: `0`
- tooling retries: `0`
- user-observed 5HR consumption: `6%`
- migration / actual PostgreSQL / broker I/O: NO

Mechanical intake:

`MECHANICAL_INTAKE_PASS / SEMANTIC_REVIEW_REQUIRED`

Independent semantic review:

`PASS`

## Execution-history learning retained

D1A also established a reusable blocked-work workflow:

`BLOCKED -> preserve WIP patch -> reauthorize exact compatibility delta -> resume`

The blocked paths exposed only test-double contract drift; production semantics remained mandatory/fail-closed.

Result Intake V1 still models successful one-runtime-commit completion only. A future tooling revision may add an explicit blocked/no-runtime-commit state.

## Freeze

D1A source semantics are now frozen/read-only.

Any later semantic change requires explicit reauthorization.

No D1B/D2/D3 semantics are granted by this closure.
