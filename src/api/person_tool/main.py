import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse, RedirectResponse

from person_tool.config import configure_logging, settings
from person_tool.jobs.views import router as job_router
from person_tool.lifespan import lifespan
from person_tool.middlewares.measure_response_time import add_process_time_header
from person_tool.system.views import router as system_router
from person_tool.users.views import router as user_router

configure_logging()


app: FastAPI = FastAPI(
    title=settings.app.name,
    version=settings.app.version,
    lifespan=lifespan,
    contact={"name": "Simon Lidwell", "email": "slidwell@gmail.com"},
    redoc_url=None,
)


app.middleware("http")(add_process_time_header)


@app.get("/", include_in_schema=False)
async def root() -> RedirectResponse:
    """Redirect users to the documentation"""
    return RedirectResponse("/docs")


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Display the people management favicon"""
    return FileResponse("assets/favicon.png")


app.include_router(
    user_router, prefix=f"{settings.app.base_api_url}/users", tags=["Users"]
)

app.include_router(
    job_router, prefix=f"{settings.app.base_api_url}/jobs", tags=["Jobs"]
)

app.include_router(
    system_router, prefix=f"{settings.app.base_api_url}/system", tags=["System"]
)


if __name__ == "__main__":
    uvicorn.run(
        "person_tool.main:app",
        host=settings.app.host,
        port=settings.app.port,
        reload=settings.app.reload,
        log_level=settings.app.log_level,
    )
