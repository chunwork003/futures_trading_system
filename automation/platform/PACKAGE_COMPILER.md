# Mechanical package compiler — candidate v1

`package.schema.v1.json` contains the required identity/authority/design/dependencies/verification/completion shape. `scripts/p00_compile.py` consumes that package plus a previously produced exact context manifest and prints a deterministic compiled candidate. It performs no writes, tests, provider calls, acceptance or dispatch.

Checks: closed schema, nonempty required design fields, positive deliverable weights, exact baseline/package/scope equality, context hash, protected-path overlap, safe paths, required dependency evidence hash binding, explicit design gaps and context byte-budget status. Output includes package/context/schema/scope hashes and execution_eligible=false unconditionally. DRAFT/gaps/over-budget context/external gates yield PACKAGE_NOT_READY. Otherwise status is COMPILED_CANDIDATE_PENDING_INDEPENDENT_REVIEW, never READY_FOR_EXECUTION.

```text
python -B scripts/p00_compile.py --package <candidate-package.json> --context <exact-context-manifest.json>
```

Inputs are explicitly selected local JSON files. Hash integrity is not a signature or proof that the supplied context was produced by a reviewed process. WORK must regenerate/verify context from exact Git evidence before using compiler output. Required acceptance hashes prove only binding, not acceptance status; existing WORK/re-entry owns legal eligibility.

Remaining R03: semantic schema/transition-reference validation, real P01/P02 packages with exact allowlists and fixtures, canonical weight-ledger conservation, latest-result handoff integration, reviewed compiler-version binding, example templates/patterns and independent qualification. String fields can still contain inadequate prose, so a mechanically complete package is not a proof of design completeness. No current product package is registered/authorized through this compiler.

The compiler is an early mechanical gate, not a replacement for accepted automation engine/state machine. Do not introduce another writer lock or authority store here.
