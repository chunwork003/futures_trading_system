# GAP-08 W4R Package Freeze

Planning baseline:

`150053fcf638e347ffe0067a6f4a71d5baa31b9b`

Parent architect decision:

`docs/work/GAP08_WAVE4_ARCHITECT_DECISION_REPLAN.md`

VIBE replan:

`docs/work/GAP08_WAVE4_REPLAN_V2.md`

Status:

`FROZEN_FOR_BOUNDED_EXECUTION`

## 1. Accounting

Official correction-core accounting remains unchanged:

- accepted = `75 / 113`
- remaining = `38`
- W4 = `18 / NOT_CREDITED`

W4R is a rescope of the existing W4 weight 18, not a new correction-core denominator.

Internal W4R package weights:

- W4R-A = 5
- W4R-B = 4
- W4R-C = 4
- W4R-D = 5
- total = 18

These weights represent accepted lifecycle contribution, not time/token quotas.

No W4R package earns official correction-core credit until final W4 independent reviewer acceptance.

## 2. Dependency DAG

```text
W4R-A
Shared recovery fence + continuity current authority
        |
        +---------------------+
        |                     |
        v                     v
W4R-B                    W4R-C
Durable C07/C10          C13 direct reuse +
trusted evidence         recovery-root closure
        |                     |
        +----------+----------+
                   |
                   v
W4R-D
Trusted bundle + final atomic handoff + C15 integration
                   |
                   v
isolated PostgreSQL integration/concurrency
                   |
                   v
independent reviewer
                   |
                   v
W4 closure / credit 18
```

## 3. W4R-A

Responsibility:

- add `readiness_revision` to `AccountRecoveryControl`;
- add `ExecutionContinuityHead`;
- add append-only `ContinuityTransitionReceipt`;
- add controlled continuity-head transition/re-anchor repository semantics;
- add migration 0009 DDL for only these W4R-A objects plus reserved future tables only if explicitly authorized later — default: do not pre-create B/C/D tables;
- make C09-owned readiness-relevant writes participate in `readiness_revision` where exact semantics are already owned by C09;
- preserve `ingress_version` semantics;
- exact epoch identity, never substring/timestamp/lexical currentness.

Does not implement:

- C07 durable discovery receipt;
- C10 reconstruction receipt;
- trusted resolver;
- capability provider changes;
- C13 integration;
- recovery-root closure;
- final C15 READY path;
- account-authority/broker-action/C13/C14 global writer participation outside C09;
- actual PostgreSQL execution;
- A08;
- broker I/O.

Acceptance:

- stale trusted historical epoch can never be selected as current after head advance;
- EPOCH-1 never matches EPOCH-10;
- head transition CAS/idempotency/conflict semantics are explicit;
- historical SequenceGap remains append-only;
- `readiness_revision` is distinct from `ingress_version`;
- migration 0009 does not infer current head from historical epochs;
- all changed repository code remains caller-owned transaction/no commit;
- targeted + compatibility + full regression pass;
- one runtime commit then STOP reviewer.

## 4. W4R-B

Requires W4R-A accepted.

Responsibility:

- durable C07 discovery receipts;
- durable C10 positive reconstruction receipts;
- trusted immutable capability provider/fingerprint;
- exact expected snapshot and broker observation lookup;
- trusted evidence resolver core.

Weight: 4.

## 5. W4R-C

Requires W4R-A accepted.

Responsibility:

- direct C13 `unresolved(account)` + `blocking_case_state` reuse;
- semantic blocker witness;
- minimum recovery-root transitive closure;
- exact Fill/Event canonical identity/material closure.

Weight: 4.

## 6. W4R-D

Requires W4R-A/B/C accepted.

Responsibility:

- wire all readiness-relevant writers to the shared `readiness_revision` fence;
- build `TrustedReadinessEvidenceBundle`;
- final same-UoW trusted resolve/evaluate/handoff;
- remove/demote RF02 caller-authority shortcuts;
- final isolated PostgreSQL transaction/concurrency gate.

Weight: 5.

## 7. STOP / Reauthorization

STOP if any package requires:

- changing accepted C07 classification semantics;
- changing C10 economics;
- changing C13 blocking semantics;
- changing C14 formal-run semantics;
- repurposing `ingress_version`;
- modifying migrations 0001-0008;
- broker I/O;
- actual PostgreSQL/V07 without explicit verification authorization;
- production capability inference;
- P7 work;
- write scope outside package authorization.
