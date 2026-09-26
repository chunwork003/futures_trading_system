ALTER TABLE trading.orders
    ADD COLUMN broker_client_order_ref TEXT;

COMMENT ON COLUMN trading.orders.broker_client_order_ref IS
    '一筆 canonical Order 固定且不可替換的 broker client correlation identity；不代表 broker server-side idempotency。';
