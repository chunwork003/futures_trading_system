# Reconciliation execution material
Status: BLOCKED. Existing policies sufficient; no architecture escalation.
Read reconciliation.json and REV6.authorization-candidate.json in this directory.
Remote verified master baseline b36e9bc253a13a3a361b3861e607455658df524b; committed source candidate 52f0b5da1d050a8876f9716b227055219f4fd070.
Forensic/budget/dirty status are explicitly HUMAN_REPORTED until exact checkpoint evidence is published.

## Current disposition
Execution axis STOPPED; reason RECONCILIATION_REQUIRED / STOP_NO_BACKFILL.
REV5 remains CONSUMED, not reset/reused. Original handoff/dispatch/reservation/false invocation evidence immutable.
Source commits preserved, not semantically accepted.
Writer remains HELD until the ordered reconciliation release below. No CODEX now.

## Operator checkpoint (run from repo root, with old executor actually stopped)
Fetch this directory's preserve-batch4.ps1 from remote master into .tmp without editing source.
Run:
```powershell
& .\.tmp\preserve-batch4.ps1 -ConfirmNoActiveExecutor -RestoreTracked
```
The script uses a private temporary Git index, includes the untracked test, emits Git raw binary/full-index patch bytes directly, reconstructs identical tree in a second temporary index, records all8 hashes, then restores only approved tracked paths and moves the new test to the verified checkpoint directory.
No reset --hard, git clean, data move/delete, or known-failing source commit.
On any error STOP; preserve partial checkpoint. No lifecycle allocation.
The command's flag is an operator attestation of an actual fact, not authority approval.

## Publish checkpoint as evidence (isolated control-plane worktree only)
Use the exact CHECKPOINT_DIRECTORY returned above as $CheckpointDir.
```powershell
$EvidencePath = 'automation/work_orders/reconciliations/EXEC-AUTO-GOV-PROGRAM-1_2-ORCH-MANUAL-20261006T122032Z/checkpoint'
git fetch origin master
if ($LASTEXITCODE) { throw 'FETCH_FAILED' }
$ControlHead = (git rev-parse origin/master).Trim()
$ControlTree = Join-Path $env:TEMP ('fts-reconciliation-' + [guid]::NewGuid().ToString('N'))
git worktree add --detach $ControlTree $ControlHead
if ($LASTEXITCODE) { throw 'CONTROL_WORKTREE_FAILED' }
$PublishDir = Join-Path $ControlTree $EvidencePath
New-Item -ItemType Directory -Path $PublishDir -Force | Out-Null
Copy-Item -LiteralPath (Join-Path $CheckpointDir 'Batch4.checkpoint.patch') -Destination (Join-Path $PublishDir 'Batch4.checkpoint.patch')
Copy-Item -LiteralPath (Join-Path $CheckpointDir 'Batch4.checkpoint.json') -Destination (Join-Path $PublishDir 'Batch4.checkpoint.json')
git -C $ControlTree add -- $EvidencePath
if ($LASTEXITCODE) { throw 'EVIDENCE_ADD_FAILED' }
git -C $ControlTree diff --cached --name-only
# Only the two evidence files above may appear.
git -C $ControlTree commit -m 'gov: preserve exact Batch4 checkpoint for execution reconciliation'
if ($LASTEXITCODE) { throw 'EVIDENCE_COMMIT_FAILED' }
git -C $ControlTree fetch origin master
if ($LASTEXITCODE) { throw 'REFRESH_FAILED' }
if ((git -C $ControlTree rev-parse origin/master).Trim() -ne $ControlHead) { throw 'MASTER_DRIFT_REVALIDATE_NO_FORCE_PUSH' }
git -C $ControlTree push origin HEAD:master
if ($LASTEXITCODE) { throw 'PUBLISH_FAILED_NO_FORCE_PUSH' }
```
These commands publish evidence, not authorize implementation. No credentials printed or collected.

## Writer release ordering — WORK, after remote checkpoint exists
1. Read exact checkpoint commit/hash/tree/path list and quiescence attestation; bind to source HEAD, master and this reconciliation commit.
2. Fresh verify old execution/REV5 lock remains exact owner; no other executor active; no source drift.
3. Append automation/runs/EXEC-AUTO-GOV-PROGRAM-1_2-ORCH-MANUAL-20261006T122032Z/writer_release.json with reason EXPLICIT_RECONCILIATION, previous HELD blob, reconciliation/checkpoint commit, timestamp, no invocation proof, actual source preserved.
4. Update current automation/runs/EXEC-AUTO-GOV-PROGRAM-1_2-ORCH-MANUAL-20261006T122032Z/writer_lock.yaml state RELEASED, released_at and release evidence pointer. Preserve previous HELD bytes in Git; do not edit historical dispatch/reservation/handoff.
5. CURRENT writer_state RELEASED and old execution STOPPED, no handoff. No concurrent writer proof required before any successor acquisition.
6. Keep old execution non-resumable; optional supersession sidecar only when actual authorized successor exists. Do not label it completed/accepted.

## Budget/authorization barrier
Implementation2/2 exhausted. Owner artifact budget_renewal=DENIED; review-fix2 requires independent REVIEW_FIX_REQUIRED, unavailable for forensic PASS.
Required narrow human action: explicitly approve one additional Batch4 encoding-compatibility implementation correction cycle for REV6, exact8 checkpoint restore + two-file correction, architecture unchanged.
No architecture decision required. Candidate AUTH is NOT_AUTHORIZED and cannot be consumed.

## Fresh CODEX lifecycle, only after prerequisites
Same logical WO; new exact AUTH REV6, new execution pattern EXEC-AUTO-GOV-PROGRAM-1_2-ORCH-CODEX-<UTC yyyyMMddTHHmmssZ>.
Compile authority binding source52f0..., exact8 scope digest/checkpoint SHA, added budget grant, protected13 remaining main source blobs, fresh architecture bundle and continuation forecast. Unknown checkpoint/future execution prevents authorization now.
1 FRESH_AUTHORITY_RESOLUTION (new exact Owner grant, old consumed not reused).
2 FRESH_ELIGIBILITY_EVALUATION (checkpoint/clean source/released writer/current architecture/scope/provider5H MANUAL P75).
3 ACQUIRE_GLOBAL_RUNTIME_WRITER_LOCK for CODEX only.
4 ALLOCATE_EXECUTION_ID now, never during planning.
5 DURABLY_CREATE_EXECUTION_RESERVATION with fresh source/controlplane/exactscope references.
6 STATE_TO_RESERVED.
7 RECHECK_LOCK_HEAD_AND_BINDING including fresh provider/capacity.
8 MARK_DISPATCH_COMMITTED.
9 STATE_TO_CONSUMED.
STOP READY_FOR_MANUAL_CODEX_TRIGGER.
10 INVOKE_EXECUTOR only on manual trigger; executor contemporaneously records actual invocation evidence BEFORE source edits. No retroactive backfill.
New branch auto/WO-AUTO-GOV-PROGRAM-1_2-ORCH-01-REV6; no old HUMAN_DIALOGUE execution identity inheritance.

## Test plan / barrier
{
  "shells": [
    "Windows PowerShell5.1 REQUIRED",
    "PowerShell7 if installed; absence recorded NOT_AVAILABLE not false PASS"
  ],
  "cases": [
    "four previously failing cases",
    "pause=False positive control",
    "minimal legacy empty payload",
    "optional bands absent/null/partial",
    "test_cycles absent/null/partial",
    "structural evidence absent/null/partial",
    "provider_interruption empty object preserved",
    "provider pause telemetry and capacity review signal",
    "provider_pause_is_source_defect=false",
    "no automatic split authority"
  ],
  "commands": [
    "python -m pytest -p no:cacheprovider tests/automation/test_execution_cost_reconcile.py",
    "python -m pytest -p no:cacheprovider tests/automation/test_execution_cost_reconcile.py tests/automation/test_execution_capacity.py tests/automation/test_orchestration.py tests/automation/test_contracts.py"
  ],
  "full_regression": "Only after targeted/cross-targeted PASS: one full regression when required by existing test-cost policy; no repeats for metadata/hash-only changes"
}
STOP immediately on architecture/authority/lifecycle/sideeffect/scope expansion, competing writer, contradiction, unprovable HEAD/scope/authority, or failure beyond forensic encoding issue.
PASS barrier: COMPLETED_PENDING_REVIEW for WORK intake; final cohesive ProgramV2 review/acceptance remain distinct. No merge or next package.
Conditional exact CODEX prompt: CODEX_HANDOFF_CANDIDATE.md (not executable until gates materialized).
