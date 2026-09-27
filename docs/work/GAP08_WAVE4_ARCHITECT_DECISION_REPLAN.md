# GAP-08 Wave-4 — Architect Decision: Rescope C15 and Replan W4

## Decision

Disposition:

`RESCOPE_C15_AND_REPLAN_W4`

Reviewed runtime candidate:

`8f410ec2c76493c4db2b904be11974c42c09cae0`

Governance state:

- W4 = `HOLD / RESCOPE_C15_AND_REPLAN_W4`
- accepted correction core = `75 / 113`
- W4 weight 18 = `NOT_CREDITED`
- P7 = `DO NOT START`
- Runtime Authorization = `NOT_AUTHORIZED`
- RF03 = `NOT_AUTHORIZED`
- Executor coding = `NOT_AUTHORIZED`

RF02 source changes are retained as candidate work but are not accepted as W4 closure authority.

## AD-01 — Continuity Authority

Introduce a BrokerAccount-scoped durable continuity head.

Each BrokerAccount has exactly one authoritative current continuity head with a monotonic authority revision.

The head points to the current immutable epoch and its validated transition / re-anchor provenance.

Currentness must not be inferred from lexical epoch order、latest timestamp、historical trusted rows or caller-provided trust flags.

Required binding includes at least:

- BrokerAccount
- active recovery generation
- continuity head revision
- epoch identity
- anchor identity / fingerprint
- ingress frontier
- relevant gap disposition
- snapshot / authority-commit provenance
- producer identity
- contract version
- evidence identity
- complete RecoveryCut identity

After the head advances, the old epoch immediately loses current readiness eligibility.

A later untrusted / invalidated epoch must never fall back to an older trusted epoch.

A valid re-anchor may restore trust only with complete provenance and without deleting historical gap/degradation evidence.

Fail closed:

- current epoch untrusted / re-anchor incomplete / evidence pending => REVIEW
- head missing / identity conflict / provenance conflict => HALT

## AD-02 — Trusted Evidence Resolution

C15 is rescoped.

Before C15 acceptance, establish and accept an independent trusted evidence resolution prerequisite.

The production direction is a trusted resolver model.

Pure evaluators may remain, but readiness authority must come from resolver-backed evidence and trusted final revalidation.

Trusted resolution must cover:

- C07 discovery
- AD-01 continuity authority
- C10 reconstruction provenance
- C13 reconciliation case semantics
- C14 formal run
- versioned capability registry

Typed DTO construction is allowed, but constructability does not grant authority.

Fields such as complete、conflict、available、source_refs and completeness state must be derived or verified by the trusted resolver.

Planning shall define a `TrustedReadinessEvidenceBundle` that binds one authoritative world:

- BrokerAccount
- evaluation / recovery generation
- RecoveryCut
- continuity head + epoch
- expected snapshot
- authority commit
- discovery run
- broker observation
- reconstruction provenance
- formal reconciliation run
- policy
- scope
- capability registry evidence

Final PostgreSQL readiness verification must re-resolve or revalidate authoritative sources and must not trust caller booleans or arbitrary fingerprints alone.

Final verification and conditional handoff must share an authority fence / CAS contract that covers every readiness-relevant writer.

Fail closed:

- unresolved / incomplete positive evidence => REVIEW
- missing source / identity conflict / material conflict / explicitly unavailable required capability => HALT
- DB operational / programming error propagates

## AD-03 — Reconciliation Currentness

C15 must reuse C13 authoritative repository semantics.

C15 must not become another owner for latest、current、scoped、unresolved or blocking semantics.

Use C13 `unresolved(account)` semantics plus `blocking_case_state`.

If another read interface is needed, extend the C13 owner rather than duplicate SQL semantics.

Legacy NULL BrokerAccount scope remains fail-closed and must not be hidden by account WHERE filters.

Explicitly other-account cases do not block the current account.

Blocking semantics:

- HALT => readiness HALT
- REVIEW_REQUIRED => readiness at least REVIEW
- both => HALT precedence
- unknown state / scope conflict / version integrity conflict / legacy ambiguity => fail closed
- RESOLVED or no unresolved applicable case only means the case gate does not block

Any authoritative blocking-set change after evaluation invalidates the evaluation.

Pure audit metadata changes that cannot affect blocking semantics should not invalidate readiness.

## AD-04 — Exact Fill / Event Recovery Closure

Do not mechanically restrict all Fill/Event evidence to non-terminal Orders.

Exact scope is:

`minimum complete canonical transitive closure of the current required recovery roots`

Non-terminal Orders are primary roots.

Terminal-order evidence remains included only when required by:

- current snapshot provenance
- unresolved action
- pending material report
- reconstruction
- another current dependency root

Historical evidence with no current dependency may be excluded.

Canonical Fill identity:

- immutable fill_id
- verified Order/Event linkage

Canonical Event identity:

- immutable event_id
- verified entity identity
- sequence
- idempotency identity

Comparison semantics:

- Fill = identity-keyed set equality + exact material comparison
- Event = authoritative per-Order sequence equality
- cross-Order = identity map comparison
- aggregate hash only as summary with projection version + exact membership + per-record material
- count is never authority

Same identity + same material is idempotent replay.
Same identity + different material is integrity conflict.

Unknown payload fields are material by default unless explicitly classified as non-material metadata.

Missing required closure member、identity conflict、invalid linkage、invalid sequence or material conflict => HALT.

Legitimate concurrent current-world change invalidates the prior witness and requires re-evaluation.

## W4 Replan Required Output

Before any runtime authorization, produce a planning-only replan that defines:

1. continuity current-head model and producer contract
2. trusted resolver prerequisite and ownership
3. TrustedReadinessEvidenceBundle contract
4. C13 API reuse / extension design
5. minimum recovery-root transitive closure algorithm
6. all readiness-relevant writers
7. shared transaction / CAS / fence model for final handoff
8. exact schema additions / modifications
9. exact production files that would need modification
10. exact migration impact
11. isolated PostgreSQL conformance requirements
12. negative counterexamples
13. dependency order
14. new bounded leaf/package breakdown
15. weights and accepted-progress accounting
16. closure gate
17. whether W4 remains one Wave or is split into prerequisites + C15 completion

Required counterexamples:

- stale trusted epoch after a newer untrusted/degraded epoch
- EPOCH-1 vs EPOCH-10 substring collision
- forged / nonexistent capability source ref
- typed but unresolvable completeness / reconstruction provenance
- legacy NULL-scope reconciliation case
- cross-world evidence bundle
- duplicate identity with conflicting material
- concurrent readiness-relevant writer invalidating a pre-handoff evaluation

## Authorization Boundary

This decision grants planning only.

It does NOT authorize:

- production code changes
- test changes
- migration source changes
- migration execution
- actual PostgreSQL / V07
- A08 crash / concurrency execution
- broker / paper / Shioaji I/O
- credential access
- production activation
- RF03
- C16-C20 / P7

No executor coding is authorized until the replan is independently reviewed and a new bounded authorization is materialized.