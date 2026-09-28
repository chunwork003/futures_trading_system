ALTER TABLE trading.account_recovery_controls
    ADD COLUMN readiness_revision BIGINT NOT NULL DEFAULT 0
    CHECK (readiness_revision >= 0);

COMMENT ON COLUMN trading.account_recovery_controls.readiness_revision IS
    '復原就緒證據的 currentness/CAS fence；不代表經濟狀態 revision 或 broker ingress 數量。';

ALTER TABLE trading.execution_continuity_epochs
    ADD CONSTRAINT execution_continuity_epochs_scope_identity_uq
    UNIQUE (broker, account_ref, generation, epoch_id);

CREATE TABLE trading.execution_continuity_heads (
    broker TEXT NOT NULL,
    account_ref TEXT NOT NULL,
    generation BIGINT NOT NULL CHECK (generation >= 1),
    current_epoch_id TEXT NOT NULL,
    transition_receipt_id TEXT NOT NULL,
    head_revision BIGINT NOT NULL CHECK (head_revision >= 1),
    readiness_revision BIGINT NOT NULL CHECK (readiness_revision >= 1),
    recorded_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (broker, account_ref),
    FOREIGN KEY (broker, account_ref, generation, current_epoch_id)
        REFERENCES trading.execution_continuity_epochs (broker, account_ref, generation, epoch_id)
);

COMMENT ON TABLE trading.execution_continuity_heads IS
    '每個 broker account 唯一 current continuity selector；epoch 本身的歷史旗標不得取代此 authority。';
COMMENT ON COLUMN trading.execution_continuity_heads.current_epoch_id IS
    '目前唯一被選定的 continuity epoch；不得以字串、時間或歷史 trusted 標記推論。';
COMMENT ON COLUMN trading.execution_continuity_heads.head_revision IS
    'current head 的單調 CAS revision，用於拒絕 stale 或 concurrent transition。';
COMMENT ON COLUMN trading.execution_continuity_heads.transition_receipt_id IS
    '建立 current head 的 exact append-only transition receipt identity。';

CREATE TABLE trading.continuity_transition_receipts (
    transition_id TEXT PRIMARY KEY,
    broker TEXT NOT NULL,
    account_ref TEXT NOT NULL,
    generation BIGINT NOT NULL CHECK (generation >= 1),
    previous_epoch_id TEXT NULL,
    current_epoch_id TEXT NOT NULL,
    previous_head_revision BIGINT NOT NULL CHECK (previous_head_revision >= 0),
    head_revision BIGINT NOT NULL CHECK (head_revision = previous_head_revision + 1),
    previous_readiness_revision BIGINT NOT NULL CHECK (previous_readiness_revision >= 0),
    readiness_revision BIGINT NOT NULL CHECK (readiness_revision = previous_readiness_revision + 1),
    recovery_cut_fingerprint TEXT NOT NULL,
    anchor_fingerprint TEXT NOT NULL,
    recovery_cut_revision BIGINT NOT NULL CHECK (recovery_cut_revision >= 0),
    ingress_version BIGINT NOT NULL CHECK (ingress_version >= 0),
    account_revision BIGINT NOT NULL CHECK (account_revision >= 0),
    expected_snapshot_id TEXT NOT NULL,
    authority_commit_id TEXT NOT NULL,
    gap_set_fingerprint TEXT NOT NULL,
    producer_id TEXT NOT NULL,
    contract_version TEXT NOT NULL,
    evidence_id TEXT NOT NULL,
    recorded_at TIMESTAMPTZ NOT NULL,
    evidence_json JSONB NOT NULL CHECK (jsonb_typeof(evidence_json) = 'array'),
    receipt_json JSONB NOT NULL CHECK (jsonb_typeof(receipt_json) = 'object'),
    UNIQUE (broker, account_ref, head_revision),
    UNIQUE (transition_id, broker, account_ref, generation, current_epoch_id, head_revision, readiness_revision),
    FOREIGN KEY (broker, account_ref, generation, current_epoch_id)
        REFERENCES trading.execution_continuity_epochs (broker, account_ref, generation, epoch_id),
    FOREIGN KEY (broker, account_ref, generation, previous_epoch_id)
        REFERENCES trading.execution_continuity_epochs (broker, account_ref, generation, epoch_id)
);

ALTER TABLE trading.execution_continuity_heads
    ADD CONSTRAINT execution_continuity_heads_receipt_scope_fk
    FOREIGN KEY (transition_receipt_id, broker, account_ref, generation, current_epoch_id, head_revision, readiness_revision)
    REFERENCES trading.continuity_transition_receipts
        (transition_id, broker, account_ref, generation, current_epoch_id, head_revision, readiness_revision);

COMMENT ON TABLE trading.continuity_transition_receipts IS
    'Append-only continuity current-head transition 證據；revision 鏈是 causal ordering authority。';
COMMENT ON COLUMN trading.continuity_transition_receipts.transition_id IS
    '穩定 transition identity；相同 identity 的不同 material content 必須 fail closed。';
COMMENT ON COLUMN trading.continuity_transition_receipts.previous_head_revision IS
    'transition 接受前的 exact continuity head revision。';
COMMENT ON COLUMN trading.continuity_transition_receipts.previous_readiness_revision IS
    'transition 接受前的 exact account readiness fence。';
COMMENT ON COLUMN trading.continuity_transition_receipts.recovery_cut_revision IS
    '在 account recovery control 鎖下驗證的本地 recovery cut revision；不得由其他 fingerprint 推論。';

-- W4R-B1：延伸 trusted recovery evidence receipts；不執行歷史回填。
CREATE TABLE trading.broker_discovery_receipts (
    discovery_run_id TEXT PRIMARY KEY,
    broker TEXT NOT NULL,
    account_ref TEXT NOT NULL,
    generation BIGINT NOT NULL CHECK (generation >= 1),
    recorded_at TIMESTAMPTZ NOT NULL,
    receipt_json JSONB NOT NULL,
    result_fingerprint TEXT GENERATED ALWAYS AS (receipt_json ->> 'result_fingerprint') STORED,
    CHECK (length(btrim(result_fingerprint)) > 0)
);
COMMENT ON TABLE trading.broker_discovery_receipts IS 'Broker discovery canonical result 的不可變正向證據；不代表 runtime authorization。';
COMMENT ON COLUMN trading.broker_discovery_receipts.discovery_run_id IS 'Discovery receipt 唯一 identity；禁止 latest fallback。';
COMMENT ON COLUMN trading.broker_discovery_receipts.generation IS '必須匹配寫入當下 active account recovery generation。';
COMMENT ON COLUMN trading.broker_discovery_receipts.result_fingerprint IS '由完整 canonical BrokerDiscoveryResult 決定性衍生的 SHA-256。';
COMMENT ON COLUMN trading.broker_discovery_receipts.receipt_json IS '完整 immutable canonical receipt，供 duplicate material equality 驗證。';

CREATE TABLE trading.broker_reconstruction_receipts (
    reconstruction_receipt_id TEXT PRIMARY KEY,
    broker TEXT NOT NULL,
    account_ref TEXT NOT NULL,
    generation BIGINT NOT NULL CHECK (generation >= 1),
    recorded_at TIMESTAMPTZ NOT NULL,
    receipt_json JSONB NOT NULL,
    recovery_cut_fingerprint TEXT GENERATED ALWAYS AS (receipt_json ->> 'recovery_cut_fingerprint') STORED,
    discovery_run_id TEXT GENERATED ALWAYS AS (receipt_json ->> 'discovery_run_id') STORED,
    order_id TEXT GENERATED ALWAYS AS (receipt_json ->> 'order_id') STORED,
    input_coverage_fingerprint TEXT GENERATED ALWAYS AS (receipt_json ->> 'input_coverage_fingerprint') STORED,
    output_fingerprint TEXT GENERATED ALWAYS AS (receipt_json ->> 'output_fingerprint') STORED,
    deal_set_completeness TEXT GENERATED ALWAYS AS (receipt_json ->> 'deal_set_completeness') STORED,
    CHECK (deal_set_completeness = 'COMPLETE'),
    CHECK (length(btrim(output_fingerprint)) > 0)
);
COMMENT ON TABLE trading.broker_reconstruction_receipts IS '完整 DealSet reconstruction 的不可變正向證據；缺少資料列即無正向 authority。';
COMMENT ON COLUMN trading.broker_reconstruction_receipts.reconstruction_receipt_id IS 'Reconstruction receipt 唯一 identity。';
COMMENT ON COLUMN trading.broker_reconstruction_receipts.generation IS '必須匹配 active account recovery generation。';
COMMENT ON COLUMN trading.broker_reconstruction_receipts.input_coverage_fingerprint IS '重建輸入 coverage 的決定性 fingerprint。';
COMMENT ON COLUMN trading.broker_reconstruction_receipts.output_fingerprint IS '重建 lifecycle/economics 輸出的決定性 fingerprint。';
COMMENT ON COLUMN trading.broker_reconstruction_receipts.receipt_json IS '包含 exact accepted Fill IDs 與完整 immutable canonical receipt。';
