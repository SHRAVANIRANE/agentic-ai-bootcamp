from langchain_core.tools import tool
from app.services.data_service import DataService

_data_service = DataService()


@tool
def get_forecast_summary(store_id: str, product_id: str) -> str:
    """Get a 30-day demand forecast summary for a product in a store."""
    # Import here to avoid circular imports at module load
    from app.services.llm_service import LLMService
    from app.services.forecasting_service import ForecastingService
    import asyncio

    svc = ForecastingService(_data_service, LLMService())
    result = asyncio.run(svc.forecast(store_id, product_id, horizon_days=30))
    avg = sum(p.predicted_units for p in result.forecast) / len(result.forecast)
    return (
        f"30-day forecast for {product_id} at {store_id}: "
        f"avg {avg:.1f} units/day. Trend: {result.trend_summary}"
    )


@tool
def get_reorder_recommendation(store_id: str, product_id: str, current_inventory: int) -> str:
    """Get reorder recommendation with reasoning for a product."""
    from app.services.llm_service import LLMService
    from app.services.forecasting_service import ForecastingService
    from app.services.reorder_service import ReorderService
    import asyncio

    llm = LLMService()
    fs = ForecastingService(_data_service, llm)
    svc = ReorderService(_data_service, llm, fs)
    rec = asyncio.run(svc.recommend(store_id, product_id, current_inventory, lead_time_days=7))
    action = "REORDER NOW" if rec.reorder_now else "STOCK SUFFICIENT"
    return (
        f"{action} — Recommended qty: {rec.recommended_quantity} units. "
        f"Reorder point: {rec.reorder_point}. Reasoning: {rec.reasoning}"
    )


@tool
def list_available_products(store_id: str) -> str:
    """List all product IDs available for a given store."""
    products = _data_service.list_products(store_id)
    return f"Products in {store_id}: {', '.join(products[:20])}"
