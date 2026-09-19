def expectancy(
    win_rate: float,
    average_win: float,
    average_loss: float,
) -> float:

    return (
        win_rate * average_win
        + (1 - win_rate) * average_loss
    )