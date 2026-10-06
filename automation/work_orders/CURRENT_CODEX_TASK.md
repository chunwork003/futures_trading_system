# WO-AUTO-GOV-PROGRAM-1_2-ORCH-01 — NOT EXECUTABLE

Current route: WAIT_5H_CAPACITY.
Architecture 1.2.2 / Capacity Policy 2.2 ACTIVE; AUTH-AUTO-GOV-PROGRAM-1_2-ORCH-01-REV4 AUTHORIZED / NOT_CONSUMED.
Latest observed PRIMARY_5H used=88%, safe capacity=5,588,889 tokens < MANUAL P75=7,000,000. Weekly statistical execution gate=false; P90=12,000,000 advisory for MANUAL.
No writer, execution ID, reservation, dispatch, invocation. handoff_ready=false. Do not invoke CODEX from this pointer.
Next legal action: WAKE -> fresh origin/master and provider/PRIMARY_5H revalidation; only after all gates PASS materialize normal single-use lifecycle and READY_FOR_MANUAL_CODEX_TRIGGER. No automatic CODEX.
Implementation correction budget=2; separate bounded review-fix budget=2. Exact 21-file scope, no architecture/authority/side-effect expansion. CONTROLLED_AUTO DISABLED.
Canonical exact pointers: CURRENT_CODEX.yaml, referenced WO/auth/forecast/eligibility/provider/rolling artifacts. AUTO-IMP-003 NOT_AUTHORIZED; runtime/broker/DB/migration/LIVE/production DENIED.
