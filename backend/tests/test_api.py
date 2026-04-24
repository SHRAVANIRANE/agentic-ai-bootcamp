import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock
from app.main import app


@pytest.fixture
def mock_forecast_service():
    from app.models.schemas import ForecastResponse, ForecastPoint
    from datetime import date
    mock_response = ForecastResponse(
        store_id="S001",
        product_id="P001",
        forecast=[ForecastPoint(date=date(2024, 1, 1), predicted_units=50.0, lower_bound=40.0, upper_bound=60.0)],
        trend_summary="Stable demand with slight upward trend.",
        seasonality_notes="Summer",
    )
    return mock_response


@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_forecast_endpoint(mock_forecast_service):
    with patch(
        "app.services.forecasting_service.ForecastingService.forecast",
        new_callable=AsyncMock,
        return_value=mock_forecast_service,
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                "/api/v1/forecast/",
                json={"store_id": "S001", "product_id": "P001", "horizon_days": 1},
            )
    assert resp.status_code == 200
    data = resp.json()
    assert data["store_id"] == "S001"
    assert len(data["forecast"]) == 1
