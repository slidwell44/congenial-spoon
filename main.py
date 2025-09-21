import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse, FileResponse

from config import configure_logging, settings
from lifespan import lifespan
from system.views import router as system_router

configure_logging()


app = FastAPI(
    title=settings.app.name,
    version=settings.app.version,
    lifespan=lifespan,
    contact={"name": "Simon Lidwell", "email": "slidwell@gmail.com"},
    redoc_url=None,
)


@app.get("/", include_in_schema=False)
async def root() -> RedirectResponse:
    """Redirect users to the documentation"""
    return RedirectResponse("/docs")


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Display the people management favicon"""
    return FileResponse("assets/favicon.png")


app.include_router(
    system_router, prefix=f"{settings.app.base_api_url}/system", tags=["System"]
)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.app.host,
        port=settings.app.port,
        reload=settings.app.reload,
        log_level=settings.app.log_level,
    )
