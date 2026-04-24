import pandas as pd
import numpy as np


class FeatureEngineer:
    """
    Builds ML-ready features from cleaned inventory data.
    Mirrors the feature set from the EDA notebook and extends it.
    """

    LAG_DAYS = [7, 14, 21, 28]
    ROLLING_WINDOWS = [7, 14, 28]

    def build(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy().sort_values("date")

        # Calendar features
        df["day_of_week"] = df["date"].dt.dayofweek
        df["month"] = df["date"].dt.month
        df["week_of_year"] = df["date"].dt.isocalendar().week.astype(int)
        df["quarter"] = df["date"].dt.quarter
        df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)

        # Lag features (demand signal from past weeks)
        for lag in self.LAG_DAYS:
            df[f"lag_{lag}d"] = df["units_sold"].shift(lag)

        # Rolling statistics (trend + volatility)
        for window in self.ROLLING_WINDOWS:
            df[f"rolling_mean_{window}d"] = df["units_sold"].shift(1).rolling(window).mean()
            df[f"rolling_std_{window}d"] = df["units_sold"].shift(1).rolling(window).std()

        # Price sensitivity
        df["price_discount_ratio"] = df["discount"] / (df["price"] + 1e-6)
        df["price_vs_competitor"] = df["price"] / (df["competitor_price"] + 1e-6)

        # Encode categoricals
        df["weather_encoded"] = df["weather_condition"].astype("category").cat.codes
        df["seasonality_encoded"] = df["seasonality"].astype("category").cat.codes

        df = df.dropna()
        return df

    def get_feature_columns(self) -> list[str]:
        lag_cols = [f"lag_{d}d" for d in self.LAG_DAYS]
        rolling_cols = [
            f"rolling_{stat}_{w}d"
            for stat in ["mean", "std"]
            for w in self.ROLLING_WINDOWS
        ]
        return [
            "day_of_week", "month", "week_of_year", "quarter", "is_weekend",
            "is_promotion", "price_discount_ratio", "price_vs_competitor",
            "weather_encoded", "seasonality_encoded",
            *lag_cols, *rolling_cols,
        ]
