import polars as pl


def calculate_drawdown(
    equity: pl.Series,
) -> pl.Series:

    peak = equity.cum_max()

    return equity - peak