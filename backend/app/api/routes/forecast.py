from fastapi import APIRouter, Depends
from app.models.schemas import ForecastRequest, ForecastResponse, TrendExplanation
from app.services.forecasting_service import ForecastingService
from app.api.dependencies import get_forecasting_service

router = APIRouter(prefix="/forecast", tags=["Forecasting"])


@router.post("/", response_model=ForecastResponse)
async def get_forecast(
    req: ForecastRequest,
    service: ForecastingService = Depends(get_forecasting_service),
) -> ForecastResponse:
    return await service.forecast(req.store_id, req.product_id, req.horizon_days)


@router.get("/trends", response_model=TrendExplanation)
async def get_trends(
    store_id: str,
    product_id: str,
    service: ForecastingService = Depends(get_forecasting_service),
) -> TrendExplanation:
    return await service.explain_trends(store_id, product_id)
