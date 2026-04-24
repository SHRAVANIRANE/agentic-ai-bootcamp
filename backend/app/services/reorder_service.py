import numpy as np
from app.services.data_service import DataService
from app.services.llm_service import LLMService
from app.services.forecasting_service import ForecastingService
from app.models.schemas import ReorderRecommendation
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class ReorderService:
    """
    Computes reorder point, safety stock, and EOQ-based order quantity.
    Uses LLM to generate plain-language business reasoning.
    """

    def __init__(
        self,
        data_service: DataService,
        llm_service: LLMService,
        forecasting_service: ForecastingService,
    ):
        self.data_service = data_service
        self.llm_service = llm_service
        self.forecasting_service = forecasting_service
        self.settings = get_settings()

    async def recommend(
        self, store_id: str, product_id: str, current_inventory: int, lead_time_days: int
    ) -> ReorderRecommendation:
        df = self.data_service.get_product_data(store_id, product_id)

        # Historical demand stats
        daily_demand = df["units_sold"].mean()
        demand_std = df["units_sold"].std()

        # Safety stock = Z * σ_demand * √lead_time  (Z=1.65 for 95% service level)
        safety_stock = int(
            1.65 * demand_std * np.sqrt(lead_time_days) * self.settings.SAFETY_STOCK_MULTIPLIER
        )

        # Reorder point = (avg daily demand × lead time) + safety stock
        reorder_point = int(daily_demand * lead_time_days + safety_stock)

        # Forecast demand over lead time for recommended quantity
        forecast_resp = await self.forecasting_service.forecast(
            store_id, product_id, horizon_days=lead_time_days
        )
        forecasted_demand = sum(p.predicted_units for p in forecast_resp.forecast)

        # EOQ-inspired recommended quantity (cover lead time + safety stock buffer)
        recommended_qty = max(0, int(forecasted_demand + safety_stock - current_inventory))
        reorder_now = current_inventory <= reorder_point

        llm_context = {
            "store_id": store_id,
            "product_id": product_id,
            "current_inventory": current_inventory,
            "lead_time": lead_time_days,
            "forecasted_demand": forecasted_demand,
            "reorder_point": reorder_point,
            "safety_stock": safety_stock,
            "recommended_qty": recommended_qty,
        }
        reasoning = await self.llm_service.explain_reorder(llm_context)

        logger.info(
            "Reorder | store=%s product=%s reorder_now=%s qty=%d",
            store_id, product_id, reorder_now, recommended_qty,
        )

        return ReorderRecommendation(
            store_id=store_id,
            product_id=product_id,
            reorder_now=reorder_now,
            recommended_quantity=recommended_qty,
            reorder_point=reorder_point,
            safety_stock=safety_stock,
            reasoning=reasoning,
        )
