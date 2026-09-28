# GAP-08 W4R-C2A Closure

Final runtime candidate:

`f5a41a6edade61be85cfb31d8ce76e5e8cc4e1a6`

Disposition:

`W4R-C2A ACCEPTED / FROZEN / READ_ONLY`

Parent W4R-C remains:

`PARTIAL — C1 + C2A ACCEPTED / C2B PENDING`

Parent W4 remains:

`HOLD`

Official correction-core progress remains:

`75 / 113`

W4 weight:

`18 / NOT_CREDITED`

Internal W4R accepted package weight remains:

`9 / 18`

W4R-C weight 4 is not accepted until C2B passes independent review.

## Accepted C2A authority

C2A establishes deterministic minimum recovery-root authority from:

1. BrokerAccount-scoped BrokerAction heads;
2. unresolved BrokerAction heads even when the Order projection is terminal;
3. exact B2 reconstruction receipt IDs/full receipt fingerprints;
4. exact expected snapshot source-event ORDER dependency;
5. explicit unambiguous canonical `order_id` from supplied material broker-report entries.

It also establishes:

- no global Order/history scan;
- terminal resolved BrokerAction head alone is not a root;
- missing head-owned Order fails closed;
- BrokerAction head -> Order exact embedded identity validation;
- expected snapshot exact ID + BrokerAccount validation;
- source-event exact event ID + ORDER entity validation;
- material report world validation;
- missing report order ID preserved as ambiguous ingress;
- malformed report order ID fails closed;
- deterministic root dedupe preserving all source categories;
- immutable deterministic root-set fingerprint;
- no READY/finalize/handoff authority.

## Review history

Initial C2A:

- runtime candidate: `cdd979d6fe46b161b9376f6c58c14ed1aa90e749`
- user-observed 5HR: 17%
- changed files: 6
- diff ~= +224 / -3
- targeted: 95 passed
- compatibility: 42 passed
- full: 1310 passed / 4 skipped
- semantic correction cycles: 2
- tooling retries: 0
- result: HOLD / RF01_REQUIRED

RF01:

- runtime candidate: `f5a41a6edade61be85cfb31d8ce76e5e8cc4e1a6`
- user-observed 5HR: 11%
- changed files: 2
- diff = +37 / -0
- targeted: 49 passed
- compatibility: 61 passed
- full: 1315 passed / 4 skipped
- semantic correction cycles: 0
- tooling retries: 0
- result: ACCEPTED

Observed C2A consumption:

`17% -> 11%`

The controlled-staging-first route remained retry-free.

## Side effects

- migrations: unchanged / not executed
- actual PostgreSQL/V07: NOT_RUN
- A08: NOT_RUN
- broker/paper/Shioaji I/O: NO
- production: NOT_AUTHORIZED
- P7: DO NOT START

C2A is frozen. Later semantic modification requires explicit reauthorization.
