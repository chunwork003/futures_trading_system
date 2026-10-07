# MANUAL CODEX HANDOFF — WO-AUTO-IMP-002-REV2-01

READY_FOR_MANUAL_CODEX_TRIGGER; WORK does not invoke CODEX.

Read fresh origin/master CURRENT first. Exact handoff: `automation/runs/EXEC-AUTO-IMP-002-REV2-20261007T032957Z/handoff.yaml`. Exact execution: `EXEC-AUTO-IMP-002-REV2-20261007T032957Z`; authorization `AUTH-AUTO-IMP-002-REV2-01` CONSUMED single-use; source baseline `b56494966f33c47ea7744c5c1fed271ad01b39f1`; control-plane head before handoff `796bd1f4c529786e7612d5a1e7a20dc4bafc0641`. Resolve this handoff's containing commit and freshly revalidate any descendants; no source/scope/authority drift.

Lifecycle commits:
- owner_decision: `c5b0e2b0238b131398c9541b1cc3c448960b2341`
- authorization: `d9808efec1c2b48e94d295d9d76e28b16ace1f2b`
- eligibility: `ddbe34c9e76a0f9704c86604726c7db6e52324b0`
- writer_acquisition: `9cd0366fd5e38a7605cfd2d1091a1bcc07860419`
- execution_allocation: `4e2465688e92ff3ab82be6b5208b1453bc316074`
- reservation: `838981dec6c9e3f91c2432099386a114c5b6575f`
- reserved: `24314d88713c958ec6097d8f8c8a3aa242c40419`
- pre_dispatch_recheck: `5ee442fa0d03fcd006160c0103103d4ef3bd32e0`
- dispatch: `3889f5d7fbd2b9cfcccd3f588aca27cb8baaba67`
- consumed: `796bd1f4c529786e7612d5a1e7a20dc4bafc0641`

Scope digest `bb1c8b8600dc6d37cd6e72cedd263f206898a773b73c8127744c9c4a5b07a2c7`. Write ONLY:
- `automation/engine/repository_snapshot.py`
- `automation/engine/yaml_io.py`
- `tests/automation/test_contracts.py`
- `tests/automation/test_repository_snapshot.py`

Plan/interfaces/criteria/test matrix: `automation/work_orders/planning/AUTO-IMP-002-REV2.compilation.json`. Current WO: `automation/work_orders/WO-AUTO-IMP-002-REV2-01.yaml`; package: `automation/packages/AUTO-IMP-002.v2.yaml`; forecast: `automation/work_orders/forecasts/WO-AUTO-IMP-002-REV2-01.json` (1.8M/3.5M/6M LOW_PROVISIONAL). Pre-dispatch proof: `automation/runs/EXEC-AUTO-IMP-002-REV2-20261007T032957Z/pre_dispatch_recheck.json`.

Fresh first invocation sequence:
1. Fetch origin/master; prove exact authority RESERVATION/DISPATCH/CONSUMED/HELD writer and SOURCE preimages. Provider actual denial wins; Capacity2.2 PRIMARY_5H versus P75, weekly advisory.
2. Require exact execution branch absent for FIRST claim; never claim another execution or redispatch consumed authority. Branch from freshly proven compatible master, preserving all current control-plane evidence.
3. Publish your own contemporaneous `automation/runs/EXEC-AUTO-IMP-002-REV2-20261007T032957Z/claim.json` and `automation/runs/EXEC-AUTO-IMP-002-REV2-20261007T032957Z/invocation.json` BEFORE source writes, recording actual session, UTC, fresh execution-start SHA, branch, writer, Owner/auth/scope and gates. Do not backfill or mutate consumed history. Missing/contradictory evidence STOP_TO_WORK.
4. Implement only fresh Manifest Integrity and Unified Re-entry Snapshot Resolver: new cohesive snapshot module, safe YAML bytes API, two exact tests; reuse accepted orchestration.resolve_route. No routing/queue/capacity/authority/lifecycle redesign, no historical source assembly.
5. Initial implementation1; bounded in-scope implementation corrections2. Expected pre-fix failure or retry without semantic delta does not consume correction budget. Conditional review-fix2 is NOT executable now and cannot be repurposed. Scope/architecture/authority/side-effect expansion or budget exhaustion STOP_TO_OWNER.
6. Minimum contract/counterexample cases, impacted subset until clean, one targeted/cross-targeted/full after PASS:
```
python -m pytest -p no:cacheprovider tests/automation/test_repository_snapshot.py tests/automation/test_contracts.py -q
python -m pytest -p no:cacheprovider tests/automation/test_repository_snapshot.py tests/automation/test_contracts.py tests/automation/test_orchestration.py tests/automation/test_execution_capacity.py -q
python -m pytest -p no:cacheprovider -q
git diff --check
```
Verify exact four-file semantic delta and every protected path against your fresh execution-start SHA. No actual DB/broker/credentials/LIVE environments.
7. Publish own completion.json/execution_cost_actual.json, exact UTC/session/test/diff/scope/budget/provider evidence and task/context profile. Local exact tokens only from later deterministic WORK extraction; PENDING_EXTERNAL_EXTRACTION/UNKNOWN if unavailable. Cached input subset input, reasoning subset output; provider percentage proxy != exact tokens/billing.
8. STOP at COMPLETED_PENDING_REVIEW. Writer remains held pending WORK durable intake. No merge/accept/controller activation/next-package dispatch.

Controller NOT_ACTIVE; CONTROLLED_AUTO DISABLED; AUTO-IMP-003 NOT_AUTHORIZED; all unsafe side effects DENIED. NEXT: user manually triggers CODEX first invocation.
