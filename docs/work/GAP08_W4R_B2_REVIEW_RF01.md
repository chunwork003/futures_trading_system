# GAP-08 W4R-B2 Independent Review — RF01 Required

Reviewed runtime candidate:

`b505c41a7c46a6dbe335cb3cb738270f1acbac32`

Authorization baseline:

`4b2b1ae31560fd0b248346e023d670b1d5ed6b3b`

Disposition:

`HOLD / W4R_B2_RF01_REQUIRED`

Official correction-core acceptance remains:

`75 / 113`

W4 weight 18 remains:

`NOT_CREDITED`

W4R-A:

`ACCEPTED / FROZEN / READ_ONLY`

W4R-B1:

`ACCEPTED / FROZEN / READ_ONLY`

## Mechanical result

PASS:

- exactly one runtime commit;
- master == runtime candidate;
- exactly eight authorized files changed;
- migrations unchanged;
- no actual PostgreSQL/V07/A08/broker I/O claimed.

Executor evidence:

- actual changed files = 8;
- approximate diff = 264 insertions / 2 deletions;
- targeted = 85 passed;
- compatibility = 59 passed;
- full regression = 1292 passed / 4 skipped;
- semantic correction cycles = 0;
- test assertion correction = 1;
- tooling retries = 1;
- observed 5HR = 23%.

## Efficiency interpretation

Do not use pytest pass count as workload.

Compared with B1 RF01:

- B1 RF01: 6 files / ~155 changed lines / 15% / 0 tooling retries;
- B2 initial: 8 files / ~266 changed lines / 23% / 1 tooling retry.

B2 consumed more absolute 5HR because its actual change surface was materially larger and crossed three concerns:

1. capability registry;
2. exact durable receipt readers;
3. resolver core.

Normalized by approximate changed lines, B2 is not obviously less efficient than B1 RF01.

The remaining optimization target is the single tooling retry.

## Accepted B2 work retained

Retain:

- immutable capability registry snapshot;
- deterministic matrix fingerprint;
- exact broker-scoped static provider;
- Sinopac documentation-only registry snapshot;
- discovery/reconstruction exact receipt reads;
- exact read canonical decode + identity/account verification;
- resolver revalidation of generation/cut/discovery linkage;
- exact expected/actual ID reads;
- verification-mode-aware capability checks;
- resolver output has no READY/finalize surface.

## Material blocker — Resolver core does not bind full durable receipt material

The B2 resolver validates full `BrokerDiscoveryReceipt` / `BrokerReconstructionReceipt` objects, but the returned `TrustedRecoveryEvidenceCore` preserves only partial fingerprints:

- discovery: `result_fingerprint`;
- reconstruction: `output_fingerprint`.

These are not full durable receipt fingerprints.

Two reconstruction receipts may have the same output plan while differing in:

- broker Deal input material;
- local Fill input identity set;
- lifecycle evidence;
- input coverage fingerprint;
- accepted Fill IDs;
- producer ID;
- contract version;
- authority commit provenance;
- recorded_at.

The current resolver core can therefore collapse materially different durable receipts into the same output fingerprint representation.

Likewise, discovery `result_fingerprint` does not bind all receipt-level provenance such as producer/contract/generation/recorded_at.

This prevents W4R-D from proving exactly which complete durable receipt material was accepted by B2 without re-deriving B2 trust from scratch.

## Required correction

Add deterministic canonical full-receipt fingerprints.

### BrokerDiscoveryReceipt

Provide deterministic full receipt fingerprint derived from canonical normalized receipt material.

It must bind at least:

- discovery_run_id;
- account;
- generation;
- canonical result + result fingerprint;
- producer_id;
- contract_version;
- recorded_at.

### BrokerReconstructionReceipt

Provide deterministic full receipt fingerprint derived from canonical normalized receipt material.

It must bind at least:

- reconstruction_receipt_id;
- account;
- generation;
- recovery_cut_fingerprint;
- discovery_run_id;
- order_id;
- canonical broker Deals;
- local Fill IDs;
- lifecycle evidence;
- canonical reconstruction plan;
- input coverage fingerprint;
- accepted Fill IDs;
- output fingerprint;
- deal-set completeness;
- authority_commit_id;
- producer_id;
- contract_version;
- recorded_at.

### TrustedRecoveryEvidenceCore

Replace/augment partial provenance with:

- `discovery_receipt_fingerprint`;
- `reconstruction_receipt_fingerprints`.

The reconstruction receipt identity/fingerprint pairs must be deterministic and preserve exact one-to-one binding.

Required canonicalization:

- reconstruction receipt IDs must be unique;
- resolver canonicalizes requested reconstruction receipt identities in deterministic order;
- output core uses the same canonical order for IDs and full receipt fingerprints;
- duplicate requested receipt IDs must not silently create duplicate authority.

The existing result/output fingerprints may remain as diagnostic fields if useful, but they are not sufficient authority fingerprints.

## Boundary

RF01 does not change:

- capability support semantics;
- provider trust-composition policy;
- C13/C14;
- continuity authority;
- recovery-root closure;
- final TrustedReadinessEvidenceBundle;
- C15;
- final handoff.

Production composition-root prevention of arbitrary provider substitution remains W4R-D responsibility.

## Required counterexamples first

1. two reconstruction receipts with the same output plan but different input material produce different full receipt fingerprints;
2. same reconstruction output but different producer/contract version produces different full receipt fingerprints;
3. discovery same result but different producer/contract provenance produces different full receipt fingerprints;
4. canonical model dump/reload produces identical full receipt fingerprint;
5. reconstruction receipt ID input order does not change resolver-core canonical identity/fingerprint ordering;
6. duplicate requested reconstruction receipt IDs are rejected or canonicalized to exactly one authority according to explicit contract;
7. full receipt fingerprint changes if accepted Fill identities change;
8. B2 core still has no READY/finalize/handoff surface.

## Reviewer state

W4R-B2 remains unaccepted.

W4R-C/D remain NOT_AUTHORIZED.

No GPT-6 escalation is required.

This is a narrow B2 correction.
