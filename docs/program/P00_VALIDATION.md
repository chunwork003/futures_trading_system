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

## Actual repository smoke and discovered limits

Exact candidate `0d3ca85946d85305071d0d5293b96bfe4d9ae005`: context hash `59ac86f6ff67ac686ee0488000a069bcd3a7274019f7b781caf5d0171be20739`, 23 mandatory / 2 optional files, 633847 mandatory bytes. Authority NONE_CONTEXT_ONLY; execution_eligible=false. This exceeds the 128 KiB planning target. Budget overflow is now reported explicitly; no source is silently omitted. R06 must implement reviewed compaction and selective contract loading before claiming fast bootstrap.

The installed jsonschema lacks its optional date-time checker. Tests now register an explicit UTC parser and lexical constraints; new fixtures cover invalid Gregorian date, hour 24, offset/missing zone and excessive fractional precision. The first hour-24 negative fixture exposed Python 3.14 normalization; explicit 00–23 schema bounds fixed it. This is a candidate schema-validation defect, not an accepted runtime defect. Tool versions are recorded in tests/platform/requirements.txt; this is not a full product dependency lock.

Final complete platform rerun after budget and timestamp corrections: **66 passed in 51.56 seconds** (`python -B -m pytest tests/platform -q -p no:cacheprovider --basetemp .tmp/p00-platform-release-check`). Generator check PASS. Authoritative remote master rechecked unchanged at `9b5ab5fdd98744a7db45ec9f14b64ef1f324920f`. Only P00 candidate docs/tooling/tests are changed; no accepted product runtime or active policy modifications.

## 2026-10-08 domain adapter checkpoint

Reconciled actual StrategyInstance version type, legacy symbol-based target/virtual positions and PriorityStrategyConflictPolicy. Preserved higher priority wins and rejected opposite-direction ties; removed the earlier candidate automatic ID tie-break. Added five domain schemas (57 total), immutable rejection semantics and distinct desired/staged target. Thirteen source/class bindings are checked against exact accepted baseline Git blobs. Full platform regression: **76 passed in 52.14 seconds**. No new runtime implementation or independent acceptance. Simulation genesis/auth-handler and first incremental codec remain design work.

Genesis/auth checkpoint: 22 internal domain operations, 4 BFF-only auth operations, 60 shared component schemas. Reserved genesis receipt requires null resource revision and a durable operation reference. Login requires CSRF despite anonymous authentication status; Python exposes no /auth routes. Full platform suite: **78 passed in 53.48 seconds**. Generator drift check PASS. Tests prove candidate structure/isolation; they do not prove future DB atomicity or running authentication handlers.

## Incremental codec / envelope / mechanical compiler checkpoint

First EMA codec matches existing batch adjust=False/min_samples semantics, with literal golden outputs, every golden restart boundary and nontrivial streams at spans 1/20/60. Hex persistence preserves exact binary64 state; invalid codec/fresh-state shapes reject. TradingEvidenceEnvelope preserves E/G ownership and explicit immutable metadata while accepted stores remain unchanged. Mechanical package compiler binds context/hash/scope and reports missing design or oversized context; it never grants authority. Full platform suite: **104 passed in 55.70 seconds**. Generated-contract drift check PASS. Product runtime, real PG transaction conformance and independent architecture acceptance remain outside this evidence.
