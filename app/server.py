from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from auth.router import router as auth_router
from db.connection import init_db
from config.settings import settings
from utils.utilities import get_auth_instance

from RBAC.routes.organization import router as org_router
from RBAC.routes.teams import router as teams_router
from RBAC.routes.roles import router as roles_router
from RBAC.routes.permissions import router as perm_router


def make_middleware() -> list[Middleware]:
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        ),
        Middleware(
            SessionMiddleware,
            secret_key="your-secret-key"  # Replace with a secure key
        )
    ]
    return middleware


def init_routers(app_: FastAPI) -> None:
    app_.include_router(auth_router)
    app_.include_router(org_router)
    app_.include_router(teams_router)
    app_.include_router(perm_router)
    app_.include_router(roles_router)


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
