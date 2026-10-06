# Exact manual CODEX handoff — V2 RF01

Status: `READY_FOR_MANUAL_CODEX_TRIGGER`
Execution: `EXEC-AUTO-GOV-EXEC-CAPACITY-V2-RF01-20261006T063605Z`
Work Order: `WO-AUTO-GOV-EXEC-CAPACITY-V2-RF01-01`
Authorization: `AUTH-AUTO-GOV-EXEC-CAPACITY-V2-RF01-01` (CONSUMED, reserved first invocation only)

Fresh fetch origin/master. Read CURRENT and exact WO `automation/work_orders/WO-AUTO-GOV-EXEC-CAPACITY-V2-RF01-01.yaml`, authorization, forecast and run `automation/runs/EXEC-AUTO-GOV-EXEC-CAPACITY-V2-RF01-20261006T063605Z` pointers FROM origin/master. Candidate historical CURRENT/auth are not authority.

Fresh verify durable steps1-9, no invocation/completion, exact writer, no competing writer, no revocation/supersession, only own control-plane master descendants, provider ordinaryUsageAllowed=true and no hard/rate/spend denial. Any failed gate STOP. This prompt is not an automatic trigger.

Source candidate: `e414c108e075c8aa2307d607ffe77013b40c5391`. Create a clean isolated correction branch `auto/WO-AUTO-GOV-EXEC-CAPACITY-V2-RF01-01` at this exact source commit; stop if branch already exists unless exact canonical same-execution claim reconciliation proves legal continuation. Do not check out master as implementation base: it does not contain unaccepted V2. Do not copy candidate old control-plane state to master, do not cherry-pick the old execution branch, do not merge candidate. Master is authority; e414 is source provenance.

Writable source ONLY:
- `automation/engine/execution_capacity.py`
- `tests/automation/test_execution_capacity.py`
- `automation/engine/contracts.py`
- `tests/automation/test_contracts.py`

Fix ONLY V2-CAL-01/V2-SER-01 per exact WO. Verify original19 protected candidate blobs unchanged plus historical identities. Minimum two finding counterexamples -> impacted until clean -> one complete targeted -> one full regression -> diff-check/scope/hash checks. Preserve all unrelated reviewed PASS semantics. Serializer warnings explicitly captured; internal sections remain deeply immutable.

Publish only four-file source correction delta against e414 and own completion/cost evidence. Record exact start/master/source/claim/implementation/evidence, tests/exit/timing, raw provider before/after and local-token PENDING_EXTERNAL_EXTRACTION. Result `COMPLETED_PENDING_RE_REVIEW`; no activation/acceptance/integration. No automatic RF02. Scope expansion or extra architecture requirement STOP.

Architecture1.1 ACTIVE;1.2 CANDIDATE_REVIEW_FIX_REQUIRED. IVF01 BLOCKED; no IVF01Rev2; AUTO-IMP-003NOT_AUTHORIZED. Runtime/broker/DB/migration/LIVE/production DENIED.

After publication STOP; WORK intake/token/reconcile -> fresh narrow review of effective original23+fourfiledelta candidate.
