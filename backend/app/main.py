import logging.config
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.const import CONFIG
from app.providers import fruitytag
from app.routers import accessory, location, login, user, export

@asynccontextmanager
async def lifespan(app: FastAPI):
    await fruitytag.setup()
    yield
    await fruitytag.shutdown()


app = FastAPI(lifespan=lifespan)

if CONFIG.cors:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CONFIG.cors.cors_origins,
        allow_credentials=CONFIG.cors.allow_credentials,
        allow_methods=CONFIG.cors.cors_methods,
        allow_headers=CONFIG.cors.cors_headers,
    )

app.include_router(
    accessory,
    prefix="/api/accessory",
)
app.include_router(
    location,
    prefix="/api/location",
)
app.include_router(
    login,
    prefix="/api/login",
)
app.include_router(
    user,
    prefix="/api/user",
)
app.include_router(
    export,
    prefix="/api/export",
)

app.mount("/", StaticFiles(directory=CONFIG.frontend.path, html=True), name="frontend")
