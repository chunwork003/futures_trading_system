ALTER TABLE trading.account_recovery_controls
    ADD COLUMN readiness_revision BIGINT NOT NULL DEFAULT 0
    CHECK (readiness_revision >= 0);

COMMENT ON COLUMN trading.account_recovery_controls.readiness_revision IS
    '復原就緒證據的 currentness/CAS fence；不代表經濟狀態 revision 或 broker ingress 數量。';

CREATE TABLE trading.execution_continuity_heads (
    broker TEXT NOT NULL,
    account_ref TEXT NOT NULL,
    generation BIGINT NOT NULL CHECK (generation >= 1),
    current_epoch_id TEXT NOT NULL REFERENCES trading.execution_continuity_epochs(epoch_id),
    head_revision BIGINT NOT NULL CHECK (head_revision >= 1),
    readiness_revision BIGINT NOT NULL CHECK (readiness_revision >= 1),
    recorded_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (broker, account_ref)
);

COMMENT ON TABLE trading.execution_continuity_heads IS
    '每個 broker account 唯一 current continuity selector；epoch 本身的歷史旗標不得取代此 authority。';
COMMENT ON COLUMN trading.execution_continuity_heads.current_epoch_id IS
    '目前唯一被選定的 continuity epoch；不得以字串、時間或歷史 trusted 標記推論。';
COMMENT ON COLUMN trading.execution_continuity_heads.head_revision IS
    'current head 的單調 CAS revision，用於拒絕 stale 或 concurrent transition。';

CREATE TABLE trading.continuity_transition_receipts (
    transition_id TEXT PRIMARY KEY,
    broker TEXT NOT NULL,
    account_ref TEXT NOT NULL,
    generation BIGINT NOT NULL CHECK (generation >= 1),
    previous_epoch_id TEXT NULL,
    current_epoch_id TEXT NOT NULL REFERENCES trading.execution_continuity_epochs(epoch_id),
    previous_head_revision BIGINT NOT NULL CHECK (previous_head_revision >= 0),
    head_revision BIGINT NOT NULL CHECK (head_revision = previous_head_revision + 1),
    previous_readiness_revision BIGINT NOT NULL CHECK (previous_readiness_revision >= 0),
    readiness_revision BIGINT NOT NULL CHECK (readiness_revision = previous_readiness_revision + 1),
    recorded_at TIMESTAMPTZ NOT NULL,
    evidence_json JSONB NOT NULL CHECK (jsonb_typeof(evidence_json) = 'array'),
    receipt_json JSONB NOT NULL CHECK (jsonb_typeof(receipt_json) = 'object'),
    UNIQUE (broker, account_ref, head_revision)
);

COMMENT ON TABLE trading.continuity_transition_receipts IS
    'Append-only continuity current-head transition 證據；revision 鏈是 causal ordering authority。';
COMMENT ON COLUMN trading.continuity_transition_receipts.transition_id IS
    '穩定 transition identity；相同 identity 的不同 material content 必須 fail closed。';
COMMENT ON COLUMN trading.continuity_transition_receipts.previous_head_revision IS
    'transition 接受前的 exact continuity head revision。';
COMMENT ON COLUMN trading.continuity_transition_receipts.previous_readiness_revision IS
    'transition 接受前的 exact account readiness fence。';
