ALTER TABLE trading.orders
    ADD COLUMN broker_client_order_ref TEXT;

COMMENT ON COLUMN trading.orders.broker_client_order_ref IS
    '一筆 canonical Order 固定且不可替換的 broker client correlation identity；不代表 broker server-side idempotency。';

CREATE TABLE trading.broker_action_attempts (
    attempt_id TEXT PRIMARY KEY,
    broker TEXT NOT NULL,
    account_ref TEXT NOT NULL,
    order_id TEXT NOT NULL,
    action TEXT NOT NULL CHECK (action IN ('SUBMIT', 'CANCEL')),
    broker_client_order_ref TEXT NOT NULL,
    command_id TEXT NOT NULL,
    correlation_id TEXT NOT NULL,
    authorization_id TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    attempt_json JSONB NOT NULL
);

CREATE TABLE trading.broker_action_resolutions (
    resolution_id TEXT PRIMARY KEY,
    attempt_id TEXT NOT NULL REFERENCES trading.broker_action_attempts(attempt_id),
    kind TEXT NOT NULL CHECK (kind IN ('SUCCEEDED', 'FAILED', 'NOT_DISPATCHED')),
    resolved_at TIMESTAMPTZ NOT NULL,
    resolution_json JSONB NOT NULL
);

CREATE TABLE trading.broker_action_heads (
    broker TEXT NOT NULL,
    account_ref TEXT NOT NULL,
    order_id TEXT NOT NULL,
    action TEXT NOT NULL CHECK (action IN ('SUBMIT', 'CANCEL')),
    version BIGINT NOT NULL CHECK (version >= 1),
    unresolved_attempt_id TEXT REFERENCES trading.broker_action_attempts(attempt_id),
    PRIMARY KEY (broker, account_ref, order_id, action)
);

COMMENT ON TABLE trading.broker_action_attempts IS
    'Broker material action 呼叫前先耐久化的不可變嘗試證據；不代表 OrderStatus。';
COMMENT ON COLUMN trading.broker_action_attempts.authorization_id IS
    'C21 protected action 授權證據參照；不等於 production activation。';
COMMENT ON COLUMN trading.broker_action_attempts.broker_client_order_ref IS
    '用於 broker correlation 的固定 client reference；不是 server-side idempotency authority。';
COMMENT ON TABLE trading.broker_action_resolutions IS
    'Broker action 已知結果的 append-only 證據；未知結果不建立虛構 resolution。';
COMMENT ON COLUMN trading.broker_action_resolutions.resolution_json IS
    '完整 immutable resolution evidence；NOT_DISPATCHED 必須含 verified pre-transport proof。';
COMMENT ON TABLE trading.broker_action_heads IS
    '每個 BrokerAccount、Order、action scope 至多一個 unresolved attempt 的 concurrency projection。';
COMMENT ON COLUMN trading.broker_action_heads.unresolved_attempt_id IS
    '目前阻止 automatic resubmit 或 recancel 的 unresolved attempt identity。';
