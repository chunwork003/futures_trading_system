# AUTO-IMP-001 QRF01 Bounded Review Fix

```text
RF_ID = AUTO-IMP-001-QRF01
SOURCE_HEAD = d34fdfb969e830c227300b5229ba07c1c478ed7f
REVIEW_RESULT = REVIEW_FIX_REQUIRED
NEW_MASTER_ARCHITECTURE_CONTRADICTION = NO
ARCHITECTURE_ESCALATION_REQUIRED = NO
STATUS = REVIEW_FIX_APPLIED_PENDING_RE_REVIEW
```

Only three semantics are corrected:

1. `RESERVE_ARITHMETIC`
   - 80% remaining is the sole admission floor.
   - control-plane and recovery reserve intent are embedded.
   - no additional reserve subtraction.

2. `APPLICABLE_WINDOW_FAIL_CLOSED`
   - `APPLICABLE`, `NOT_APPLICABLE_WITH_POSITIVE_PROOF`, `UNKNOWN`.
   - UI absence never proves non-applicability.
   - applicable-without-evidence and unknown both require recheck.

3. `RESERVATION_BOUND_FRESHNESS`
   - evidence belongs to the current eligibility/reservation attempt.
   - 10 minutes is a hard TTL only.
   - intervening quota-affecting events invalidate evidence.

Unchanged:

- active QuotaAdmissionPolicyV1 v1.0 remains FROZEN;
- v1.1 candidate remains inactive;
- AUTO-IMP-001 remains AUTHORIZED;
- execution eligibility remains BLOCKED_POLICY_REVIEW;
- CODEX remains NOT_STARTED;
- Runtime/Broker/Migration/LIVE/Production remain unauthorized.

Next route:

`AUTOMATION_QUOTA_NORMALIZED_FALLBACK_RF_RE_REVIEW`
