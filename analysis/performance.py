import polars as pl


def calculate_performance(
    trades: pl.DataFrame,
) -> dict:

    if trades.height == 0:
        return {
            "trades": 0,
            "net_pnl": 0.0,
        }

    return {
        "trades": trades.height,
        "net_pnl": trades["net_pnl"].sum(),
        "average_pnl": trades["net_pnl"].mean(),
    }