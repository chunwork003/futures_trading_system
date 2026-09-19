from datetime import date
from pathlib import Path
from typing import Optional

import duckdb


class ContractRepository:

    def __init__(
        self,
        database_path: str = "database/market.duckdb",
    ):
        self.database_path = Path(database_path)

    def _connect(self):
        return duckdb.connect(
            str(self.database_path)
        )

    def get(
        self,
        contract_code: str,
    ) -> Optional[dict]:

        conn = self._connect()

        try:
            row = conn.execute(
                """
                SELECT
                    contract_id,
                    instrument_id,
                    contract_code,
                    contract_month,
                    listing_date,
                    last_trade_date,
                    settlement_date,
                    status
                FROM contracts
                WHERE contract_code = ?
                """,
                [contract_code],
            ).fetchone()

            if row is None:
                return None

            return {
                "contract_id": row[0],
                "instrument_id": row[1],
                "contract_code": row[2],
                "contract_month": row[3],
                "listing_date": row[4],
                "last_trade_date": row[5],
                "settlement_date": row[6],
                "status": row[7],
            }

        finally:
            conn.close()

    def exists(
        self,
        contract_code: str,
    ) -> bool:

        return self.get(contract_code) is not None

    def get_last_trade_date(
        self,
        contract_code: str,
    ) -> Optional[date]:

        contract = self.get(contract_code)

        if contract is None:
            return None

        return contract["last_trade_date"]

    def insert(
        self,
        contract: dict,
    ) -> None:

        conn = self._connect()

        try:
            conn.execute(
                """
                INSERT INTO contracts (
                    contract_id,
                    instrument_id,
                    contract_code,
                    contract_month,
                    listing_date,
                    last_trade_date,
                    settlement_date,
                    status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    contract["contract_id"],
                    contract["instrument_id"],
                    contract["contract_code"],
                    contract["contract_month"],
                    contract["listing_date"],
                    contract["last_trade_date"],
                    contract["settlement_date"],
                    contract["status"],
                ],
            )

        finally:
            conn.close()