CREATE TABLE trading.market_observation_acceptance_policies (
    policy_id TEXT NOT NULL,
    version BIGINT NOT NULL CHECK (version >= 1),
    scope_ref TEXT NOT NULL,
    policy_json JSONB NOT NULL,
    PRIMARY KEY (policy_id, version)
);

COMMENT ON TABLE trading.market_observation_acceptance_policies IS
'市場觀測接受政策的不可變版本證據；routing role 與 canonical truth authority 必須分離。';
COMMENT ON COLUMN trading.market_observation_acceptance_policies.policy_id IS
'接受政策穩定識別；同一 policy_id 可透過 version 建立新政策版本。';
COMMENT ON COLUMN trading.market_observation_acceptance_policies.version IS
'接受政策版本；政策變更不得回寫既有 accepted revision。';
COMMENT ON COLUMN trading.market_observation_acceptance_policies.scope_ref IS
'政策適用 scope 的穩定識別；不得由 routing PRIMARY 隱式推導 truth authority。';
COMMENT ON COLUMN trading.market_observation_acceptance_policies.policy_json IS
'完整不可變 policy audit evidence；不參與 mor1 identity。';


CREATE TABLE trading.market_observation_candidates (
    candidate_id TEXT PRIMARY KEY,
    instrument_id BIGINT NOT NULL CHECK (instrument_id > 0),
    contract_id BIGINT CHECK (contract_id > 0),
    timeframe TEXT NOT NULL,
    interval_start_at TIMESTAMPTZ NOT NULL,
    content_schema_version INTEGER NOT NULL CHECK (content_schema_version >= 1),

    open_price NUMERIC NOT NULL,
    high_price NUMERIC NOT NULL,
    low_price NUMERIC NOT NULL,
    close_price NUMERIC NOT NULL,
    volume BIGINT NOT NULL CHECK (volume >= 0),
    amount NUMERIC,
    trade_count BIGINT CHECK (trade_count >= 0),
    tick_count BIGINT CHECK (tick_count >= 0),
    trade_date DATE NOT NULL,
    session_ref TEXT,

    content_fingerprint TEXT NOT NULL
        CHECK (content_fingerprint ~ '^[0-9a-f]{64}$'),
    observation_revision_id TEXT NOT NULL
        CHECK (observation_revision_id ~ '^mor1_[0-9a-f]{64}$'),

    source_id TEXT NOT NULL,
    routing_role TEXT NOT NULL
        CHECK (routing_role IN ('PRIMARY','SECONDARY','VALIDATION')),
    source_record_ref TEXT,
    formal_correction_ref TEXT,
    received_at TIMESTAMPTZ NOT NULL,
    provenance_json JSONB NOT NULL,

    acceptance_policy_id TEXT NOT NULL,
    acceptance_policy_version BIGINT NOT NULL CHECK (acceptance_policy_version >= 1),
    acceptance_scope_ref TEXT NOT NULL,

    candidate_json JSONB NOT NULL,

    FOREIGN KEY (acceptance_policy_id, acceptance_policy_version)
        REFERENCES trading.market_observation_acceptance_policies
            (policy_id, version)
);

COMMENT ON TABLE trading.market_observation_candidates IS
'不可變 MarketObservation candidate/provenance evidence；candidate durable 不代表 canonical acceptance。';
COMMENT ON COLUMN trading.market_observation_candidates.candidate_id IS
'上游提供的 immutable candidate identity；相同 ID 不得對應不同 evidence。';
COMMENT ON COLUMN trading.market_observation_candidates.observation_revision_id IS
'C23 deterministic mor1 revision-specific identity；candidate 尚未接受時仍可存在。';
COMMENT ON COLUMN trading.market_observation_candidates.content_fingerprint IS
'C23 canonical content SHA-256 fingerprint；source/provenance 不得影響此值。';
COMMENT ON COLUMN trading.market_observation_candidates.source_id IS
'候選資料來源 identity；來源本身不自動取得 canonical truth authority。';
COMMENT ON COLUMN trading.market_observation_candidates.routing_role IS
'資料取得 routing role；PRIMARY 不等同 AUTHORITATIVE_FOR_SCOPE。';
COMMENT ON COLUMN trading.market_observation_candidates.formal_correction_ref IS
'來源正式 correction evidence reference；不同內容自動接受時必須由 policy 明確授權。';
COMMENT ON COLUMN trading.market_observation_candidates.received_at IS
'系統收到 candidate evidence 的具時區時間；不得作為 revision causal authority。';
COMMENT ON COLUMN trading.market_observation_candidates.provenance_json IS
'來源與 provenance audit evidence；provenance-only 變更不得產生新 content revision。';


CREATE TABLE trading.market_observation_revisions (
    observation_revision_id TEXT PRIMARY KEY
        CHECK (observation_revision_id ~ '^mor1_[0-9a-f]{64}$'),

    instrument_id BIGINT NOT NULL CHECK (instrument_id > 0),
    contract_id BIGINT CHECK (contract_id > 0),
    timeframe TEXT NOT NULL,
    interval_start_at TIMESTAMPTZ NOT NULL,
    content_schema_version INTEGER NOT NULL CHECK (content_schema_version >= 1),

    open_price NUMERIC NOT NULL,
    high_price NUMERIC NOT NULL,
    low_price NUMERIC NOT NULL,
    close_price NUMERIC NOT NULL,
    volume BIGINT NOT NULL CHECK (volume >= 0),
    amount NUMERIC,
    trade_count BIGINT CHECK (trade_count >= 0),
    tick_count BIGINT CHECK (tick_count >= 0),
    trade_date DATE NOT NULL,
    session_ref TEXT,

    content_fingerprint TEXT NOT NULL
        CHECK (content_fingerprint ~ '^[0-9a-f]{64}$'),

    revision_seq BIGINT NOT NULL CHECK (revision_seq >= 1),
    supersedes_revision_id TEXT
        REFERENCES trading.market_observation_revisions(observation_revision_id),

    accepted_at TIMESTAMPTZ NOT NULL,
    acceptance_policy_id TEXT NOT NULL,
    acceptance_policy_version BIGINT NOT NULL CHECK (acceptance_policy_version >= 1),
    acceptance_scope_ref TEXT NOT NULL,

    revision_json JSONB NOT NULL,

    FOREIGN KEY (acceptance_policy_id, acceptance_policy_version)
        REFERENCES trading.market_observation_acceptance_policies
            (policy_id, version),

    CONSTRAINT uq_market_observation_revision_content
        UNIQUE NULLS NOT DISTINCT
        (
            instrument_id,
            contract_id,
            timeframe,
            interval_start_at,
            content_schema_version,
            content_fingerprint
        ),

    CONSTRAINT uq_market_observation_revision_seq
        UNIQUE NULLS NOT DISTINCT
        (
            instrument_id,
            contract_id,
            timeframe,
            interval_start_at,
            revision_seq
        )
);

COMMENT ON TABLE trading.market_observation_revisions IS
'已接受的不可變 canonical MarketObservation 修訂版本；revision_seq 為 logical-key authority order。';
COMMENT ON COLUMN trading.market_observation_revisions.observation_revision_id IS
'C23 產生之 mor1 opaque revision identity；禁止 collision 後 salt/regenerate。';
COMMENT ON COLUMN trading.market_observation_revisions.revision_seq IS
'同一 logical key 下的 contiguous accepted revision authority sequence。';
COMMENT ON COLUMN trading.market_observation_revisions.supersedes_revision_id IS
'正式 correction 接受時精確指向前一 accepted revision。';
COMMENT ON COLUMN trading.market_observation_revisions.accepted_at IS
'該 revision 被 policy 接受的顯式時間；非 market occurrence time。';
COMMENT ON COLUMN trading.market_observation_revisions.acceptance_policy_id IS
'產生接受決策的 policy identity；不參與 mor1 identity。';


CREATE TABLE trading.market_observation_candidate_decisions (
    decision_id TEXT PRIMARY KEY,
    candidate_id TEXT NOT NULL
        REFERENCES trading.market_observation_candidates(candidate_id),
    decision_kind TEXT NOT NULL,
    decided_at TIMESTAMPTZ NOT NULL,
    linked_revision_id TEXT,
    reason TEXT,

    acceptance_policy_id TEXT NOT NULL,
    acceptance_policy_version BIGINT NOT NULL CHECK (acceptance_policy_version >= 1),
    acceptance_scope_ref TEXT NOT NULL,

    decision_json JSONB NOT NULL,

    FOREIGN KEY (acceptance_policy_id, acceptance_policy_version)
        REFERENCES trading.market_observation_acceptance_policies
            (policy_id, version)
);

COMMENT ON TABLE trading.market_observation_candidate_decisions IS
'不可變 candidate acceptance/corroboration/quarantine decision history。';
COMMENT ON COLUMN trading.market_observation_candidate_decisions.decision_kind IS
'顯式接受、corroboration、quarantine 或 integrity-conflict 類型。';
COMMENT ON COLUMN trading.market_observation_candidate_decisions.linked_revision_id IS
'該 decision 關聯的 accepted revision；quarantine 可保留當前 accepted revision reference。';
COMMENT ON COLUMN trading.market_observation_candidate_decisions.reason IS
'明確 audit reason；actor/reason 本身不是 production authorization proof。';


CREATE TABLE trading.market_observation_revision_evidence (
    candidate_id TEXT NOT NULL
        REFERENCES trading.market_observation_candidates(candidate_id),
    observation_revision_id TEXT NOT NULL
        REFERENCES trading.market_observation_revisions(observation_revision_id),
    evidence_kind TEXT NOT NULL,
    recorded_at TIMESTAMPTZ NOT NULL,

    PRIMARY KEY (
        candidate_id,
        observation_revision_id,
        evidence_kind
    )
);

COMMENT ON TABLE trading.market_observation_revision_evidence IS
'candidate-to-accepted-revision 不可變 evidence/corroboration link；多 source 相同 content 不建立人工 revision。';
COMMENT ON COLUMN trading.market_observation_revision_evidence.evidence_kind IS
'ACCEPTED 或 CORROBORATED 等 evidence 關係，不改變 mor1 identity。';


CREATE TABLE trading.market_observation_heads (
    head_id BIGSERIAL PRIMARY KEY,

    instrument_id BIGINT NOT NULL CHECK (instrument_id > 0),
    contract_id BIGINT CHECK (contract_id > 0),
    timeframe TEXT NOT NULL,
    interval_start_at TIMESTAMPTZ NOT NULL,

    current_revision_id TEXT
        REFERENCES trading.market_observation_revisions(observation_revision_id),

    revision_seq BIGINT NOT NULL DEFAULT 0
        CHECK (revision_seq >= 0),

    quarantined BOOLEAN NOT NULL DEFAULT FALSE,
    quarantine_reason TEXT,

    CONSTRAINT uq_market_observation_logical_head
        UNIQUE NULLS NOT DISTINCT
        (
            instrument_id,
            contract_id,
            timeframe,
            interval_start_at
        ),

    CHECK (
        (revision_seq = 0 AND current_revision_id IS NULL)
        OR
        (revision_seq >= 1 AND current_revision_id IS NOT NULL)
    )
);

COMMENT ON TABLE trading.market_observation_heads IS
'每個 MarketObservation logical key 的 mutable concurrency/current-state projection；歷史 authority 仍在 immutable evidence tables。';
COMMENT ON COLUMN trading.market_observation_heads.current_revision_id IS
'目前 accepted revision reference；不得因 provenance-only evidence 改變。';
COMMENT ON COLUMN trading.market_observation_heads.revision_seq IS
'目前 accepted contiguous revision sequence；只有新 accepted revision 可遞增。';
COMMENT ON COLUMN trading.market_observation_heads.quarantined IS
'此 logical key 是否因 evidence/policy/integrity conflict 而禁止 strategy-consumable authority。';
COMMENT ON COLUMN trading.market_observation_heads.quarantine_reason IS
'目前隔離（quarantine）原因；解除隔離需要未來明確 authority workflow。';
