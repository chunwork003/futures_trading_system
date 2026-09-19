from .resample import resample_bars


def bar_to_15m(df):
    return resample_bars(df, "15m")