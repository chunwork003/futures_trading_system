Duplicate YAML mapping keys previously silently overwrote earlier values. This AUTO-IMP-001 correction rejects duplicates at the loader boundary and adds top-level, nested, and container mapping tests. Independent semantic review is required; mechanical intake does not establish acceptance.

- work_order_id: WO-AUTO-IMP-001-CORR-01
- package_id: AUTO-IMP-001
- correction_id: AUTO-IMP-001-DUPKEY-RF01
- execution_start_sha: b2dbe51568674a936d6da4a811b45943198b905c
- claim_commit_sha: d03809db4a020eec4ab68547fbb6fbf130b4b15e
- implementation_commit_sha: 2a8974acbb7319ce55b3d7fb88737ad027061244
- evidence_commit_sha: 383ea7305557575a3c5330a1c2e2e54161d1dceb
- changed implementation files: automation/engine/yaml_io.py; tests/automation/test_contracts.py
- protected automation/engine/contracts.py: unchanged (remote commit diff)
- targeted tests (executor report): 19 passed, exit 0
- full regression (executor report): 1508 passed, 8 skipped, exit 0
- git diff --check (executor report): PASS
- scope violations: NONE
- correction cycles used: 1; budget remaining: 0
- tooling retries: 2
- machine-readable token usage: NOT_AVAILABLE
- branch push: SUCCESS; verified remote head matches evidence commit
- AUTO-IMP-002: NOT_STARTED
- evidence: automation/work_orders/executions/WO-AUTO-IMP-001-CORR-01.json

Reviewer: independently assess fail-closed rejection at every mapping depth, SafeLoader safety, valid-document compatibility, and exact two-file scope. Return a verdict bound to these exact commit SHAs. No automatic merge or next-package authorization.
