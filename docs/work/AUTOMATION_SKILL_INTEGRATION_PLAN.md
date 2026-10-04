# Automation Skill Integration Plan

Status:

```text
DEFERRED_PLANNING_ONLY
```

Candidate future leaf:

```text
AUTO-IMP-SKILL-001
Automation Skill Adapter / Skill Registry
```

## Goal

After the Automation v1.1 foundation is proven stable, convert repeatable operational playbooks into reusable Skills so new ChatGPT/WORK/CODEX sessions can enter with less repeated context while preserving repository-canonical governance.

## Layering

```text
Human / WORK
  -> Automation Control Plane
  -> Re-entry / State / Authorization / Quota / Review
  -> Skill Adapter / Skill Registry
  -> Reusable Skills
  -> CODEX / ChatGPT / MCP / shell
  -> Result / Telemetry / Review / Governance Materialization
```

Governance is above Skills. Skills describe how to perform repeatable permitted work; they never decide whether work is authorized.

## Candidate Skills

- `repo-reentry`
- `exact-binding-validator`
- `bounded-package-executor`
- `quota-eligibility-check`
- `reviewer-packet-builder`
- `historical-replay-review`

## Hard Rules

Skills MUST NOT:

- grant or infer authorization;
- mutate AuthorizationLifecycle or QuotaAdmissionPolicy;
- infer Runtime Authorization from package/source authorization;
- bypass `docs/CURRENT_STATE.md`;
- silently expand read/write/protected scope;
- auto-advance to another package;
- bypass fresh quota/telemetry/writer checks;
- activate broker/migration/LIVE/production behavior.

Skills MAY:

- read canonical repository governance;
- perform a permitted reusable workflow;
- call approved tools/executors within the active side-effect envelope;
- emit normalized evidence/result/handoff.

## Stability Trigger Before Skill Implementation

Do not implement `AUTO-IMP-SKILL-001` until all are true:

1. `AUTO-IMP-001` through `AUTO-IMP-005` foundation capabilities are accepted, or Architecture Owner explicitly narrows the prerequisite with evidence.
2. Re-entry, authorization, quota, and negative-assertion contracts have stable machine-readable schemas.
3. At least 2-3 bounded packages (or equivalent accepted stability cohort) complete without unauthorized scope expansion.
4. No unresolved repeated context/authority defect requires architecture changes.
5. Skill integration can be introduced without changing current package authority or the frozen 001-009 DAG.

At trigger time, compile a new planning leaf/program revision; do not silently insert it into the current authorized package.

## Optimization Goal

Measure whether Skills reduce:

- repeated context tokens;
- re-entry reading;
- manual prompt duplication;
- task-contract regeneration;
- reviewer packet construction cost;
- human intervention caused by workflow inconsistency.

Optimization must not reduce safety evidence or governance checks.
