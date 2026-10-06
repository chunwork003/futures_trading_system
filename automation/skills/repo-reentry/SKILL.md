# Skill: repo-reentry

Status: SHADOW

Trigger:
WORK_START / CODEX_START / MANUAL_REENTRY

Inputs:
repository, authoritative_branch, actor_role

Canonical reads:
1. fresh origin/master
2. docs/CURRENT_STATE.md
3. automation/work_orders/CURRENT_CODEX.yaml
4. exact pointers referenced by current state

Output only the minimum sufficient snapshot:
- current_head
- current package/work order/authorization
- execution and review state
- changed pointers
- exact next action
- stop reason if any

Rules:
- pointer/delta first
- unchanged repo+path+git-blob-SHA should not be reread without reason
- stale planning state is not current authority

Must not:
grant authority, infer missing authority, mutate repo, preload unrelated history.


## V2 successor procedure — candidate only

After reviewed activation follow development_entry_protocol.v2 and authorization_lifecycle.v1_1. Safety -> exact unfinished execution -> pending result/review/integration -> authorized new work. Provider recovery is wake-only; RESUME_PENDING_REVALIDATION requires exact fresh HEAD/authority/dispatch/invocation/scope/writer/provider/policy continuity. Historical phase snapshots are not current projections; contradictions require reconciliation. Owner procedure: single-use-lifecycle-guard/SKILL.md. No new identity/reservation/dispatch/budget for same invoked resume.
Architecture1.1 remains ACTIVE until fresh governance review and WORK materialization; candidate presence grants no authority. Provider denial always wins.
