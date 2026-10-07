# AUTO-IMP-002 revision 2 — planning only; NO CODEX EXECUTION

Current route: `HUMAN_AUTO_IMP_002_REV2_IMPLEMENTATION_AUTHORIZATION_DECISION`.
`handoff_ready=false`; `execution_authority=NOT_AUTHORIZED`; no writer/reservation/dispatch/execution ID. Do not claim, invoke CODEX, or resume an old AUTO-IMP-002 execution.

- Baseline: `b56494966f33c47ea7744c5c1fed271ad01b39f1` (accepted Program V2 master).
- Package candidate: `automation/packages/AUTO-IMP-002.v2.candidate.yaml`
- Work Order candidate: `automation/work_orders/WO-AUTO-IMP-002-REV2-01.candidate.yaml`
- Exact plan/interfaces/test/review/dependency pointers: `automation/work_orders/planning/AUTO-IMP-002-REV2.compilation.json`
- Authority preparation: `automation/work_orders/AUTO-IMP-002-REV2.authorization-prep.json` (NON_AUTHORITY_CANDIDATE).
- Forecast: `automation/work_orders/forecasts/WO-AUTO-IMP-002-REV2-01.json`
- Historical retirement: `automation/work_orders/reconciliations/AUTO-IMP-002.historical-lineage-retirement.json`
- Owner strategy: `automation/governance/decisions/OWNER-AUTO-IMP-002-REV2-FRESH-PROGRAM-V2-BASELINE.json`

Proposed implementation paths (not writable until exact new authority):
- `automation/engine/repository_snapshot.py`
- `automation/engine/yaml_io.py`
- `tests/automation/test_contracts.py`
- `tests/automation/test_repository_snapshot.py`

All historical AUTO-IMP-002 correction/auth/execution/source/budget lineage is EVIDENCE_ONLY. Program V2 accepted semantics remain; snapshot assembly delegates accepted orchestration route resolution. AUTO-IMP-003 not authorized; controller not active; CONTROLLED_AUTO disabled; unsafe side effects denied. STOP for Human revision2 implementation authorization decision.
