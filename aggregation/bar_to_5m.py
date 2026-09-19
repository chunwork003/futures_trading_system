from .resample import resample_bars


def bar_to_5m(df):
    return resample_bars(df, "5m")