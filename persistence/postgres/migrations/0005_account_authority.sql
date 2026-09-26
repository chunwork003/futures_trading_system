CREATE TABLE trading.account_state_heads (
    broker TEXT NOT NULL,
    account_ref TEXT NOT NULL,
    current_revision BIGINT NOT NULL CHECK (current_revision >= 0),
    initialized BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (broker, account_ref),
    CHECK ((initialized AND current_revision >= 1) OR (NOT initialized AND current_revision = 0))
);

CREATE TABLE trading.account_recovery_checkpoints (
    broker TEXT NOT NULL,
    account_ref TEXT NOT NULL,
    account_revision BIGINT NOT NULL CHECK (account_revision >= 1),
    expected_snapshot_id TEXT NOT NULL REFERENCES trading.expected_position_snapshots(snapshot_id),
    authority_commit_id TEXT NOT NULL,
    recorded_at TIMESTAMPTZ NOT NULL,
    checkpoint_json JSONB NOT NULL,
    PRIMARY KEY (broker, account_ref, account_revision),
    UNIQUE (authority_commit_id)
);

CREATE TABLE trading.account_authority_commit_receipts (
    authority_commit_id TEXT PRIMARY KEY,
    mutation_fingerprint TEXT NOT NULL,
    broker TEXT NOT NULL,
    account_ref TEXT NOT NULL,
    committed_revision BIGINT NOT NULL CHECK (committed_revision >= 1),
    expected_snapshot_id TEXT NOT NULL REFERENCES trading.expected_position_snapshots(snapshot_id),
    recorded_at TIMESTAMPTZ NOT NULL,
    receipt_json JSONB NOT NULL,
    UNIQUE (broker, account_ref, committed_revision),
    FOREIGN KEY (broker, account_ref, committed_revision)
        REFERENCES trading.account_recovery_checkpoints(broker, account_ref, account_revision)
);

COMMENT ON TABLE trading.account_state_heads IS '每個 BrokerAccount 的連續 material authority revision frontier，不代表 READY。';
COMMENT ON COLUMN trading.account_state_heads.current_revision IS '已成功提交的最新 account authority revision；rev0 僅為未初始化控制狀態。';
COMMENT ON COLUMN trading.account_state_heads.initialized IS '正向證明 EXPECTED_STATE_INITIALIZED 已完成，不可由 snapshot 缺失推斷。';
COMMENT ON TABLE trading.account_recovery_checkpoints IS '每個 material revision 唯一且 exact-reference expected snapshot 的 recovery checkpoint。';
COMMENT ON COLUMN trading.account_recovery_checkpoints.expected_snapshot_id IS '該 revision 的 exact expected-state snapshot，禁止 latest fallback。';
COMMENT ON TABLE trading.account_authority_commit_receipts IS '可重現的 account authority commit idempotency receipt。';
COMMENT ON COLUMN trading.account_authority_commit_receipts.mutation_fingerprint IS '決定性 canonical mutation fingerprint，用於區分相同 retry 與衝突。';
