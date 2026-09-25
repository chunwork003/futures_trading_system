CREATE TABLE trading.orders (
    order_id TEXT PRIMARY KEY,
    intent_id TEXT NOT NULL,
    correlation_id TEXT NOT NULL,
    broker_order_id TEXT,
    instrument_id BIGINT NOT NULL,
    contract_id BIGINT,
    status TEXT NOT NULL,
    version BIGINT NOT NULL CHECK (version >= 0),
    projection_json JSONB NOT NULL
);
COMMENT ON TABLE trading.orders IS '由不可變事件推導的訂單最新投影；歷史權威仍為 event ledger。';
COMMENT ON COLUMN trading.orders.version IS '用於 optimistic concurrency 的投影版本。';

CREATE TABLE trading.fills (
    fill_id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL,
    event_id TEXT NOT NULL,
    quantity BIGINT NOT NULL CHECK (quantity > 0),
    price NUMERIC NOT NULL,
    occurred_at TIMESTAMPTZ NOT NULL,
    broker_deal_id TEXT,
    fill_json JSONB NOT NULL,
    UNIQUE (order_id, broker_deal_id)
);
COMMENT ON TABLE trading.fills IS '不可變成交證據；broker deal ID 與內部 fill ID 分離。';
COMMENT ON COLUMN trading.fills.fill_json IS '包含 exact NUMERIC 語意來源的 canonical Fill payload。';

CREATE TABLE trading.expected_position_snapshots (
    snapshot_id TEXT PRIMARY KEY,
    broker TEXT NOT NULL,
    account_ref TEXT NOT NULL,
    effective_at TIMESTAMPTZ NOT NULL,
    recorded_at TIMESTAMPTZ NOT NULL,
    source_event_id TEXT NOT NULL,
    snapshot_json JSONB NOT NULL
);
CREATE TABLE trading.expected_position_snapshot_items (
    snapshot_id TEXT NOT NULL REFERENCES trading.expected_position_snapshots(snapshot_id),
    item_index INTEGER NOT NULL CHECK (item_index >= 0),
    instrument_id BIGINT NOT NULL,
    contract_id BIGINT,
    direction TEXT NOT NULL,
    quantity BIGINT NOT NULL CHECK (quantity > 0),
    PRIMARY KEY (snapshot_id, item_index)
);
COMMENT ON TABLE trading.expected_position_snapshots IS '系統預期實體帳戶部位的完整批次；空 items 表示 FLAT。';
COMMENT ON TABLE trading.expected_position_snapshot_items IS '預期部位批次內的 canonical position items。';

CREATE TABLE trading.broker_position_observations (
    observation_id TEXT PRIMARY KEY,
    broker TEXT NOT NULL,
    account_ref TEXT NOT NULL,
    observed_at TIMESTAMPTZ NOT NULL,
    recorded_at TIMESTAMPTZ NOT NULL,
    observation_json JSONB NOT NULL
);
CREATE TABLE trading.broker_position_observation_items (
    observation_id TEXT NOT NULL REFERENCES trading.broker_position_observations(observation_id),
    item_index INTEGER NOT NULL CHECK (item_index >= 0),
    instrument_id BIGINT NOT NULL,
    contract_id BIGINT,
    direction TEXT NOT NULL,
    quantity BIGINT NOT NULL CHECK (quantity > 0),
    average_price NUMERIC,
    PRIMARY KEY (observation_id, item_index)
);
COMMENT ON TABLE trading.broker_position_observations IS 'Broker actual position 的 audit observation；startup 仍須即時查詢 broker。';
COMMENT ON TABLE trading.broker_position_observation_items IS 'Broker observation 批次內的實際部位 items。';

CREATE TABLE trading.account_snapshots (
    snapshot_id TEXT PRIMARY KEY,
    broker TEXT NOT NULL,
    account_ref TEXT NOT NULL,
    observed_at TIMESTAMPTZ NOT NULL,
    recorded_at TIMESTAMPTZ NOT NULL,
    cash_balance NUMERIC,
    equity NUMERIC,
    available_funds NUMERIC,
    margin_used NUMERIC,
    snapshot_json JSONB NOT NULL,
    CHECK (cash_balance IS NOT NULL OR equity IS NOT NULL OR available_funds IS NOT NULL OR margin_used IS NOT NULL)
);
COMMENT ON TABLE trading.account_snapshots IS 'Broker-observed account monetary evidence，與 risk config 分離。';
COMMENT ON COLUMN trading.account_snapshots.equity IS 'Broker 回報之 exact account equity。';

CREATE TABLE trading.reconciliation_case_history (
    case_id TEXT NOT NULL,
    version BIGINT NOT NULL CHECK (version >= 1),
    recorded_at TIMESTAMPTZ NOT NULL,
    state TEXT NOT NULL,
    actor_ref TEXT,
    evidence JSONB NOT NULL,
    case_json JSONB NOT NULL,
    PRIMARY KEY (case_id, version)
);
COMMENT ON TABLE trading.reconciliation_case_history IS 'Append-only reconciliation case version history；不得覆寫舊版本。';

CREATE TABLE trading.strategy_instances (
    strategy_instance_id TEXT PRIMARY KEY,
    strategy_id TEXT NOT NULL,
    strategy_version TEXT NOT NULL,
    config_version TEXT NOT NULL,
    config_fingerprint TEXT NOT NULL,
    instrument_id BIGINT NOT NULL,
    timeframe TEXT NOT NULL,
    config_json JSONB NOT NULL,
    instance_json JSONB NOT NULL
);
COMMENT ON TABLE trading.strategy_instances IS '不可變策略定義、設定版本及 scope identity。';

CREATE TABLE trading.strategy_state_snapshots (
    snapshot_id TEXT PRIMARY KEY,
    strategy_instance_id TEXT NOT NULL REFERENCES trading.strategy_instances(strategy_instance_id),
    captured_at TIMESTAMPTZ NOT NULL,
    strategy_id TEXT NOT NULL,
    strategy_version TEXT NOT NULL,
    config_version TEXT NOT NULL,
    config_fingerprint TEXT NOT NULL,
    instrument_id BIGINT NOT NULL,
    timeframe TEXT NOT NULL,
    state_schema_version INTEGER NOT NULL CHECK (state_schema_version >= 1),
    last_market_observation_id TEXT NOT NULL,
    state_json JSONB NOT NULL,
    snapshot_json JSONB NOT NULL
);
COMMENT ON TABLE trading.strategy_state_snapshots IS 'Completed market observation boundary 的 versioned logical strategy state。';
COMMENT ON COLUMN trading.strategy_state_snapshots.captured_at IS '策略完成該 observation 處理後的 UTC capture time。';
