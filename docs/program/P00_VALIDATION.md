# P00 validation checkpoint — API / context / registries

Candidate only. Validation is not independent acceptance, runtime readiness or a dispatch grant.

## Executed

- `python -B scripts/p00_build_contracts.py`: generated two OpenAPI 3.1 candidates with 22 operations and 52 component schemas; finite workload policy stored separately.
- `python -B scripts/p00_build_contracts.py --check`: deterministic generation drift check.
- `python -B -m pytest tests/platform -q -p no:cacheprovider --basetemp .tmp/p00-platform-tests`: 59 passed (47.81 seconds at first full-suite run).
- After adding the durable simulation kill latch and HTTP 413 mapping, impacted contract/registry suites: 32 passed (0.57 seconds). Context code unchanged from its 27-test passing run.
- Actual repository active-policy Git blob SHA256 values checked against master manifest: PASS at `da09f7665ea286d18dc625268ae4b2e6f4acec10`; dirty worktree bytes were not used.
- Original request attachment hash and normalized repository blob hash are separately recorded in `current_truth.v1.json`. Their line-ending difference is not hidden or treated as policy drift.

## What tests establish

Closed DTOs reject extra authority fields, missing identity, noncanonical money, invalid modes and UNKNOWN actual-position objects carrying fabricated positions. Browser and internal authentication schemes remain separate; BFF mutations require CSRF. All local schema references resolve and synthetic shape examples validate.

Context fixtures establish deterministic selection/hash, inferred domain inclusion, exact Git object provenance despite dirty local files, rejection of stale active-policy hashes, path traversal, symlinks, missing files, unregistered packages and scope violations. Registry schemas prevent declaring current candidates authorized or independently qualified merely by changing a field.

## Not established

Dedicated OpenAPI specification validator is unavailable in the current environment; JSON Schema/reference checks are narrower. Synthetic examples prove shape only, not valid real object provenance. HTTP handlers, live DB transactions, lease race correctness, workload enforcement, container startup, UI journeys, broker behavior and production conformance have not been implemented or tested here. No product tests are rerun for this docs/offline-platform scope. No existing accepted runtime/policy source changed.

P00 still requires domain/adapter closure, handoff/compiler/golden evaluations, automation remapping, weighted progress ledger, compact CURRENT migration, requirement coverage completion and independent review. Do not turn this partial checkpoint into READY_FOR_EXECUTION.
