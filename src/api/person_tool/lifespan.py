from contextlib import asynccontextmanager

from fastapi import FastAPI

from person_tool.db.core import people_management_db


# noinspection PyUnusedLocal
@asynccontextmanager
async def lifespan(app: FastAPI):
    await people_management_db.startup()
    try:
        yield
    finally:
        await people_management_db.shutdown()
