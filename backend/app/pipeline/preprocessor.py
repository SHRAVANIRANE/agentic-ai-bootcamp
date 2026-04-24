import pandas as pd
import numpy as np
from pathlib import Path
from app.core.logging import get_logger

logger = get_logger(__name__)


class DataPreprocessor:
    """Cleans and prepares raw retail inventory CSV for forecasting."""

    REQUIRED_COLS = {
        "Date", "Store ID", "Product ID", "Category", "Region",
        "Units Sold", "Inventory Level", "Price", "Discount",
        "Weather Condition", "Holiday/Promotion", "Competitor Pricing", "Seasonality",
    }

    def load(self, path: str | Path) -> pd.DataFrame:
        df = pd.read_csv(path)
        self._validate(df)
        return self._clean(df)

    def _validate(self, df: pd.DataFrame) -> None:
        missing = self.REQUIRED_COLS - set(df.columns)
        if missing:
            raise ValueError(f"Missing columns: {missing}")

    def _clean(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.rename(columns={
            "Store ID": "store_id",
            "Product ID": "product_id",
            "Units Sold": "units_sold",
            "Inventory Level": "inventory_level",
            "Weather Condition": "weather_condition",
            "Holiday/Promotion": "is_promotion",
            "Competitor Pricing": "competitor_price",
            "Demand Forecast": "demand_forecast",
            "Units Ordered": "units_ordered",
        })
        df.columns = [c.lower().replace(" ", "_") for c in df.columns]
        df = df.sort_values(["store_id", "product_id", "date"]).reset_index(drop=True)
        df["units_sold"] = df["units_sold"].clip(lower=0)
        logger.info("Loaded %d rows after cleaning", len(df))
        return df

    def filter_product(self, df: pd.DataFrame, store_id: str, product_id: str) -> pd.DataFrame:
        mask = (df["store_id"] == store_id) & (df["product_id"] == product_id)
        result = df[mask].copy()
        if result.empty:
            raise ValueError(f"No data for store={store_id}, product={product_id}")
        return result
