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
