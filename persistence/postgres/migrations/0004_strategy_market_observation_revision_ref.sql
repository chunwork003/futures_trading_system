
ALTER TABLE trading.strategy_state_snapshots
    ADD COLUMN last_market_observation_revision_id TEXT;

COMMENT ON COLUMN
    trading.strategy_state_snapshots.last_market_observation_revision_id IS
'Canonical MarketObservation ?????????????????? mor1 revision-specific identity??? legacy row ???? NULL?';

COMMENT ON COLUMN
    trading.strategy_state_snapshots.last_market_observation_id IS
'Legacy ?????canonical revision ??????? mirror ?? mor1???????????????';

ALTER TABLE trading.strategy_state_snapshots
    ADD CONSTRAINT ck_strategy_state_market_observation_revision_id
    CHECK (
        last_market_observation_revision_id IS NULL
        OR last_market_observation_revision_id
            ~ '^mor1_[0-9a-f]{64}$'
    );

COMMENT ON CONSTRAINT
    ck_strategy_state_market_observation_revision_id
    ON trading.strategy_state_snapshots IS
'Canonical ???????????? C23 mor1_<64 lowercase SHA-256 hex>?NULL ???? legacy row ???';

ALTER TABLE trading.strategy_state_snapshots
    ADD CONSTRAINT ck_strategy_state_market_observation_legacy_mirror
    CHECK (
        last_market_observation_revision_id IS NULL
        OR last_market_observation_id
            = last_market_observation_revision_id
    );

COMMENT ON CONSTRAINT
    ck_strategy_state_market_observation_legacy_mirror
    ON trading.strategy_state_snapshots IS
'Canonical revision ????legacy last_market_observation_id ?? mirror ???? mor1????????????';

ALTER TABLE trading.strategy_state_snapshots
    ADD CONSTRAINT fk_strategy_state_market_observation_revision
    FOREIGN KEY (
        last_market_observation_revision_id
    )
    REFERENCES trading.market_observation_revisions
        (observation_revision_id);

COMMENT ON CONSTRAINT
    fk_strategy_state_market_observation_revision
    ON trading.strategy_state_snapshots IS
'Canonical ?????????????? durable ? MarketObservationRevision??? candidate ??? BAR ID ?? recovery authority?';
