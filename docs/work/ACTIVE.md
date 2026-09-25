# ACTIVE WORK PACKAGE

## 1. Work Package ID

GAP-BROKER-002

---

## 2. Title

Broker Capability Matrix / Mapping Semantics

---

## 3. Status

COMPLETED / ACCEPTED

Architecture / Source Review：

COMPLETED。

Architecture / Design Freeze：

COMPLETED for I120 / I130 / I140 / I940。

Runtime execution authorization：

COMPLETED。

Launch Gate：

`CONSUMED`

Architecture freeze commit：

`b5c0a1c3af50e0a2d31261b81eb1630380d496d9`

Runtime gate release commit：

`767b1e3e22a1ab1baeebefa0c0731008503f23aa`

Accepted runtime commit：

`7d7fdabcb99da59d3d23ccec62b11c6572ceea82`


## 4. Recommended Model

GPT-5.6 Sol

Effort：

輕度

Execution Mode：

LEVEL_3A_BOUNDED

Model / effort不得中途切換。

Level 3B remains NOT_ENABLED。

---

## 5. Goal

建立 broker-neutral capability evidence contract 與 Sinopac documentation-backed capability matrix。

Capability matrix 只描述已知支援與 verification evidence；不執行 broker action，也不授權 LIVE。

---

## 6. Why This Is Next

GAP-BROKER-001 與 GAP-RECON-001 已 CLOSED / ACCEPTED。

Broker capability matrix 是 persistence/live phases 前的 explicit integration-safety boundary。

---

## 7. Baseline

Branch：master

Expected architecture baseline ancestor：

    457dc054641551f04dea5e6b1eda80f042a07c64

Recorded full regression：

    847 passed

Known warning：

    GAP-ENV-001 / PytestCacheWarning

Known untracked：

    data/

不得修改、刪除、stage data/。

---

## 8. Source Freeze

Last verified：2026-09-25

Current reviewed upstream release：Shioaji 1.7.6

Required Source IDs：

    SRC-SINOPAC-LOGIN-001
    SRC-SINOPAC-FUT-ORDER-001
    SRC-SINOPAC-POSITION-001
    SRC-SINOPAC-SIMULATION-001
    SRC-SINOPAC-ORDER-STATUS-001
    SRC-SINOPAC-ORDER-EVENT-001
    SRC-SINOPAC-RELEASE-001
    SRC-PYDANTIC-001
    SRC-ADR-001
    SRC-ARCH-001
    SRC-BLUEPRINT-001

Runtime executor不得自行重新定義 broker semantics。

Source conflict -> HARD_BLOCK。

---

## 9. Canonical Ownership

Broker-neutral capability contracts：

    adapters/capabilities.py

Sinopac evidence matrix：

    adapters/sinopac/capabilities.py

No parallel model elsewhere。

---

## 10. BrokerCapability

Exact values：

    ACCOUNT_QUERY
    POSITION_QUERY
    ORDER_PLACE
    ORDER_UPDATE
    ORDER_CANCEL
    ORDER_STATUS
    TRADE_LIST
    ORDER_DEAL_EVENT

---

## 11. BrokerCapabilitySupport

Exact values：

    SUPPORTED
    UNSUPPORTED
    UNKNOWN

---

## 12. BrokerVerificationMode

Exact values：

    DOCUMENTATION
    FAKE
    SIMULATION
    PRODUCTION

No implicit hierarchy。

DOCUMENTATION != SIMULATION != PRODUCTION。

---

## 13. BrokerCapabilityEvidence

Immutable Pydantic model：

    capability: BrokerCapability
    support: BrokerCapabilitySupport
    source_ids: tuple[str, ...]
    verification_modes: tuple[BrokerVerificationMode, ...]
    sdk_version: str | None
    verified_on: date
    note: str | None = None

Rules：

- frozen / extra forbid。
- source IDs trim/nonblank/no duplicates。
- verification modes no duplicates；normalize to enum order。
- sdk_version optional but nonblank after trim。
- note optional but nonblank after trim。
- SUPPORTED / UNSUPPORTED requires source evidence。
- UNKNOWN cannot claim verification mode。
- no hidden current date。

---

## 14. BrokerCapabilityMatrix

Immutable：

    broker: str
    entries: tuple[BrokerCapabilityEvidence, ...]

Rules：

- broker uppercase/trim/nonblank。
- duplicate capability rejected。
- deterministic enum-order entries。
- evidence only；not execution authority。

---

## 15. Failure Contract

Explicit：

    BrokerCapabilityUnavailableError(RuntimeError)

Public pure functions：

    get_broker_capability(matrix, capability)

    require_broker_capability(
        matrix,
        capability,
        *,
        required_mode=None
    )

require must reject：

- missing entry。
- UNSUPPORTED。
- UNKNOWN。
- requested verification mode absent。

No fallback。

---

## 16. SINOPAC_CAPABILITY_MATRIX

Exact broker：

    SINOPAC

Initial source-reviewed evidence：

    sdk_version = 1.7.6
    verified_on = 2026-09-25
    verification_modes = (DOCUMENTATION,)

Supported capability source mapping：

- ACCOUNT_QUERY -> SRC-SINOPAC-LOGIN-001。
- POSITION_QUERY -> SRC-SINOPAC-POSITION-001。
- ORDER_PLACE / ORDER_UPDATE / ORDER_CANCEL -> SRC-SINOPAC-FUT-ORDER-001。
- ORDER_STATUS / TRADE_LIST -> SRC-SINOPAC-ORDER-STATUS-001。
- ORDER_DEAL_EVENT -> SRC-SINOPAC-ORDER-EVENT-001 + SRC-SINOPAC-RELEASE-001。

Initial concrete matrix MUST NOT contain SIMULATION or PRODUCTION verification modes。

Official simulation documentation is source context only；not an executed verification run。

---

## 17. Scope Freeze

Implements only：

    I120
    I130
    I140
    I940

Touches：

    I110
    I210-I660
    I830
    I910

Does Not Implement：

    I720
    I730
    I740
    I820
    I920
    I930

Also not implemented：

- login / logout。
- CA activation。
- reconnect logic。
- live account-selection orchestration。
- real broker network call。
- actual simulation verification。
- production verification。
- adapter relocation。
- execution mapping changes。

---

## 18. Allowed Runtime Files

Primary：

    adapters/capabilities.py
    adapters/sinopac/capabilities.py

Tests：

    tests/unit/test_broker_capabilities.py

Only if export compatibility requires：

    adapters/__init__.py
    adapters/sinopac/__init__.py

No other runtime files without direct dependency evidence。

---

## 19. Forbidden

    data/**
    database/**
    trading/**
    backtest/**
    strategy/**
    strategies/**
    features/**

Do not modify existing Shioaji execution/mapping runtime。

No credentials。

No broker login。

No network tests。

---

## 20. Required Tests

At minimum：

1. BrokerCapability exact values。
2. BrokerCapabilitySupport exact values。
3. BrokerVerificationMode exact values。
4. evidence immutable / extra-forbid。
5. source_ids trim/nonblank。
6. duplicate source_ids reject。
7. verification mode duplicate reject。
8. verification modes canonical ordering。
9. sdk_version trim/nonblank。
10. note trim/nonblank。
11. SUPPORTED requires source evidence。
12. UNSUPPORTED requires source evidence。
13. UNKNOWN cannot claim verification modes。
14. matrix broker normalization。
15. duplicate capability reject。
16. deterministic entry ordering。
17. get known capability。
18. get missing capability -> None。
19. require supported capability PASS。
20. require missing capability explicit failure。
21. require UNSUPPORTED explicit failure。
22. require UNKNOWN explicit failure。
23. require absent requested mode explicit failure。
24. DOCUMENTATION does not satisfy SIMULATION。
25. SIMULATION does not satisfy PRODUCTION。
26. concrete matrix broker = SINOPAC。
27. concrete matrix exact eight capabilities。
28. concrete matrix sdk_version = 1.7.6。
29. concrete matrix verified_on = 2026-09-25。
30. concrete matrix source mappings correct。
31. concrete matrix only DOCUMENTATION mode。
32. no SIMULATION claim。
33. no PRODUCTION claim。
34. no network / credential / broker action surface。
35. existing account mapping compatibility。
36. existing Shioaji mapping/submission compatibility。
37. full regression。

---

## 21. Compatibility Tests

At least：

    tests/unit/test_trading_account.py
    tests/unit/test_trading_execution.py
    tests/unit/test_shioaji_mapping.py
    tests/unit/test_shioaji_submission.py
    tests/unit/test_shioaji_broker.py

Then full regression。

---

## 22. Acceptance

PASS requires：

- exact frozen contracts implemented。
- initial SINOPAC matrix documentation-only。
- unsupported/unverified explicit failure。
- no live authorization implication。
- no existing execution behavior modified。
- targeted PASS。
- compatibility PASS。
- full regression PASS。
- git diff --check PASS。
- data/ untouched。

---

## 23. Stop Conditions

HARD_BLOCK if：

- official source conflicts with frozen semantics。
- implementation requires login/network/CA。
- implementation requires existing execution adapter changes。
- public capability IDs need redesign。
- simulation/production evidence cannot be distinguished。
- unrelated core regression。
- data/ modified。
- secret exposure。

---

## 24. Git

After gate release：

    precheck
    -> implementation
    -> targeted
    -> compatibility
    -> full regression
    -> git diff --check
    -> exact scope
    -> stage
    -> commit
    -> push
    -> remote verify
    -> final report
    -> STOP

Runtime commit message：

    feat(adapters): add broker capability matrix

No amend / rebase public history / force push / reset --hard。

---

## 24A. Runtime Completion Evidence

Result：

PASS / ACCEPTED。

Runtime commit：

`7d7fdabcb99da59d3d23ccec62b11c6572ceea82`

Runtime files：

- adapters/capabilities.py。
- adapters/sinopac/capabilities.py。
- tests/unit/test_broker_capabilities.py。

Verification：

- targeted：22 passed。
- compatibility：45 passed。
- full regression：869 passed。
- git diff --check：PASS。
- implementation correction cycles：0。
- final status：only `?? data/`。

Calibration：

- formal Level 3A sample：5。
- GPT-5.6 Sol / 輕度。
- user-observed 5HR usage：10%。
- files read：12。
- files created：3。
- existing files modified：0。
- tool operations：17。
- command/tool retries：2。
- wall time：約 3m44s。
- token/context：unavailable。
- five-sample 5HR average：12.60%。

Closure：

- GAP-BROKER-002 CLOSED / ACCEPTED。
- capability evidence remains non-authoritative for LIVE。
- SIMULATION / PRODUCTION evidence still deferred。
- GAP-08 not runtime-authorized。

---

## 25. Documentation Responsibility

Runtime Codex only：implementation / tests / debug / runtime commit / push / report。

Deterministic acceptance remains manual。

完成後 STOP。

Do not start GAP-08。

Do not enable Level 3B。

---

## 26. Re-entry Precheck Scope

Default：

    AGENTS.md
    docs/work/ACTIVE.md
    adapters/__init__.py
    adapters/sinopac/__init__.py
    adapters/sinopac/account_mapping.py

Compatibility-only reads：

    backtest/shioaji_mapping.py
    backtest/shioaji_broker.py
    relevant listed tests

No whole-repo rescan。

---

## 27. Architect / Codex Responsibility Freeze

Architect frozen：

- canonical ownership。
- public capability IDs。
- support enum。
- verification-mode enum。
- evidence fields / invariants。
- matrix fields / uniqueness。
- explicit error semantics。
- query / require functions。
- Sinopac source mappings。
- initial evidence version/date/mode。
- deferred live/session scope。

Codex only decides private helpers、fixture layout、local implementation detail。

Public semantic change -> STOP + LEVEL 3。

---

## 28. Runtime Launch Gate

Current：

    CONSUMED

Release requires：

1. this architecture freeze + complete ACTIVE committed。
2. push verified。
3. local master == origin/master。
4. working tree only known data/。

Release authorizes only GAP-BROKER-002。
