CREATE TABLE trading.broker_report_inbox (
    ingress_id TEXT PRIMARY KEY,
    broker TEXT NOT NULL,
    account_ref TEXT NOT NULL,
    generation BIGINT NOT NULL CHECK (generation >= 1),
    received_at TIMESTAMPTZ NOT NULL,
    report_type TEXT NOT NULL,
    payload_fingerprint TEXT NOT NULL,
    report_json JSONB NOT NULL
);

CREATE TABLE trading.broker_report_applications (
    application_id TEXT PRIMARY KEY,
    ingress_id TEXT NOT NULL REFERENCES trading.broker_report_inbox(ingress_id),
    generation BIGINT NOT NULL CHECK (generation >= 1),
    status TEXT NOT NULL CHECK (status IN ('APPLIED','DUPLICATE','CORROBORATED','DEFERRED','CONFLICT')),
    recorded_at TIMESTAMPTZ NOT NULL,
    evidence_json JSONB NOT NULL
);

CREATE TABLE trading.account_recovery_controls (
    broker TEXT NOT NULL,
    account_ref TEXT NOT NULL,
    generation BIGINT NOT NULL CHECK (generation >= 1),
    recovery_cut_revision BIGINT NOT NULL CHECK (recovery_cut_revision >= 0),
    ingress_version BIGINT NOT NULL CHECK (ingress_version >= 0),
    active BOOLEAN NOT NULL,
    recorded_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (broker, account_ref)
);

CREATE TABLE trading.execution_continuity_epochs (
    epoch_id TEXT PRIMARY KEY,
    broker TEXT NOT NULL,
    account_ref TEXT NOT NULL,
    generation BIGINT NOT NULL CHECK (generation >= 1),
    trusted_current BOOLEAN NOT NULL,
    historical_degradation BOOLEAN NOT NULL,
    anchored_at TIMESTAMPTZ NOT NULL,
    evidence_json JSONB NOT NULL
);

CREATE TABLE trading.broker_sequence_gaps (
    gap_id TEXT PRIMARY KEY,
    broker TEXT NOT NULL,
    account_ref TEXT NOT NULL,
    detected_at TIMESTAMPTZ NOT NULL,
    evidence TEXT NOT NULL
);

COMMENT ON TABLE trading.broker_report_inbox IS 'Broker report/callback 在 canonical application 前的 append-only durable ingress evidence；不推進 AccountStateHead。';
COMMENT ON COLUMN trading.broker_report_inbox.payload_fingerprint IS '同 ingress identity 的 material content 指紋；衝突時 fail closed。';
COMMENT ON TABLE trading.broker_report_applications IS 'Inbox evidence 的不可變 application/deferred/conflict 歷史。';
COMMENT ON COLUMN trading.broker_report_applications.status IS 'APPLIED、DUPLICATE、CORROBORATED、DEFERRED 或 CONFLICT；post-cut evidence 必須先 durable capture。';
COMMENT ON TABLE trading.account_recovery_controls IS '與 economic AccountStateHead 分離的 recovery generation 與 short fence control；不是完整 C12 RecoveryCut。';
COMMENT ON COLUMN trading.account_recovery_controls.recovery_cut_revision IS '短 fence 所參照的 AccountStateHead revision；revision 單獨不代表完整 RecoveryCut。';
COMMENT ON COLUMN trading.account_recovery_controls.ingress_version IS 'Final handoff conditional write 使用的 durable ingress frontier。';
COMMENT ON TABLE trading.execution_continuity_epochs IS 'Current-trust 與 historical degradation 分離的 append-only continuity evidence。';
COMMENT ON TABLE trading.broker_sequence_gaps IS '永不因 re-anchor 刪除或改寫的 historical SequenceGap evidence。';
