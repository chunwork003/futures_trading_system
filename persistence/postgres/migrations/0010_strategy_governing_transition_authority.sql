-- GAP-08 P7 C17：Strategy governing-context transition authority。
-- 本 migration 僅建立 source contract；本 wave 明確禁止執行 migration 或歷史回填。

CREATE TABLE trading.strategy_governing_transition_authorities (
    transition_id TEXT PRIMARY KEY,
    strategy_instance_id TEXT NOT NULL
        REFERENCES trading.strategy_instances(strategy_instance_id),
    source_config_version TEXT NOT NULL,
    source_config_fingerprint TEXT NOT NULL,
    source_implementation_revision TEXT NOT NULL,
    source_instrument_id BIGINT NOT NULL CHECK (source_instrument_id > 0),
    target_config_version TEXT NOT NULL,
    target_config_fingerprint TEXT NOT NULL,
    target_implementation_revision TEXT NOT NULL,
    target_instrument_id BIGINT NOT NULL CHECK (target_instrument_id > 0),
    transition_policy_id TEXT NOT NULL,
    transition_policy_version TEXT NOT NULL,
    transition_json JSONB NOT NULL
        CHECK (jsonb_typeof(transition_json) = 'object'),
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (transition_id, strategy_instance_id)
);

COMMENT ON TABLE trading.strategy_governing_transition_authorities IS
    'C17 append-only governing-context transition authority；PRE/IN_PROGRESS/POST classification 由 immutable transition payload 與 durable boundary evidence 決定。';
COMMENT ON COLUMN trading.strategy_governing_transition_authorities.transition_id IS
    '穩定 transition identity；相同 identity 不得對應不同 authority material。';
COMMENT ON COLUMN trading.strategy_governing_transition_authorities.strategy_instance_id IS
    '被 transition 綁定的 exact C16 StrategyInstance lifecycle identity。';
COMMENT ON COLUMN trading.strategy_governing_transition_authorities.transition_json IS
    '完整 source/target config、implementation、instrument provenance、policy、compatibility/migration authority 與 durable boundary evidence。';
COMMENT ON COLUMN trading.strategy_governing_transition_authorities.recorded_at IS
    'Audit timestamp only；不得作為 transition ordering 或 effective authority。';

CREATE TABLE trading.strategy_governing_transition_heads (
    strategy_instance_id TEXT PRIMARY KEY
        REFERENCES trading.strategy_instances(strategy_instance_id),
    transition_id TEXT NOT NULL,
    head_revision BIGINT NOT NULL CHECK (head_revision >= 1),
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (transition_id, strategy_instance_id)
        REFERENCES trading.strategy_governing_transition_authorities
            (transition_id, strategy_instance_id)
);

COMMENT ON TABLE trading.strategy_governing_transition_heads IS
    '每個 StrategyInstance 唯一 current C17 transition selector；禁止 SQL latest/time ordering 發明 governing authority。';
COMMENT ON COLUMN trading.strategy_governing_transition_heads.transition_id IS
    'current transition 的 exact durable pointer。';
COMMENT ON COLUMN trading.strategy_governing_transition_heads.head_revision IS
    'current head 的 CAS revision；只處理 current-pointer concurrency，不代表策略 state revision。';
COMMENT ON COLUMN trading.strategy_governing_transition_heads.recorded_at IS
    'Audit timestamp only；不得作為 current transition authority。';
