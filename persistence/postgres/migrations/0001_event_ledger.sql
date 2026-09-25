CREATE SCHEMA IF NOT EXISTS trading;

CREATE TABLE trading.event_ledger (
    event_id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL,
    source TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    occurred_at TIMESTAMPTZ NOT NULL,
    received_at TIMESTAMPTZ NOT NULL,
    sequence BIGINT NOT NULL CHECK (sequence >= 0),
    event_version INTEGER NOT NULL CHECK (event_version >= 1),
    idempotency_scope TEXT NOT NULL,
    idempotency_key TEXT NOT NULL,
    correlation_id TEXT,
    causation_id TEXT,
    payload_json JSONB NOT NULL,
    UNIQUE (idempotency_scope, idempotency_key),
    UNIQUE (source, entity_type, entity_id, sequence)
);

COMMENT ON TABLE trading.event_ledger IS '交易系統不可變事件帳本；保存可重播與稽核的 canonical 事件。';
COMMENT ON COLUMN trading.event_ledger.event_id IS '呼叫端提供且不可由資料庫改寫的全域事件識別。';
COMMENT ON COLUMN trading.event_ledger.sequence IS '同一來源與實體範圍內的決定性事件序號。';
COMMENT ON COLUMN trading.event_ledger.payload_json IS '事件的 canonical JSON object payload。';
