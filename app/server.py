from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from auth.router import router as auth_router
from RBAC.router import router as rbac_router
from db.connection import init_db
from config.settings import settings
from utils.utilities import get_auth_instance


def make_middleware() -> list[Middleware]:
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    ]
    return middleware


def init_routers(app_: FastAPI) -> None:
    app_.include_router(auth_router)
    app_.include_router(rbac_router)  # New router added


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup event
    await init_db()
    settings.auth_instance = await get_auth_instance()
    yield


def create_app() -> FastAPI:
    app_ = FastAPI(
        title="Auth",
        description="Authentication & Authorization",
        version="1.0.0",
        middleware=make_middleware(),
        lifespan=lifespan
    )
    init_routers(app_=app_)

    return app_


app = create_app()
