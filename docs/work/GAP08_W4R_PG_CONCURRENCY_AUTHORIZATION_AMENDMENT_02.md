# GAP-08 W4R PostgreSQL Gate Authorization Amendment 02

Status:

`BOUNDED_AUTHORIZED_FOR_W4R_PG_RF02_STRATEGY_JSONB_ONLY`

Planning baseline:

`0898cc0702d5fff2cb0328716c474e74768e775f`

## Exact writable files

Production:

- `persistence/postgres/strategy_state.py`

Tests:

- `tests/integration/test_operational_persistence.py`
- `tests/unit/test_operational_postgres.py`

Exactly these three files.

The already-dirty RF01 integration fixture is explicitly retained and included in the final RF02 commit.

## Production correction

In `PostgresStrategyInstanceRepository.append()`:

replace raw dict binding of `instance.config_json` with deterministic JSON text.

In `PostgresStrategyStateRepository.append()`:

replace raw dict binding of `snapshot.state_json` with deterministic JSON text.

Required serialization contract:

```python
json.dumps(
    value,
    sort_keys=True,
    separators=(",", ":"),
    ensure_ascii=False,
)
```

Do not change complete `instance_json` / `snapshot_json` evidence behavior.

Do not commit inside repository methods.

## Integration fixture correction

Retain:

`broker_client_order_ref=f"PG{major}-CLIENT"`

Replace legacy strategy-state observation reference with canonical `mor1_` revision identity.

No other scenario semantics may change.

## Unit regression guard

Add a bounded unit test to `tests/unit/test_operational_postgres.py` proving:

- StrategyInstance JSONB `config_json` bound parameter is a string;
- JSON round-trip equals instance config;
- StrategyStateSnapshot JSONB `state_json` bound parameter is a string;
- JSON round-trip equals snapshot state;
- complete model JSON parameters remain strings;
- neither repository commits.

## Environment

`POSTGRES17_TEST_DSN` remains the only required actual test database.

`POSTGRES18_TEST_DSN` may remain absent.

Do not print DSN values.

No production/V07 DB.

## Test gates

Unit:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/test_operational_postgres.py -q --basetemp .\.tmp\pytest-w4r-pg-rf02-unit
```

Concurrency targeted:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/integration/test_w4r_recovery_concurrency.py -q --basetemp .\.tmp\pytest-w4r-pg-rf02-concurrency
```

Compatibility:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/integration/test_postgres_foundation.py tests/integration/test_operational_persistence.py -q --basetemp .\.tmp\pytest-w4r-pg-rf02-compat
```

Full regression exactly once after prior gates pass:

```powershell
.\.venv\Scripts\python.exe -m pytest -q --basetemp .\.tmp\pytest-w4r-pg-rf02-full
```

## Git

Exactly one RF02 source/test commit:

`fix(persistence): serialize strategy JSONB for PostgreSQL`

Then push once and STOP.

## Denied

- any migration source change;
- any other production file;
- D3/concurrency semantic change;
- broker I/O;
- production/V07 DB;
- W4 closure by executor;
- P7.
