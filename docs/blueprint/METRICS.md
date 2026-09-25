# Blueprint Metrics

## Status

AUTHORITATIVE
Blueprint-based official progress：

ENABLED。

Formal baseline：

- Engineering leaves：603。
- Total weight：2137。
- Lifecycle-weighted completion：43.46%。
- Architecture Design Coverage：87.23%。
- Design Freeze Coverage：51.47%。
- Runtime Implementation：38.84%。
- Unit Verification：35.61%。
- Integration Verification：35.52%。
- Accepted Capability：35.52%。
- Operational Readiness：NOT_READY。
- Production Live Readiness：BLOCKED。
- LIVE_AUTO：NOT_AUTHORIZED。

Lifecycle inventory：

- NOT_DESIGNED：62 leaves / weight 273。
- DESIGNED：201 leaves / weight 764。
- DESIGN_FROZEN：66 leaves / weight 270。
- IMPLEMENTED：27 leaves / weight 69。
- UNIT_VERIFIED：1 leaf / weight 2。
- INTEGRATION_VERIFIED：0 leaves / weight 0。
- ACCEPTED：246 leaves / weight 759。

Latest accepted runtime commit：`4049f982474454556baf8734a5729ecbedc7a438`。

---

## 1. Lifecycle Coefficients

| Lifecycle | Coefficient |
|---|---:|
| NOT_DESIGNED | 0.00 |
| DESIGNED | 0.10 |
| DESIGN_FROZEN | 0.20 |
| IMPLEMENTED | 0.55 |
| UNIT_VERIFIED | 0.70 |
| INTEGRATION_VERIFIED | 0.85 |
| ACCEPTED | 1.00 |
| DEFERRED | excluded |
| DEPRECATED | excluded from active denominator |

---

## 2. Weight

Allowed：

    1
    2
    3
    4
    5

Formula：

    Leaf Contribution
    =
    Weight × Lifecycle Coefficient

Domain completion：

    Sum(Leaf Contribution)
    ----------------------
    Sum(Active Leaf Weight)

V1 completion：

同樣公式跨所有 V1 leaves。

---

## 3. Independent Metrics

不得只顯示一個百分比。

至少分開：

### Architecture Design Coverage

有完整 blueprint design 的 active leaf / total active leaf。

### Design Freeze Coverage

DESIGN_FROZEN 以上。

### Runtime Implementation

IMPLEMENTED 以上。

### Unit Verification

UNIT_VERIFIED 以上。

### Integration Verification

INTEGRATION_VERIFIED 以上。

### Accepted Capability

ACCEPTED。

### Operational Readiness

有 operational integration / recovery / observability 等 gate 的能力。

### Production Live Readiness

只對 live-required capability 計算。

---

## 4. Production Safety

Safety state：

    NOT_APPLICABLE
    NOT_VERIFIED
    SIMULATION_VERIFIED
    PAPER_VERIFIED
    PRODUCTION_VERIFIED

Live-related leaf 必須另外標：

    LIVE_BLOCKER = YES / NO

Implementation 100%：

不等同 Production Live Ready。

---

## 5. Progress Integrity Rules

不得用：

- LOC。
- file count。
- test count。
- commit count。

直接當完成百分比。

Test count：

只作 verification evidence。

Blueprint score：

必須基於 accepted leaf inventory + weight + lifecycle。

---

## 6. Blueprint Activation Gate

正式啟用 Blueprint authoritative baseline 前：

- A～O leaves 建立。
- 92/92 capability mapping PASS。
- weight review PASS。
- no orphan PASS。
- no duplicate owner PASS。
- architecture consistency PASS。
- baseline commit completed。

切換時：

必須在 DEVELOPMENT_LOG 記錄 old / new estimate 與差異原因。
