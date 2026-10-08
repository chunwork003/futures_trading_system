# Candidate bootstrap — P00

This entry point is not accepted runtime authority. Read `docs/program/p00_status.v1.json` for the exact unfinished architect step. Do not restart the full inventory or infer approval from generated files.

## Resume sequence

1. Read worktree branch/status and remote authoritative master SHA. Fetch only if needed; do not reset another writer's work. Compare with stored baseline and review relevant drift only.
2. Read `AGENTS.md`, canonical `docs/CURRENT_STATE.md`, manifest active policies, `docs/CURRENT_WORK.md`, current handoff/result/STOP pointers. A source snapshot is not necessarily the current legal runtime route.
3. Read this candidate's status/package and capability registries. Separate IMPLEMENTED_PENDING_REVIEW from accepted behavior; no operational maturity based on a file existing.
4. Build a context manifest from an exact committed SHA with `scripts/p00_context.py`. For P00 API work select `--task ARCHITECT --package P00 --domains api product`. Uncommitted changes require a separate reviewed delta; the resolver intentionally ignores worktree bytes.
5. Load mandatory context first, optional context only for a specific open question. Read latest relevant delta and unresolved findings before editing. Context hash is an evidence binding, never authorization.
6. Finish the saved continuation, run relevant tests, report exact candidate/validation and preserve pending work. CODEX starts only after independent architecture acceptance plus exact package grant.

Example (replace SHA with the verified committed candidate; do not literally pass the placeholder):

```text
python -B scripts/p00_context.py --baseline <40-character-SHA> --task ARCHITECT --package P00 --domains api product
```

## Knowledge owners and precedence

Authoritative Git branch anchors accepted architecture/ADRs, active Program, accepted execution/review/integration evidence, machine current projection, compact CURRENT, relevant deltas, then historical records. Copied chat/prompts are contextual history, not an inferred current grant. A new direct human instruction can authorize bounded architect work; materialize its provenance and scope rather than claiming preexisting controller authorization.

`docs/CURRENT_STATE.md` remains the current operational navigation owner until its successor projection migration is reviewed and accepted. Candidate registries/context packs do not supersede it. Active policy SHA mismatch, unresolved accepted-document contradiction or stale grant binding means stop affected execution; do not arbitrarily choose the shorter/newer document. P00 source artifacts can coexist with an unchanged operational route.

Stable architecture: `docs/architecture/`; program/deliverables/continuation: `docs/program/`; operational CURRENT: existing canonical pointers; machine development indexes: `automation/platform/`; evidence: exact Git blobs and test outputs. Each field has one owner. Generated projections refer back to the owner, not create another editable truth.

## Current resolver coverage and limitations

Input has exactly task_type/package_id/changed_paths/architecture_domains/baseline_sha. Output provides mandatory/optional/forbidden-stale references, raw Git blob SHA256, context_hash and execution_eligible=false. Changed paths infer additional domains. P00 and planning-only P01/P02 candidates are registered; P01/P02 use exact allowlists and remain non-executable while public semantics/acceptance gates are open. Active policies are resolved through the manifest and verified byte-for-byte. Inactive policies are excluded from normal current context, but can be explicitly examined as historical evidence in a separate bounded audit.

The resolver reports a 128 KiB mandatory-context byte target; excess is flagged, never silently truncated. Real candidate snapshot measurement was about 634 KB, so fast bootstrap is NOT yet achieved. Legacy CURRENT files still contain historical sections, so their whole-file references currently cost more context. Compact projection migration is pending R06; this tool does not pretend that extracting a header resolves all lifecycle authority. It also does not automatically discover every latest open result/delta inside prose. WORK must perform accepted re-entry; deterministic machine pointer integration remains a compiler/re-entry gate.

No network, writes, provider dispatch, credentials or repository scanning inside the resolver. Registry role definitions are logical responsibilities, not eight always-running agents. Independent reviewer context must exclude the author's unstated conclusions while retaining adverse evidence and exact contracts.

## Validation commands

```text
python -B scripts/p00_build_contracts.py --check
python -B -m pytest tests/platform -q -p no:cacheprovider --basetemp .tmp/p00-platform-tests
git diff --check
```

The isolated context tests create temporary Git repositories only under the chosen test directory. Python jsonschema and pytest are validation dependencies, not new product runtime dependencies. Passing these tests does not qualify production/live operation or independently accept this baseline.

## Source versus planning snapshot

`source_baseline_sha` is the proposed product baseline; `request.baseline_sha` is the later planning/tool snapshot. The resolver verifies ancestry and exact operational-pointer preservation. It binds its loaded source to the snapshot (CRLF transport only), while compiler CLI additionally binds compiler/schema source, regenerates context and checks registered candidate JSON values. This proves source/snapshot consistency, not independent review or secure-process attestation.

## Candidate reading pack (R06)

`scripts/p00_context_pack.py` regenerates context from the exact planning snapshot and verifies its own source binding. It emits complete JSON values in compact form and pools identical OpenAPI schemas by canonical SHA256. A reader can reconstruct every original JSON value with `expand_json`; all paths, security declarations, constraints and descriptions remain. Non-JSON YAML stays verbatim.

Only CURRENT_STATE and CURRENT_WORK may use the exact existing `HISTORICAL CURRENT PROJECTIONS BELOW` marker. The current prefix is retained verbatim; the historical suffix has an explicit source Git blob, start line and text hash. The first explicit marker starts the whole history suffix; later markers remain inside that suffix. Missing markers or an empty current prefix fail closed. All AGENTS instructions and active policy fields remain present. Historical inquiry, lifecycle provenance, unresolved contradiction and relevant review require loading the full linked source. This is not a semantic summary.

The reading pack is a candidate reading aid, not an authority projection or an executable handoff. The resolver/compiler still use full-source evidence and their existing byte-budget gate. Lower byte count alone cannot remove that gate. Latest result/delta intake and independent projection review remain necessary before any migration. Metrics measure exact compact UTF-8 output bytes, not guessed tokens; original evidence size is retained separately.

## Selective reading and result references

See `CONTEXT_SELECTION_AND_RESULT_INTAKE.md` for candidate profiles, exclusion manifests and exact predecessor/compilation reading. `--selective` projections are explicitly partial API views; expand_json restores only the selected projection. The full-source compiler gate and current re-entry procedure remain unchanged. Complete current result/review/STOP intake is not implemented.
