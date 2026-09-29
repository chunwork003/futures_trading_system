# GAP-08 W4R-D3 Independent Review RF01

Reviewed runtime:

`f0116524fb7254f912255023d2b80bf702a40f11`

Disposition:

`W4R-D3 HOLD / RF01_REQUIRED`

The D3 runtime candidate is retained except for the two bounded authority corrections below.

## Candidate material accepted for retention

The candidate correctly establishes:

- immutable `TrustedReadinessEvaluation`;
- pure trusted evaluator without caller convenience readiness booleans;
- constructor-scoped capability policy;
- first readiness-authority operation = active control `FOR UPDATE`;
- same-connection D2 re-resolution;
- same-transaction exact discovery receipt re-read;
- non-READY explicit rollback / no handoff;
- READY second active-control lock/recheck;
- reuse of existing C09 `finalize_handoff()`;
- exact generation / ingress / readiness CAS inputs;
- exactly one explicit commit on successful READY handoff;
- no migration / broker I/O / D2 owner changes;
- exact four-file scope;
- targeted / compatibility / full regression PASS.

Execution evidence:

- targeted: `88 passed`
- compatibility: `107 passed`
- full regression: `1375 passed / 4 skipped`
- semantic correction cycles: `0`
- test fixture/assertion corrections: `2`
- tooling retries: `0`
- user-observed 5HR: `20%`

Two semantic authority gaps remain.

## RF01-A — C14 boundary must bind B2 discovery and broker observation identity

The accepted D2 bundle contains:

- `formal_run_boundary.discovery_run_id`
- `formal_run_boundary.observation_id`
- `trusted_core.discovery_receipt_id`
- `trusted_core.broker_observation_id`

but the current bundle/evaluator path does not require equality between those pairs.

Therefore a formal C14 run established against one discovery/observation world could be combined with a B2 trusted core resolved from a different discovery/observation world and still reach the D3 evaluator.

That violates final same-world readiness authority.

### Required correction

In the D3 pure evaluator, before readiness classification, require:

```text
bundle.formal_run_boundary.discovery_run_id
    == bundle.trusted_core.discovery_receipt_id

bundle.formal_run_boundary.observation_id
    == bundle.trusted_core.broker_observation_id
```

Both exact identities must be present and equal.

Mismatch or missing linkage:

`TrustedRecoveryEvidenceError`

Do not modify the frozen D2 bundle model in RF01.

Do not modify C14 owner semantics.

## RF01-B — final handoff recorded_at must be canonically validated

Current finalizer constructs the completed inactive control using:

`captured.model_copy(update={"active": False, "recorded_at": recorded_at})`

Pydantic `model_copy(update=...)` does not re-run field validation on update material.

Therefore a caller can bypass `AccountRecoveryControl.recorded_at` canonical aware-UTC validation and pass naive/non-canonical time material into the final handoff write.

Frozen D3 requires an inactive completed control built with canonical aware UTC `recorded_at`.

### Required correction

Construct/revalidate the completed control through normal `AccountRecoveryControl` model validation.

Acceptable pattern:

```text
AccountRecoveryControl(
    broker=captured.broker,
    account_ref=captured.account_ref,
    generation=captured.generation,
    recovery_cut_revision=captured.recovery_cut_revision,
    ingress_version=captured.ingress_version,
    readiness_revision=captured.readiness_revision,
    active=False,
    recorded_at=recorded_at,
)
```

Equivalent full model re-validation is allowed.

Do not use `model_copy(update=...)` for the final completed control.

The canonical model validator remains the time authority.

## Required counterexamples

At minimum prove:

1. C14 boundary discovery ID different from trusted core discovery ID fails closed;
2. C14 boundary observation ID different from trusted core broker observation ID fails closed;
3. missing boundary discovery/observation identity fails closed;
4. matching exact identities preserve READY candidate path;
5. naive `recorded_at` cannot reach `finalize_handoff`;
6. canonical aware non-UTC input is normalized through `AccountRecoveryControl` before handoff;
7. READY handoff still uses exact generation/ingress/readiness;
8. successful READY still commits exactly once;
9. non-READY still rolls back and never handoffs;
10. no D2/C09/UoW owner changes.

## Governance

- W4R-A/B/C and W4R-D1A/D1B/D2 remain accepted/frozen.
- W4R-D3 remains HOLD until RF01 independent acceptance.
- isolated PostgreSQL integration/concurrency verification remains NOT_AUTHORIZED.
- W4 closure remains NOT_AUTHORIZED.
- P7 remains NOT_AUTHORIZED.
- internal W4R accepted parent weight remains `13/18` until D3 acceptance.
- official W4 weight remains `18 / NOT_CREDITED`.
