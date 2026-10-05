> **GOVERNANCE RECONCILIATION RESOLVED — REVIEW ACTIVE**
>
> HUMAN_GOVERNANCE_OWNER explicitly adopted the immutable implementation/evidence SHAs as a semantic review candidate only.
> The original execution lifecycle remains recorded as NONCONFORMING and is not retroactively rewritten as conforming.
> No rerun, source modification, merge authority, acceptance, or AUTO-IMP-003 authority was granted.
>
> Adoption: `automation/work_orders/reconciliations/WO-AUTO-IMP-002-01.adoption.json`
> Reconciliation: `automation/work_orders/reconciliations/WO-AUTO-IMP-002-01.lifecycle.json`

# Independent review request — WO-AUTO-IMP-002-01

AUTO-IMP-002 implements exact Git-blob manifest integrity verification and a read-only unified re-entry snapshot resolver. Mechanical intake passed; semantic acceptance remains independent-review-only.

- package: AUTO-IMP-002
- authorization: AUTH-AUTO-IMP-002-01
- quota amendment: AMEND-AUTO-IMP-002-QUOTA-01
- execution id: EXEC-AUTO-IMP-002-20261005T083857515Z
- execution start: a078289281dcf81e751d44af1ae1ddbf43dcfabe
- claim: b8dcc8017fadfacae571c0e134cc424992ea953d
- implementation: 7d3e51802fb6d016bdd4f7d57908e01460535806
- evidence/final branch HEAD: eccbe997fe4f9f2a9da06026d75df11af9c3a937
- execution branch: auto/WO-AUTO-IMP-002-01
- exact source scope:
  - automation/engine/manifest.py
  - automation/engine/reentry.py
  - tests/automation/test_manifest.py
  - tests/automation/test_reentry.py
- implementation diff: 4 files, +555 / -0
- targeted: 29 passed
- full regression: 1542 passed, 8 skipped
- git diff --check: PASS
- scope violations: NONE
- correction budget remaining: 0
- AUTO-IMP-003: NOT_AUTHORIZED

## Required semantic review

Review the exact implementation/evidence SHAs and specifically verify:

1. manifest verification is pinned to one exact commit and hashes raw Git blob bytes, not worktree bytes;
2. CRLF/worktree normalization cannot alter the authoritative hash result;
3. manifest hash/path discovery does not accidentally treat provenance-only hashes such as previous_sha256 as current file bindings;
4. missing/ambiguous Git object, noncanonical path, symlink/tree, invalid YAML/mapping, malformed hash/path binding and unsupported hash semantics fail closed;
5. the re-entry snapshot reads canonical CURRENT before historical material and cannot let historical NEXT/current-looking blocks override the canonical projection;
6. status_only never dispatches or grants execution authority;
7. the returned candidate route remains advisory only: executor gates and single-use claim are still required before execution;
8. exact authority/work-order/quota/eligibility/package/dependency bindings fail closed on mismatch;
9. repository-known answers prevent unnecessary re-ask without silently inventing missing authority;
10. no runtime/broker/DB/migration/LIVE/production side effect is introduced;
11. exact four-file implementation scope is preserved.

Return one exact result bound to the implementation/evidence SHAs:

INDEPENDENT_AUTO_IMP_002_REVIEW = PASS

or

INDEPENDENT_AUTO_IMP_002_REVIEW = REVIEW_FIX_REQUIRED

If PASS, explicitly state whether AUTO-IMP-002 may proceed to governance closure/materialization.

If REVIEW_FIX_REQUIRED, provide finding IDs, counterexample, affected file/logic and minimum correction scope.

Mechanical intake PASS is not semantic acceptance. PASS does not authorize merge or AUTO-IMP-003. Correction budget is 0, so any required source correction routes to HUMAN_DECISION_REQUIRED unless new authority is explicitly granted.
