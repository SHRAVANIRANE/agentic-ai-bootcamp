import asyncio
import numpy as np
from app.services.data_service import DataService
from app.services.llm_service import LLMService
from app.pipeline.xgboost_forecaster import XGBoostForecaster
from app.models.schemas import ForecastResponse, ForecastPoint, TrendExplanation
from app.core.logging import get_logger

logger = get_logger(__name__)


class ForecastingService:
    def __init__(self, data_service: DataService, llm_service: LLMService):
        self.data_service = data_service
        self.llm_service = llm_service
        self._model_cache: dict[str, XGBoostForecaster] = {}

    async def _get_model(self, store_id: str, product_id: str) -> XGBoostForecaster:
        key = f"{store_id}::{product_id}"
        if key not in self._model_cache:
            df = self.data_service.get_product_data(store_id, product_id)
            forecaster = XGBoostForecaster()
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, forecaster.train, df)
            self._model_cache[key] = forecaster
            logger.info("Trained and cached model for %s", key)
        return self._model_cache[key]

    async def forecast(
        self, store_id: str, product_id: str, horizon_days: int
    ) -> ForecastResponse:
        df = self.data_service.get_product_data(store_id, product_id)
        model = await self._get_model(store_id, product_id)
        result = model.forecast(df, horizon_days)

        forecast_points = [
            ForecastPoint(
                date=d.date(),
                predicted_units=round(p, 2),
                lower_bound=round(lb, 2),
                upper_bound=round(ub, 2),
            )
            for d, p, lb, ub in zip(
                result.dates, result.predictions, result.lower_bounds, result.upper_bounds
            )
        ]

        trend = self._detect_trend(result.predictions)
        top_drivers = sorted(result.shap_values, key=result.shap_values.get, reverse=True)[:3]

        llm_context = {
            "store_id": store_id,
            "product_id": product_id,
            "trend_direction": trend,
            "avg_demand": float(np.mean(result.predictions)),
            "peak_period": self._peak_period(result.dates, result.predictions),
            "top_drivers": ", ".join(top_drivers),
            "seasonality": df["seasonality"].mode()[0] if "seasonality" in df.columns else "unknown",
        }
        trend_summary = await self.llm_service.explain_trend(llm_context)
        seasonality_notes = df["seasonality"].mode()[0] if "seasonality" in df.columns else "N/A"

        return ForecastResponse(
            store_id=store_id,
            product_id=product_id,
            forecast=forecast_points,
            trend_summary=trend_summary,
            seasonality_notes=seasonality_notes,
        )

    async def explain_trends(self, store_id: str, product_id: str) -> TrendExplanation:
        df = self.data_service.get_product_data(store_id, product_id)
        model = await self._get_model(store_id, product_id)
        result = model.forecast(df, horizon_days=14)

        trend = self._detect_trend(result.predictions)
        top_drivers = sorted(result.shap_values, key=result.shap_values.get, reverse=True)[:5]

        llm_context = {
            "store_id": store_id,
            "product_id": product_id,
            "trend_direction": trend,
            "avg_demand": float(np.mean(result.predictions)),
            "peak_period": self._peak_period(result.dates, result.predictions),
            "top_drivers": ", ".join(top_drivers),
            "seasonality": df["seasonality"].mode()[0] if "seasonality" in df.columns else "unknown",
        }
        explanation = await self.llm_service.explain_trend(llm_context)

        return TrendExplanation(
            store_id=store_id,
            product_id=product_id,
            trend_direction=trend,
            seasonality_pattern=df["seasonality"].mode()[0] if "seasonality" in df.columns else "N/A",
            key_drivers=top_drivers,
            llm_explanation=explanation,
        )

    @staticmethod
    def _detect_trend(predictions: list[float]) -> str:
        if len(predictions) < 2:
            return "stable"
        slope = np.polyfit(range(len(predictions)), predictions, 1)[0]
        if slope > 0.5:
            return "upward"
        if slope < -0.5:
            return "downward"
        return "stable"

    @staticmethod
    def _peak_period(dates, predictions) -> str:
        if not dates:
            return "unknown"
        peak_idx = int(np.argmax(predictions))
        return str(dates[peak_idx].date())
