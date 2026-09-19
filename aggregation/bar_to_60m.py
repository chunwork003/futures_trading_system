from .resample import resample_bars


def bar_to_60m(df):
    return resample_bars(df, "60m")