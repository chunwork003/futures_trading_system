from pathlib import Path
from typing import Optional

import duckdb


class InstrumentRepository:
    def __init__(
        self,
        database_path: str = "database/market.duckdb",
    ):
        self.database_path = Path(database_path)

    def _connect(self):
        return duckdb.connect(str(self.database_path))

    def get(self, symbol: str) -> Optional[dict]:
        conn = self._connect()

        try:
            row = conn.execute(
                """
                SELECT
                    instrument_id,
                    symbol,
                    name,
                    asset_type,
                    exchange,
                    currency,
                    multiplier,
                    tick_size
                FROM instruments
                WHERE symbol = ?
                """,
                [symbol],
            ).fetchone()

            if row is None:
                return None

            return {
                "instrument_id": row[0],
                "symbol": row[1],
                "name": row[2],
                "asset_type": row[3],
                "exchange": row[4],
                "currency": row[5],
                "multiplier": row[6],
                "tick_size": row[7],
            }

        finally:
            conn.close()

    def get_tick_value(self, symbol: str) -> Optional[float]:
        instrument = self.get(symbol)

        if instrument is None:
            return None

        multiplier = instrument["multiplier"]
        tick_size = instrument["tick_size"]

        if multiplier is None or tick_size is None:
            return None

        return multiplier * tick_size