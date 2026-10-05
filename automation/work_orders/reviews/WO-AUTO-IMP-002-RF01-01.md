# Independent re-review request — WO-AUTO-IMP-002-RF01-01

This is a bounded re-review of AUTO-IMP-002 RF01 for finding `AUTO-IMP-002-REVIEW-BINDING-01`.

Canonical parent verdict:
- automation/work_orders/reviews/WO-AUTO-IMP-002-01.verdict.json

Exact candidate:
- source candidate: eccbe997fe4f9f2a9da06026d75df11af9c3a937
- implementation: 523e5a3b62af78991995765eaa555edb40b79e43
- durable evidence: 0c64a9f509ba27c1bc1bad139681951e2f8c2775
- branch: auto/WO-AUTO-IMP-002-RF01-01
- execution: EXEC-AUTO-IMP-002-RF01-20261005T093900Z

Exact source scope:
- automation/engine/reentry.py
- tests/automation/test_reentry.py

Protected unchanged:
- automation/engine/manifest.py
- tests/automation/test_manifest.py

Mechanical evidence:
- canonical reviewer counterexample reproduced before fix
- full negative matrix before fix: 43 failed, 30 passed, 11 deselected
- final targeted: 84 passed
- full regression: 1615 passed, 8 skipped
- git diff --check: PASS
- exact two-file scope: PASS
- protected manifest blobs: unchanged
- external DB/migration: not executed
- canonical single-use lifecycle: PASS / CONSUMED before source edit

## Required semantic re-review

Verify the RF01 implementation closes the parent finding without new authority leakage or over-strict false rejection.

Specifically verify:

1. Contradictory CURRENT/WORK pointer, identity, revision, authorization-state, quota-amendment state/effect, eligibility, package, executor-profile, scope-digest and dependency bindings fail closed before any `CODEX_EXECUTION_CANDIDATE`.
2. A byte-valid duplicate document at the wrong pointer still fails closed.
3. Supplemental non-authority WORK metadata may differ without forcing false rejection, while any provider-limit/scope/authority expansion still fails closed.
4. Dependency acceptance validates exact dependency identity plus ACCEPTED_MATERIALIZED state, not status alone.
5. Package blob/scope identity remains pinned to the exact repository commit.
6. Read-only/status-only/canonical-CURRENT semantics remain intact.
7. No runtime/broker/DB/migration/LIVE/production side effect or AUTO-IMP-003 authority is introduced.
8. The correction remains within the exact two-file source scope.
9. The implementation does not weaken the previously reviewed manifest behavior.

Return exactly one semantic result bound to the implementation/evidence SHAs:

`INDEPENDENT_AUTO_IMP_002_RF01_RE_REVIEW = PASS`

or

`INDEPENDENT_AUTO_IMP_002_RF01_RE_REVIEW = REVIEW_FIX_REQUIRED`

If PASS, explicitly state whether AUTO-IMP-002 may proceed to governance closure/materialization.

If REVIEW_FIX_REQUIRED, provide finding IDs, concrete counterexample, affected logic/file and minimum correction scope.

Correction budget remaining is 0. A new source correction requires a new HUMAN_GOVERNANCE_OWNER decision. PASS does not authorize merge or AUTO-IMP-003.
