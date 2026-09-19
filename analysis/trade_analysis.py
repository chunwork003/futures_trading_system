import polars as pl


def analyze_trades(
    trades: pl.DataFrame,
) -> dict:

    if trades.height == 0:
        return {}

    wins = trades.filter(
        pl.col("net_pnl") > 0
    )

    losses = trades.filter(
        pl.col("net_pnl") <= 0
    )

    return {
        "total_trades": trades.height,
        "winning_trades": wins.height,
        "losing_trades": losses.height,
        "win_rate": (
            wins.height / trades.height
        ),
        "average_win": (
            wins["net_pnl"].mean()
            if wins.height
            else 0
        ),
        "average_loss": (
            losses["net_pnl"].mean()
            if losses.height
            else 0
        ),
    }