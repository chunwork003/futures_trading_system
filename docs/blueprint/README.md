# Blueprint Specification

## 1. Status

AUTHORITATIVE
本文件定義 V1 Engineering Blueprint 的格式與治理規則。

---

## 2. ID Scheme

Domain：

    A ... O

Capability Group：

    X100
    X200
    ...

Engineering Leaf：

    X110
    X120
    ...

Example：

    J400 Broker Actual Position
    J410 BrokerPositionProvider
    J420 BrokerPositionSnapshot

ID 一旦被正式 baseline 接受：

不得為了排序美觀任意重編。

若 leaf deprecated：

保留 ID 並標記 DEPRECATED。

---

## 3. Required Leaf Fields

每一個 engineering leaf 最少必須能回答：

### Identity

- ID。
- Name。
- Domain。
- Capability Group。

### Goal

- Purpose。
- V1 user/system value。

### Ownership

- Canonical owner。
- Current path。
- Target path。

### Connection

- Upstream。
- Downstream。
- Inputs。
- Outputs。

### Authority

- Data/state authority。
- Not-authority-for。

### Semantics

- State semantics。
- Identity/key。
- Time/timezone。
- Numeric/precision。
- Error/ambiguity behavior。
- Invariants。

### External Reference

- Source IDs。
- source verification requirement。
- change risk。

### Migration

- CURRENT。
- TARGET。
- MIGRATION。
- compatibility boundary。

### Verification

- tests。
- acceptance。
- LIVE blocker。
- safety gate。

### Planning

- GAP。
- Work Package。
- lifecycle。
- weight。

---

## 4. Lifecycle

Allowed engineering lifecycle：

    NOT_DESIGNED
    DESIGNED
    DESIGN_FROZEN
    IMPLEMENTED
    UNIT_VERIFIED
    INTEGRATION_VERIFIED
    ACCEPTED
    DEFERRED
    DEPRECATED

不得用 file count 或 LOC 判斷 lifecycle。

---

## 5. Weight

Engineering weight：

    1 = trivial / local
    2 = small
    3 = medium
    4 = large / cross-module
    5 = safety-critical / high-integration

Weight：

衡量工程量與驗證成本。

不是 business priority。

不是 risk priority。

---

## 6. Status Dimensions

每個 leaf 分開記錄：

- Design Lifecycle。
- Runtime Lifecycle。
- Verification Lifecycle。
- Production Safety。

不得把：

`implemented`

等同：

`production ready`。

---

## 7. Source Authority

Source tiers：

    S0 = regulator / exchange authority
    S1 = official vendor / framework documentation
    S2 = official source code / repository
    S3 = internal ADR / architecture decision
    S4 = secondary reference

Broker / exchange / money semantics：

優先 S0 / S1。

S4：

不得單獨作為 live-money semantics 依據。

若官方來源不足：

HARD_BLOCK 或 REVIEW。

不得猜測。

---

## 8. Code Documentation Contract

重要 module / class / public function / public contract：

繁體中文 comment / docstring / XML comment 至少說明需要的部分：

- 用途。
- 責任。
- upstream / 資料來源。
- downstream / 使用者。
- 重要 invariant。
- 非顯而易見 business rule。
- 外部 source ID（若 semantics 依賴外部規格）。
- 不負責什麼。

禁止：

只把函式名稱翻譯成中文作為無價值註解。

---

## 9. Database Documentation Contract

Future PostgreSQL：

重要 TABLE / COLUMN / FUNCTION：

使用繁體中文 COMMENT。

至少說明：

- purpose。
- authority。
- units。
- timezone。
- nullable semantics。
- expected/actual distinction。
- lifecycle / event semantics。

---

## 10. Work Package Contract

Blueprint baseline 啟用後：

ACTIVE 必須包含：

### Blueprint Scope

    Implements:
    Touches:
    Does Not Implement:

### Source Requirements

    Source IDs:
    Last Verified:
    Revalidation Required:

### Design Freeze

不能交由 Codex 決定：

- canonical ownership。
- business semantics。
- broker semantics。
- state authority。
- identity。
- persistence authority。
- public contracts。
- live safety。

---

## 11. Migration Rule

CURRENT != TARGET 時：

必須明確記錄 MIGRATION。

不得看到 Target path 就直接 mass-move。

Compatibility-first。

每次只 migration 一個 bounded consumer slice。

---

## 12. Blueprint Activation Gate

Blueprint 轉成 AUTHORITATIVE 前必須：

1. A～O file 全部存在。
2. A～O group 全部定義。
3. engineering leaves 全部有 ID。
4. 92/92 capability blocks 有 mapping。
5. CONNECTION_MATRIX complete。
6. STATE_AUTHORITY complete。
7. SOURCE_REGISTRY initial baseline complete。
8. TRACEABILITY mapping complete。
9. METRICS baseline complete。
10. 0 orphan capability。
11. 0 duplicate canonical owner conflict。
12. architecture consistency audit PASS。
13. commit / push。
