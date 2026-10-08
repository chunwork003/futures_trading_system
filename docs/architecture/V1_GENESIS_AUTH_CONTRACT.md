# Simulation genesis and browser identity — P00 candidate

## Reservation is not an account

POST /api/v1/simulation-sessions accepts an immutable request, allocates stable future session/account IDs, and atomically stores command receipt + SIMULATION_GENESIS operation + private resource reservation. Return 202 with resource_revision_status=RESERVED, resource_revision=null and operation_id. This reservation has no canonical account head, position or readiness authority. Duplicate key replays the exact receipt; it must not allocate another account.

The fenced worker validates pinned references and constructs explicit synthetic genesis provenance through accepted account initialization contracts. In one PostgreSQL UoW it publishes initial canonical account closure, CREATED session revision 1, reservation completion and SUCCEEDED operation. No order/strategy execution occurs. The session/account metadata and accepted initialization stores must share that transactional database; no distributed transaction. Artifact prerequisites are verified before this transaction and are not proof that genesis committed.

If failure occurs before commit, rollback leaves no visible partial account/session. Retry resolves receipt and canonical commit evidence before repeating. If commit succeeded but response is lost, query Operation then Session; original receipt remains RESERVED because it is immutable, while current projections show committed revision. It is not rewritten to manufacture a second acceptance time. Genesis code must never seed from missing state, an empty provider observation or a reconciliation MATCH; synthetic opening-flat is explicit genesis evidence.

GET reserved session ID returns 409 READINESS_BLOCKED while genesis is unfinished/failed/cancelled; absent reservation returns 404. Error includes the genesis operation ID so UI can display failure instead of polling indefinitely. START/PAUSE/STOP/KILL/FORCE_FLAT before genesis completion reject with 409; no nonexistent account receives a command. Cancel pending genesis through /operations/{id}/cancel: allow kinds RESEARCH, DATASET_IMPORT and SIMULATION_GENESIS, deny SIMULATION_COMMAND. Cancel and genesis publication contend on the same fenced operation CAS. Cancel-first produces no account/session; publish-first is already terminal and preserves CREATED. Failed/cancelled reservation is a permanent tombstone for that creation identity; a deliberately new creation uses a new idempotency key and new IDs.

New non-genesis command receipts have resource_revision_status=COMMITTED and a positive accepted revision. An async operation represents subsequent work, not unknown acceptance. This distinction applies to receipt fields only, not a change to existing accepted account revision semantics.

Acceptance fixtures: crash before genesis UoW; crash between inserts rolls back all; response loss after commit; stale lease holder publish; cancel-first/publish-first; duplicate creation; mismatched same key; startup with failed reservation; attempts to START before genesis; missing genesis provenance rejected.

## Exact BFF authentication routes

Only the BFF exposes /auth routes. Internal Python has none of them and never accepts browser credentials/cookies.

| Route | Input / authorization | Output / effects |
|---|---|---|
| GET /auth/csrf | Anonymous same-origin request; no CORS | 200 request_token and protected antiforgery cookie; Cache-Control:no-store |
| POST /auth/login | username/password JSON, valid antiforgery cookie + X-CSRF-Token, exact Origin | 200 OperatorSession and secure HttpOnly session cookie; generic 401 for invalid credentials; 429 throttle |
| GET /auth/session | Valid session cookie | 200 operator_id, permissions, expires_at; expired/revoked=401 |
| POST /auth/logout | Valid session + antiforgery + Origin | Durable session revocation, clear cookie, 204; repeated unauthenticated call=401, UI still clears local state |

Browser first obtains antiforgery token, then logs in. Tokens must not be placed in URL/localStorage or logs. CSRF validation applies to login too; anonymous access is not Origin bypass. Set no-store on every auth response, no redirects containing credentials. Local operator bootstrap uses an explicit install command and interactive password with minimum 12 characters, no public registration. Password hashing/lockout/security stamp remain ASP.NET Identity responsibility; do not build custom cryptography. Session store is application schema with durable session ID/revocation/created_at/last_activity_at. Absolute timeout 8h, idle timeout 30m, checked on every authenticated request; logout/revocation effective on next request. Restart does not refresh absolute expiry. Five failed logins per account in 15m cause bounded lockout; successful authentication records sanitized audit.

Domain Idempotency-Key/If-Match rules do not apply to /auth endpoints. Do not retain login payload/password fingerprint as a command receipt. Login timeout does not justify an automatic password retry loop; browser queries /auth/session first and presents state. Logout timeout queries session and permits an explicit retry. BFF strips browser-supplied actor/role/internal credential headers and uses the authenticated subject when mediating Python. UI mode labels are projections, never permission.

Required tests: login CSRF and wrong Origin rejection; no anonymous domain access; cookie flags; generic invalid-login response; lockout boundary; idle/absolute expiry across restart; logout revocation; spoofed actor header; password/token redaction; Python rejects cookie-only calls. These are future P02/P11 integration gates, not claims that auth runtime exists today.
