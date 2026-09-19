from pathlib import Path

import duckdb


class DuckDBManager:

    def __init__(
        self,
        database_path: str = "database/market.duckdb",
    ):
        self.database_path = Path(database_path)

    def connect(self):
        self.database_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        return duckdb.connect(
            str(self.database_path)
        )

    def execute(
        self,
        sql: str,
        parameters=None,
    ):
        conn = self.connect()

        try:
            if parameters:
                return conn.execute(
                    sql,
                    parameters,
                )

            return conn.execute(sql)

        finally:
            conn.close()