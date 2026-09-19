from .resample import resample_bars


def bar_to_30m(df):
    return resample_bars(df, "30m")