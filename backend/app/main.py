from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import get_settings
from app.core.logging import setup_logging
from app.api.routes import forecast, reorder, agent


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    setup_logging(settings.DEBUG)
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.APP_NAME,
        version="1.0.0",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(forecast.router, prefix="/api/v1")
    app.include_router(reorder.router, prefix="/api/v1")
    app.include_router(agent.router, prefix="/api/v1")

    @app.get("/health")
    def health():
        return {"status": "ok", "version": "1.0.0"}

    return app


app = create_app()
