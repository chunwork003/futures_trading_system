from datetime import date

from trading_calendar.contract_dates import (
    calculate_last_trade_date,
)


class FuturesContractGenerator:

    def __init__(self, trading_calendar):
        self.trading_calendar = trading_calendar

    def generate(
        self,
        instrument: dict,
        year: int,
        month: int,
    ) -> dict:

        contract_id = (
            instrument["instrument_id"] * 1000000
            + year * 100
            + month
        )

        contract_month = date(
            year,
            month,
            1,
        )

        contract_code = (
            f"{instrument['symbol']}"
            f"{year}{month:02d}"
        )

        last_trade_date = (
            calculate_last_trade_date(
                year,
                month,
                self.trading_calendar,
            )
        )

        return {
            "contract_id": contract_id,
            "instrument_id": instrument["instrument_id"],
            "contract_code": contract_code,
            "contract_month": contract_month,
            "listing_date": None,
            "last_trade_date": last_trade_date,
            "settlement_date": last_trade_date,
            "status": "ACTIVE",
        }