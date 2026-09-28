# GAP-08 W4R-B Execution Plan

Parent package:

`W4R-B / internal weight 4`

Dependency:

`W4R-A ACCEPTED`

W4R-B is divided into two execution leaves for smaller CODEX context and reviewer boundaries.

No official correction-core credit is granted by either leaf independently.

## B1 — Durable Recovery Evidence Authority

Goal:

Create durable, exact, account-scoped authority for C07 discovery and positive C10 reconstruction evidence, plus exact expected/actual batch lookup needed by the later trusted resolver.

Responsibilities:

1. append-only `BrokerDiscoveryReceipt`;
2. append-only positive `BrokerReconstructionReceipt`;
3. exact identity/material idempotency/conflict semantics;
4. active recovery generation binding;
5. new durable receipt writes advance `readiness_revision` exactly once;
6. exact `AccountPositionSnapshot` lookup by ID + BrokerAccount;
7. exact `BrokerPositionObservation` lookup by ID + BrokerAccount;
8. migration 0009 extension for the two receipt tables.

Must reuse existing C07/C10 domain classifications.

Must not change:
- discovery classification semantics;
- reconstruction economics;
- C15 evaluator;
- C13/C14;
- capabilities;
- final readiness bundle/handoff.

## B2 — Trusted Capability + Resolver Core

Requires B1 accepted.

Goal:

Create process-trusted capability registry snapshot/fingerprint and trusted resolver core that can re-read exact B1/account evidence.

Responsibilities:

1. trusted immutable `BrokerCapabilityMatrix` provider/registry snapshot;
2. deterministic registry identity/version/fingerprint;
3. environment-specific capability verification mode;
4. exact resolution of:
   - discovery receipt;
   - reconstruction receipt(s);
   - expected snapshot;
   - broker observation;
   - capability evidence;
5. typed resolver outputs that preserve identity/provenance/currentness but do not make C15 READY.

B2 does not build the final `TrustedReadinessEvidenceBundle`; W4R-D owns final same-world bundle + atomic handoff.

## W4R-B acceptance

W4R-B internal weight 4 becomes accepted only after B1 + B2 both pass independent review.

W4 remains HOLD and official accepted correction core remains 75/113 until final W4 closure.
