-- GAP-08 P7 C17 RF01：Pattern A governing-transition authority。
-- 本 migration 僅建立 source contract；禁止執行 migration、回填或歷史 authority rewrite。

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
    transition_json JSONB NOT NULL CHECK (jsonb_typeof(transition_json) = 'object'),
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (transition_id, strategy_instance_id)
);

COMMENT ON TABLE trading.strategy_governing_transition_authorities IS
    'C17 immutable transition descriptor；同一 transition_id 跨 PRE/IN_PROGRESS/POST 永不覆寫。';
COMMENT ON COLUMN trading.strategy_governing_transition_authorities.transition_json IS
    'Stable source/target governing context 與 compatibility/migration/policy authority；不得嵌入 phase progression。';
COMMENT ON COLUMN trading.strategy_governing_transition_authorities.recorded_at IS
    'Audit timestamp only；不得作為 transition ordering 或 authority。';

CREATE TABLE trading.strategy_governing_transition_phase_evidence (
    evidence_id TEXT PRIMARY KEY,
    transition_id TEXT NOT NULL,
    strategy_instance_id TEXT NOT NULL,
    evidence_kind TEXT NOT NULL
        CHECK (evidence_kind IN ('BEGIN_EFFECTIVE','COMPLETION')),
    boundary_ref TEXT NOT NULL,
    evidence_json JSONB NOT NULL CHECK (jsonb_typeof(evidence_json) = 'object'),
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (transition_id, evidence_kind),
    FOREIGN KEY (transition_id, strategy_instance_id)
        REFERENCES trading.strategy_governing_transition_authorities
            (transition_id, strategy_instance_id)
);

COMMENT ON TABLE trading.strategy_governing_transition_phase_evidence IS
    '同一 stable transition_id 的 append-only BEGIN/COMPLETION evidence；同 kind 不得有不同 material。';
COMMENT ON COLUMN trading.strategy_governing_transition_phase_evidence.recorded_at IS
    'Audit timestamp only；不得決定 phase/currentness。';

CREATE TABLE trading.strategy_governing_transition_resolution_receipts (
    resolution_id TEXT PRIMARY KEY,
    strategy_instance_id TEXT NOT NULL
        REFERENCES trading.strategy_instances(strategy_instance_id),
    resolution_revision BIGINT NOT NULL CHECK (resolution_revision >= 1),
    resolution_kind TEXT NOT NULL
        CHECK (resolution_kind IN ('ACTIVE_TRANSITION','NO_ACTIVE_TRANSITION')),
    transition_id TEXT NULL,
    effective_config_version TEXT NOT NULL,
    effective_config_fingerprint TEXT NOT NULL,
    resolution_authority_id TEXT NOT NULL,
    resolution_authority_version TEXT NOT NULL,
    currentness_evidence_ref TEXT NOT NULL,
    resolution_json JSONB NOT NULL CHECK (jsonb_typeof(resolution_json) = 'object'),
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (resolution_id, strategy_instance_id),
    UNIQUE (strategy_instance_id, resolution_revision),
    CHECK (
        (resolution_kind='ACTIVE_TRANSITION' AND transition_id IS NOT NULL)
        OR
        (resolution_kind='NO_ACTIVE_TRANSITION' AND transition_id IS NULL)
    ),
    FOREIGN KEY (transition_id, strategy_instance_id)
        REFERENCES trading.strategy_governing_transition_authorities
            (transition_id, strategy_instance_id)
);

COMMENT ON TABLE trading.strategy_governing_transition_resolution_receipts IS
    'Immutable resolver receipts；NO_ACTIVE_TRANSITION 是正向 authority receipt，不是第四個 C17 state。';
COMMENT ON COLUMN trading.strategy_governing_transition_resolution_receipts.resolution_revision IS
    'Append-only resolution revision；currentness 必須由 exact CAS head selector 證明。';

CREATE TABLE trading.strategy_governing_transition_resolution_heads (
    strategy_instance_id TEXT PRIMARY KEY
        REFERENCES trading.strategy_instances(strategy_instance_id),
    resolution_id TEXT NOT NULL,
    head_revision BIGINT NOT NULL CHECK (head_revision >= 1),
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (resolution_id, strategy_instance_id)
        REFERENCES trading.strategy_governing_transition_resolution_receipts
            (resolution_id, strategy_instance_id)
);

COMMENT ON TABLE trading.strategy_governing_transition_resolution_heads IS
    '每個 StrategyInstance 唯一 current resolution selector；只有此 pointer 可 CAS advance。';
COMMENT ON COLUMN trading.strategy_governing_transition_resolution_heads.head_revision IS
    'CAS current-resolution revision；不得以 wall clock 或 SQL latest-row 取代。';
COMMENT ON COLUMN trading.strategy_governing_transition_resolution_heads.recorded_at IS
    'Audit timestamp only；不得作為 current resolution authority。';
