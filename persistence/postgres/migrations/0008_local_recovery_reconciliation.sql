ALTER TABLE trading.reconciliation_case_history
    ADD COLUMN broker TEXT,
    ADD COLUMN account_ref TEXT;

ALTER TABLE trading.reconciliation_case_history
    ADD CONSTRAINT reconciliation_case_scope_pair
    CHECK ((broker IS NULL) = (account_ref IS NULL));

CREATE INDEX reconciliation_case_account_latest_idx
    ON trading.reconciliation_case_history (broker, account_ref, case_id, version DESC);

CREATE FUNCTION trading.enforce_reconciliation_case_scope()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.broker IS NULL OR NEW.account_ref IS NULL THEN
        RAISE EXCEPTION 'new reconciliation case history requires explicit BrokerAccount scope';
    END IF;
    IF EXISTS (
        SELECT 1 FROM trading.reconciliation_case_history h
        WHERE h.case_id = NEW.case_id
          AND (h.broker, h.account_ref) IS DISTINCT FROM (NEW.broker, NEW.account_ref)
    ) THEN
        RAISE EXCEPTION 'reconciliation case account scope cannot change';
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER reconciliation_case_scope_guard
BEFORE INSERT ON trading.reconciliation_case_history
FOR EACH ROW EXECUTE FUNCTION trading.enforce_reconciliation_case_scope();

COMMENT ON COLUMN trading.reconciliation_case_history.broker IS 'ReconciliationCase 唯一主要 BrokerAccount scope 的 broker；既有 NULL 歷史不得猜測回填。';
COMMENT ON COLUMN trading.reconciliation_case_history.account_ref IS 'ReconciliationCase 唯一主要 BrokerAccount scope 的 account reference；跨版本不得漂移。';
COMMENT ON FUNCTION trading.enforce_reconciliation_case_scope() IS '拒絕新 unscoped case 與相同 case_id 的跨帳戶 scope drift；不修改經濟狀態。';

CREATE TABLE trading.reconciliation_runs (
    run_id TEXT PRIMARY KEY,
    broker TEXT NOT NULL,
    account_ref TEXT NOT NULL,
    established_at TIMESTAMPTZ NOT NULL,
    boundary_json JSONB NOT NULL
);

CREATE TABLE trading.reconciliation_run_outcomes (
    run_id TEXT PRIMARY KEY REFERENCES trading.reconciliation_runs(run_id),
    finalized_at TIMESTAMPTZ NOT NULL,
    technical_outcome TEXT NOT NULL CHECK (technical_outcome IN ('COMPLETED','EXTERNAL_STATE_UNKNOWN','FAILED')),
    input_qualification TEXT NOT NULL CHECK (input_qualification IN ('QUALIFIED','UNQUALIFIED')),
    outcome_json JSONB NOT NULL
);

CREATE INDEX reconciliation_runs_account_idx
    ON trading.reconciliation_runs (broker, account_ref, established_at, run_id);

COMMENT ON TABLE trading.reconciliation_runs IS 'Formal reconciliation evaluation 前先 durable 建立的 BrokerAccount-scoped evaluated-world boundary；不代表 READY。';
COMMENT ON COLUMN trading.reconciliation_runs.boundary_json IS '綁定 exact RecoveryCut、policy、authority refs 與外部 evidence qualification 的不可變 boundary。';
COMMENT ON TABLE trading.reconciliation_run_outcomes IS '每個 run 唯一 authoritative terminal audit；technical outcome、input qualification 與 domain results 同筆 crash-consistent 保存。';
COMMENT ON COLUMN trading.reconciliation_run_outcomes.outcome_json IS '完整 terminal results/provenance evidence；不得以 latest MATCH 作為 current READY authority。';
