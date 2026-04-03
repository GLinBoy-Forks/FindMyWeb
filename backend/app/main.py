import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles

from app.const import CONFIG
from app.providers import available_providers
from app.database import db
from app.routers import accessory, export, location, login, user

LOG = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    active_providers = dict()
    await db.setup()
    for provider_type, provider in available_providers.items():
        try:
            await provider.setup()
        except Exception as ex:
            LOG.error(f"Couldn't setup {provider}: {ex}")
            continue
        active_providers[provider_type] = provider
        await db.add_provider(provider_type, provider)
    yield
    for provider_type, provider in active_providers.items():
        try:
            await provider.shutdown()
        except Exception as ex:
            LOG.error(f"Couldn't shutdown {provider}: {ex}")
            continue
    await db.shutdown()


app = FastAPI(lifespan=lifespan)

if CONFIG.cors:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CONFIG.cors.cors_origins,
        allow_credentials=CONFIG.cors.allow_credentials,
        allow_methods=CONFIG.cors.cors_methods,
        allow_headers=CONFIG.cors.cors_headers,
        expose_headers=CONFIG.cors.expose_headers,
    )
if CONFIG.compression.enabled:
    app.add_middleware(GZipMiddleware, minimum_size=CONFIG.compression.minimum_size)

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
