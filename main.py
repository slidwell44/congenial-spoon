from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from config import configure_logging, settings
from db.core import service
from system.views import router as system_router

configure_logging()


# noinspection PyUnusedLocal,PyShadowingNames
@asynccontextmanager
async def lifespan(app: FastAPI):
    await service.startup()
    try:
        yield
    finally:
        await service.shutdown()


app = FastAPI(
    title=settings.app.name,
    version=settings.app.version,
    lifespan=lifespan,
)


@app.get("/")
async def root() -> RedirectResponse:
    return RedirectResponse("/docs")


app.include_router(system_router, prefix="/system")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
