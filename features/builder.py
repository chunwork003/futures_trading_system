from __future__ import annotations

import polars as pl

from features.price import add_price_features
from features.trend import add_trend_features


class FeatureBuilder:
    def build(self, df: pl.DataFrame) -> pl.DataFrame:
        result = df.clone()

        result = add_price_features(result)
        result = add_trend_features(result)

        return result