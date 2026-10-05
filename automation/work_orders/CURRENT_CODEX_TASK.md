# AUTO-IMP-001 bounded correction — unattended Codex pilot

這份 task packet 只執行 `WO-AUTO-IMP-001-CORR-01`。
本輪目標是先證明 Work -> Codex 自動執行鏈可以無人工 quota 確認地完成。
Token / quota 最佳化延後到自動鏈穩定後再做。

## Pilot authority

Authoritative pilot record:

`automation/work_orders/AUTO_DISPATCH_PILOT_20261005.yaml`

Key decisions:

- automatic dispatch: ALLOWED_FOR_THIS_EXACT_WORK_ORDER
- human manual trigger: NOT_REQUIRED
- quota admission threshold: DISABLED_FOR_THIS_PILOT
- 80% minimum gate: NOT_USED
- fresh human Usage confirmation: NOT_REQUIRED
- machine-readable token usage required to start: NO
- token usage if available: RECORD
- if unavailable: report NOT_AVAILABLE and continue
- expires: 2026-10-05T21:00:00+08:00
- AUTO-IMP-002: NOT AUTHORIZED BY THIS PILOT

Do not reinterpret the historical frozen 80% bootstrap threshold as an execution gate for this exact pilot.

## Exact correction goal

Reviewer verdict = REVIEW_FIX_REQUIRED.

Defect:
`automation/engine/yaml_io.py` currently uses PyYAML behavior that allows duplicate mapping keys, silently keeping the later value.

Required correction:
Reject duplicate YAML mapping keys at every mapping depth and raise `AutomationYamlError`.

Required assertions:
- top-level duplicate key rejected
- nested duplicate key rejected
- nested mappings inside containers also reject duplicates
- preserve existing safe YAML and contract behavior

## Exact implementation write scope

Only:
- `automation/engine/yaml_io.py`
- `tests/automation/test_contracts.py`

Do NOT modify:
- `automation/engine/contracts.py`
- authorization files
- governance / policy / package / historical run files
- docs
- runtime trading code
- broker / DB / migration / LIVE / production / credentials

Executor metadata may additionally write only:
- `automation/work_orders/executions/**`

## Execution start and exclusive writer claim

1. `git fetch origin master`.
2. Read latest:
   - `automation/work_orders/CURRENT_CODEX.yaml`
   - `automation/work_orders/AUTO_DISPATCH_PILOT_20261005.yaml`
3. Require:
   - CURRENT_CODEX.status = READY_FOR_CODEX
   - CURRENT_CODEX.handoff_ready = true
   - work_order_id = WO-AUTO-IMP-001-CORR-01
   - pilot status = AUTHORIZED_BOUNDED
4. Verify `code_base_sha` is ancestor of current `origin/master`.
5. Verify every path changed from `code_base_sha..origin/master` is under:
   - `automation/work_orders/**`
   Any other drift => STOP.
6. Record current `origin/master` as `execution_start_sha`.
7. Confirm remote branch does NOT already exist:
   - `auto/WO-AUTO-IMP-001-CORR-01`
   Use ordinary git commands such as `git ls-remote --heads origin ...`; do not require gh CLI or private GitHub REST API.
8. Create local branch from `execution_start_sha`.
9. Before any source edit, create one unique empty claim commit, for example:
   `git commit --allow-empty -m "chore(automation): claim WO-AUTO-IMP-001-CORR-01 <unique-id>"`
10. Push that claim commit to:
    `origin auto/WO-AUTO-IMP-001-CORR-01`
    without force.
11. If branch already exists or the claim push is rejected:
    STOP. Treat the work order as already claimed.
12. A successful first push is the exclusive writer claim for this pilot.

No Publisher RUNNING claim is required before this.
No human quota input is required.
No 80% threshold is checked.

## Implementation

After successful claim:

- implement duplicate-key rejection at parser/load boundary
- fail closed at every mapping depth
- raise `AutomationYamlError`
- keep the change minimal
- important comments/docstrings in Traditional Chinese

Do not redesign nested contracts or Master Architecture.

## Tests

Run at least:

`python -m pytest tests/automation/test_contracts.py -q -p no:cacheprovider`

Then:

`python -m pytest -q -p no:cacheprovider`

Also:

`git diff --check`

Implementation diff scope must be exactly within:
- `automation/engine/yaml_io.py`
- `tests/automation/test_contracts.py`

If required tests still fail after the remaining bounded correction cycle:
STOP with HUMAN_DECISION_REQUIRED.

## Git result

After tests pass:

1. Commit the implementation once.
2. Push the same remote branch.
3. Create a PR to master if the executor environment provides a working PR creation path.
4. If PR creation is unavailable, continue without blocking: keep the pushed branch and completion evidence; Work will create the PR on the next cycle.
5. Do NOT merge.
6. Work performs result intake/review.

PR creation is non-blocking for this pilot. Missing PR tooling must not block coding, tests, commit, branch push, or completion evidence.

## Machine-readable completion evidence

Create one result record under:

`automation/work_orders/executions/WO-AUTO-IMP-001-CORR-01.json`

It must include:
- work_order_id
- execution_start_sha
- claim_commit_sha
- implementation_commit_sha
- changed implementation files
- targeted test result and exit code
- full regression result and exit code
- git diff --check result
- correction cycles used
- correction budget remaining
- scope violations
- machine-readable token usage if exposed, otherwise `NOT_AVAILABLE`
- branch push result
- status = COMPLETED_PENDING_REVIEW
- AUTO-IMP-002 = NOT_STARTED

Commit and push this metadata on the same branch after the implementation commit.

## STOP conditions

STOP only for:
- atomic branch claim conflict
- non-work-order drift after code_base_sha
- correction budget exhausted/uncertain
- reviewer verdict no longer binds to AUTO-IMP-001
- architecture/authority/write-scope/side-effect expansion required
- protected-file modification required
- unrelated regression
- original CONSUMED authorization would need redispatch

Do NOT STOP for:
- Usage remaining below 80%
- missing fresh human Usage confirmation
- machine-readable token usage NOT_AVAILABLE
- inability to create a PR
- gh CLI unavailable
- private GitHub REST API unavailable

The purpose of this pilot is to run the bounded automation first and optimize token/quota behavior afterward.

STOP after this one work order.
