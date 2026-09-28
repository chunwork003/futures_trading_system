# GAP-08 W4R-B1 Independent Review — RF01 Required

Reviewed runtime candidate:

`43acdd3e67470a8dda3ef9f3c8dd706d0a78a67c`

Authorization baseline:

`34ef061907ff0eab63bb42b1a7cb447f780e19c2`

Disposition:

`HOLD / W4R_B1_RF01_REQUIRED`

Official correction-core acceptance remains:

`75 / 113`

W4 weight 18 remains:

`NOT_CREDITED`

W4R-A remains:

`ACCEPTED / FROZEN / READ_ONLY`

## Mechanical result

PASS:

- exactly one runtime commit;
- master == runtime candidate;
- exactly eight authorized files changed;
- Result Intake V1 passed;
- migrations 0001-0008 unchanged;
- migration 0009 source extended but not executed;
- no actual PostgreSQL/V07/A08/broker I/O claimed.

Executor evidence:

- targeted = 60 passed;
- compatibility = 62 passed;
- full regression = 1278 passed / 4 skipped;
- observed 5HR = 19%;
- semantic correction cycles = 0;
- tooling retries = 2.

## Accepted B1 work retained

Retain:

- immutable `BrokerDiscoveryReceipt`;
- discovery result fingerprint derived from canonical `BrokerDiscoveryResult`;
- COMPLETE-only `BrokerReconstructionReceipt`;
- active-recovery generation lock for new receipt writes;
- readiness revision advances once for a new receipt;
- exact duplicate under the current active generation does not advance twice;
- expected snapshot exact-ID/account query;
- broker observation exact-ID/account query;
- migration 0009 extension without historical backfill.

## Material blocker A — Exact-ID read must verify decoded canonical identity

The SQL lookup is exact, but the decoded JSON object is not positively checked against the requested identity/account.

A corrupt row can therefore have DB columns equal to the requested key while the JSON body belongs to a different identity/account.

Required:

### Expected snapshot

After canonical decode, require:

- `snapshot.snapshot_id == requested snapshot_id`;
- `snapshot.broker == normalized requested broker`;
- `snapshot.account_ref == requested account_ref`.

Any mismatch => `ExpectedSnapshotIntegrityError`.

### Broker observation

After canonical decode, require:

- `observation.observation_id == requested observation_id`;
- `observation.broker == normalized requested broker`;
- `observation.account_ref == requested account_ref`.

Use a broker-observation-specific integrity error rather than misclassifying it as an expected-snapshot error.

Missing/wrong-scope SQL row may return `None`; malformed or mismatched durable material must fail closed.

## Material blocker B — Historical exact receipt replay is not idempotent

`_append_trusted_receipt` validates the current active recovery generation before checking whether the immutable receipt already exists.

Therefore an exact retry after recovery handoff or a newer recovery generation can fail before the repository recognizes the exact durable receipt.

Required algorithm:

1. pre-read immutable receipt by exact stable identity;
2. if existing:
   - exact canonical material => `DUPLICATE`;
   - different material => conflict;
   - do not require current active recovery;
   - do not advance readiness;
3. if absent:
   - lock exact BrokerAccount recovery control;
   - require matching active generation;
4. re-read identity under/after the control lock;
5. exact concurrent receipt => `DUPLICATE`;
6. conflicting concurrent receipt => conflict;
7. only a genuinely new receipt may insert and advance readiness exactly once.

Historical duplicate replay must never alter current recovery control.

## Material blocker C — Reconstruction receipt remains persisted caller assertion

Current reconstruction receipt stores `input_coverage_fingerprint`, `accepted_fill_ids`, and `output_fingerprint` as caller-provided material.

`deal_set_completeness=COMPLETE` and uniqueness checks do not prove those fields were derived from the exact C10 reconstruction inputs/output.

B2 therefore cannot distinguish a trusted C10-produced receipt from a caller-fabricated typed receipt with arbitrary fingerprint strings.

Required B1 correction:

The receipt must persist enough canonical material to recompute its authority summary rather than trusting opaque caller strings.

At minimum bind canonical reconstruction material for:

- exact broker Deal evidence used for the COMPLETE DealSet;
- exact pre-existing local Fill identities participating in the reconstruction input world;
- lifecycle evidence when present;
- canonical `BrokerReconstructionPlan` output.

Required deterministic derivations:

- `input_coverage_fingerprint` derives from canonical input material;
- `accepted_fill_ids` derives from plan accepted Fills and is canonicalized as a sorted unique identity set;
- `output_fingerprint` derives from canonical plan output material.

If a caller supplies a derived value, it must exactly equal the recomputed value or validation fails.

The receipt remains bound to BrokerAccount, generation, recovery_cut_fingerprint, discovery_run_id, order_id, authority_commit_id when present, producer_id, and contract_version.

### Boundary

B1 does not decide whether the producer ID is trusted for a deployment.

B2 owns trusted producer/provider registry, capability trust, and resolver composition.

B1 ensures the persisted material is internally canonical and re-verifiable; B2 must not be forced to trust opaque arbitrary fingerprints.

## Required negative tests first

1. exact expected snapshot row whose JSON has another snapshot ID => integrity error;
2. exact expected snapshot row whose JSON has another BrokerAccount => integrity error;
3. exact broker observation row whose JSON has another observation ID => observation integrity error;
4. exact broker observation row whose JSON has another BrokerAccount => observation integrity error;
5. exact discovery receipt retry after recovery inactive => DUPLICATE, no readiness mutation;
6. exact reconstruction receipt retry after newer generation => DUPLICATE, no readiness mutation;
7. same historical receipt identity with changed material => conflict even without matching active generation;
8. concurrent exact duplicate after control lock => DUPLICATE, one readiness advance total;
9. arbitrary/mismatched reconstruction input fingerprint => validation failure;
10. arbitrary/mismatched accepted Fill IDs => validation failure;
11. arbitrary/mismatched output fingerprint => validation failure;
12. equivalent canonical reconstruction material with different tuple ordering yields identical derived material;
13. COMPLETE-only positive receipt contract remains enforced;
14. migrations 0001-0008 unchanged; 0009 extended in place without backfill.

## Tooling finding

Migration 0009 already exists and is unexecuted. For B1 RF01:

- classify it as `EXISTING_UNEXECUTED_EXTENSION`;
- patch/append the exact authorized section in place;
- never recreate/replace the W4R-A DDL;
- use the known-working direct/controlled patch interface immediately.

This is tooling policy, not semantic correction budget.

## Reviewer state

W4R-B1 remains unaccepted.

W4R-B2/C/D remain NOT_AUTHORIZED.

No architecture escalation is required.

All corrections remain inside the original B1 eight-file scope.
