# GAP-08 Wave-3 — Reviewer Correction Authorization Amendment 02

## 1. Current State

Wave：

`GAP08-W3-BROKER-RECOVERY-EVIDENCE`

RF01 Authorization Baseline：

`45b9e55e5e5889dfdf5626341d2afa721ff0c0ca`

RF01 execution result：

`BLOCKED / REAUTHORIZATION REQUIRED`

Reason：

C09 final review discovered one additional semantic correction is required after RF01's previously authorized final C09 cycle was consumed。

C07：

`PASS / READ-ONLY`

C10 RF01 WIP：

`TARGETED_PASS / FULL_REGRESSION_PASS / FROZEN_PENDING_FINAL_REVIEW`

C09：

`HOLD / RF02_REQUIRED`

W3：

`HOLD / RF02_REQUIRED`

W3 weight：

15 / NOT CREDITED。

Accepted correction-core progress：

60 / 113。

Remaining：

53。

Runtime Source Modification Authorization：

`BOUNDED_AUTHORIZED_FOR_GAP08_W3_RF02_C09_ONLY`

Canonical Runtime Authorization：

`NOT_AUTHORIZED`

Production Activation：

`NOT_AUTHORIZED`

---

## 2. RF01 Execution Evidence Before STOP

Executor reported：

- C09 targeted：56 passed。
- C10 targeted：115 passed。
- full RF01 targeted：149 passed。
- full regression：1199 passed / 4 skipped。
- commit：NO。
- push：NO。
- HEAD / origin/master remained `45b9e55e5e5889dfdf5626341d2afa721ff0c0ca`。
- migration 0007 execution：NO。
- actual PostgreSQL / V07：NO。
- broker / paper / Shioaji simulation / production I/O：NO。
- protected/governance files：unchanged before this RF02 docs authorization。
- user-reported RF01 5HR quota observation：23%；observational only。

RF01 stopped before commit because C09 would require a second semantic correction。

---

## 3. Existing Uncommitted RF01 WIP Must Be Preserved

RF02 is intentionally authorized while the exact seven RF01 files remain modified and UNSTAGED。

Do NOT reset、checkout、restore、stash-drop、discard or reconstruct this WIP。

Exact RF01 WIP at authorization time：

- `persistence/broker_recovery.py`：`06b30e48120ec08c56c9dfd1ac06fa970057fa8b5e57caab8c6c150cbaa6f4ab`
- `persistence/postgres/broker_recovery.py`：`10d3c1bcd4226629d49a02eb4e5ee20005712a54fa5a67ced4e58e7cc36257b4`
- `persistence/postgres/migrations/0007_broker_recovery_evidence.sql`：`a3895e58f63fa946ff6fcd0b5a822458e288cba8728934d4064e689fbe5afabb`
- `tests/unit/test_c09_broker_recovery_fence.py`：`9c3be803abaec2bc25173ab0b68cb1376c3e23d76d9dbd2b72d0130dd7ac1df7`
- `tests/unit/test_c10_broker_reconstruction.py`：`e228602f0a3339aae3fe65a2dec185b88989cf0ec9a13077136e26998aff7bcc`
- `tests/unit/test_operational_postgres.py`：`0f71ea7ca7ea5fcc0859e702aeef4d36824b4eee9026a8fbe95cf74cb1c2f4cb`
- `trading/broker_recovery.py`：`e4aeacd78c49665ecea6c96b9a4a8bd1643ccef34f06650d7260bb82f8e917c8`

These hashes are evidence of the local WIP that existed BEFORE the RF02 governance commit。

The RF02 docs-only commit MUST NOT alter these bytes。

---

## 4. C10 WIP Freeze

C10 has already consumed its final RF01 semantic correction cycle。

No additional C10 semantic correction is authorized by RF02。

The following WIP files are byte-frozen during RF02：

- `tests/unit/test_c10_broker_reconstruction.py`：`e228602f0a3339aae3fe65a2dec185b88989cf0ec9a13077136e26998aff7bcc`
- `trading/broker_recovery.py`：`e4aeacd78c49665ecea6c96b9a4a8bd1643ccef34f06650d7260bb82f8e917c8`

RF02 executor MUST verify these SHA-256 values before and after C09 correction。

If either changes：

STOP / REAUTHORIZATION。

C10 final reviewer acceptance still waits for W3 reviewer verification after RF02；this freeze is not acceptance/closure。

---

## 5. RF02-C09 Defect A — Inactive Control Generation Semantics

Final RF01 review found the recovery ingress rule still needs this distinction：

### Active control

For an active recovery control：

- incoming entry generation MUST equal active generation。
- NEW ingress participates in the durable frontier and advances it exactly once。
- stale/wrong generation fails closed。

### Inactive control after handoff

For an inactive recovery control：

- wrong/stale generation MUST still fail closed。
- SAME generation post-handoff evidence MAY be durably captured。
- that evidence MUST NOT masquerade as active-recovery ingress。
- it MUST NOT reopen the recovery control。
- it MUST NOT silently advance an active-recovery frontier that no longer exists。
- it MUST remain durable evidence for later explicit handling/re-evaluation。
- it MUST NOT be lost merely because final handoff won the race。

No generation bypass。

No implicit new recovery session。

No AccountStateHead advancement from inbox capture。

---

## 6. RF02-C09 Defect B — Application Sequence Must Be Strictly Serialized

RF01 WIP introduced deterministic application sequence/current-disposition semantics but final review found a remaining race if monotonicity is derived from：

`MAX(application_sequence)` + unique constraint

without serializing writers on the same durable ingress authority。

Required：

1. all application appends for one ingress serialize on the SAME durable ingress row or an equivalent DB lock/key authority。
2. exact duplicate application identity is checked under that serialization boundary。
3. same application identity + identical material content is deterministic/idempotent。
4. same application identity + conflicting material content fails closed。
5. a NEW application sequence must be exactly prior authoritative sequence + 1。
6. concurrent appenders cannot both derive the same next sequence。
7. sequence gaps are rejected。
8. sequence regressions are rejected。
9. current disposition is derived from monotonic sequence authority，not timestamp。
10. final handoff reads authoritative current disposition consistently with this serialized order。
11. wrong-generation application remains unable to resolve active-generation ingress。
12. repository performs no independent commit/rollback。

Physical SQL may use `SELECT ... FOR UPDATE` on the durable inbox row or an equivalent PostgreSQL serialization primitive。

Do NOT use wall-clock ordering as causal authority。

---

## 7. Exact RF02 Write Scope

RF02 may MODIFY only these existing C09 files：

- `persistence/broker_recovery.py`
- `persistence/postgres/broker_recovery.py`
- `persistence/postgres/migrations/0007_broker_recovery_evidence.sql`
- `tests/unit/test_c09_broker_recovery_fence.py`
- `tests/unit/test_operational_postgres.py`

No new files。

The existing uncommitted C10 WIP files remain present but READ-ONLY：

- `trading/broker_recovery.py`
- `tests/unit/test_c10_broker_reconstruction.py`

Everything else READ-ONLY。

If RF02 requires a file outside the five C09 files：

STOP / REAUTHORIZATION。

---

## 8. Required RF02 Tests

Add/update tests proving at least：

1. active + same generation NEW ingress advances frontier once。
2. active + wrong generation rejects。
3. inactive + wrong generation rejects。
4. inactive + same generation NEW ingress is durably captured without reopening recovery。
5. inactive + same generation capture does not impersonate active frontier advancement。
6. exact duplicate ingress remains idempotent and does not advance frontier。
7. final-handoff-wins then same-generation later ingress remains durable evidence。
8. capture-wins still makes stale finalization fail。
9. application append serializes on one ingress durable authority。
10. first NEW application sequence is exact initial sequence。
11. each later NEW application sequence is previous + 1。
12. sequence gap rejects。
13. sequence regression rejects。
14. concurrent-next-sequence SQL is protected by durable row locking/equivalent serialization。
15. duplicate same application identity/content is idempotent。
16. duplicate application identity/conflicting content fails closed。
17. current disposition remains sequence-based and generation-scoped。
18. APPLIED -> later CONFLICT still blocks handoff。
19. DEFERRED -> later APPLIED may resolve only through the later authoritative sequence。
20. repository still performs no commit/rollback。
21. 0007 remains unexecuted and encodes the durable constraints needed by the chosen design。

C09 targeted：

    .\.venv\Scripts\python.exe -m pytest
        tests/unit/test_c09_broker_recovery_fence.py
        tests/unit/test_operational_postgres.py
        tests/unit/test_c04_account_authority_commit.py
        tests/unit/test_c06_broker_action_safety.py
        -q

Then C10 read-only regression：

    .\.venv\Scripts\python.exe -m pytest
        tests/unit/test_c10_broker_reconstruction.py
        tests/unit/test_operational_execution.py
        tests/unit/test_shioaji_mapping.py
        tests/unit/test_shioaji_submitted_status.py
        -q

Then full W3 reviewer-targeted regression：

    .\.venv\Scripts\python.exe -m pytest
        tests/unit/test_c07_broker_discovery.py
        tests/unit/test_c09_broker_recovery_fence.py
        tests/unit/test_c10_broker_reconstruction.py
        tests/unit/test_c04_account_authority_commit.py
        tests/unit/test_c06_broker_action_safety.py
        tests/unit/test_c08_broker_client_order_ref.py
        tests/unit/test_broker_capabilities.py
        tests/unit/test_shioaji_mapping.py
        tests/unit/test_shioaji_submitted_status.py
        tests/unit/test_operational_execution.py
        tests/unit/test_operational_postgres.py
        -q

Then：

    .\.venv\Scripts\python.exe -m pytest -q

Then：

    git diff --check

Then exact RF02 scope / C10 byte-freeze validation。

---

## 9. Semantic Correction Budget

C07：

0 / READ-ONLY。

C10：

0 additional / RF01 WIP byte-frozen。

C09：

RF02 grants exactly ONE additional final semantic correction cycle。

If RF02 implementation/final review discovers another C09 semantic correction is required：

STOP / REAUTHORIZATION。

Tooling retries remain finite and do not consume semantic budget。

---

## 10. Git / WIP Policy

The RF02 authorization commit is docs-only and is created while the seven runtime/test/migration WIP files remain unstaged。

After this authorization is committed/pushed：

- HEAD/origin/master will move to the RF02 authorization commit。
- the seven RF01 WIP files MUST remain locally modified and unstaged。
- CODEX continues from those exact local WIP bytes。
- do NOT reset to HEAD。
- do NOT checkout those seven files。
- do NOT reapply RF01 from scratch。

After RF02 correction passes all gates：

- one combined runtime correction commit may include the preserved RF01 WIP + RF02 C09 delta。
- commit only the exact seven WIP files。
- no governance docs in runtime commit。

Before push：

`git fetch origin master`

`origin/master` MUST equal the RF02 authorization commit。

No rebase / merge / force push / history rewrite。

---

## 11. Side-Effect Envelope

DENY：

- migration execution。
- actual PostgreSQL。
- V07。
- broker network。
- paper broker。
- Shioaji simulation / production。
- real callback registration。
- credential access。
- V01～V05 verification。
- production activation。
- C12/C13/C14/C15。
- next Wave。

---

## 12. Completion Boundary

After combined RF01+RF02 runtime correction commit/push：

STOP and return to reviewer。

DO NOT：

- mark W3 accepted/closed。
- credit weight 15。
- modify governance closure docs。
- execute migration 0007。
- start next Wave。

---

## 13. Current Governance

W3：

`HOLD / RF02_REQUIRED`

C07：

`PASS / READ-ONLY`

C09：

`RF02 REQUIRED`

C10：

`RF01 WIP FROZEN / NO ADDITIONAL SEMANTIC CHANGE`

Runtime Source Modification Authorization：

`BOUNDED_AUTHORIZED_FOR_GAP08_W3_RF02_C09_ONLY`

Canonical Runtime Authorization：

`NOT_AUTHORIZED`

Accepted correction-core：

60 / 113。

Remaining：

53。

W3 weight 15：

NOT CREDITED。