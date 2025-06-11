from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from auth.routes import router as auth_router
from db.pg_connection import get_db, engine
from config.settings import settings
from utils.custom_logger import logger
from utils.utilities import get_auth_instance
from utils.permission_middleware import PermissionMiddleware, build_permissions, initialize_roles
from db.redis_connection import RedisClient

from organizations.routes import router as org_router
from teams.routes import router as teams_router
from roles.routes import router as roles_router
from permissions.routes import router as perm_router
from context.routes import router as context_router
from starlette.middleware.base import BaseHTTPMiddleware

class DBSessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        db_session = None
        db_gen = None
        try:
            # Get database session using the dependency
            db_gen = get_db()
            db_session = await anext(db_gen)
            request.state.db = db_session
            response = await call_next(request)
            return response
        except Exception as e:
            # If there's an error and we have a session, roll it back
            if db_session:
                await db_session.rollback()
            raise e
        finally:
            # Always close the session if we created one
            if db_session:
                await db_session.close()
            if db_gen is not None:
                await db_gen.aclose()


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
            secret_key="your-secret-key"
        ),
        Middleware(DBSessionMiddleware),
        Middleware(PermissionMiddleware)
    ]
    return middleware


def init_routers(app_: FastAPI) -> None:
    app_.include_router(auth_router)
    app_.include_router(context_router)
    app_.include_router(org_router)
    app_.include_router(teams_router)
    app_.include_router(perm_router)
    app_.include_router(roles_router)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await build_permissions()
    await initialize_roles()
    settings.auth_instance = await get_auth_instance()
    await RedisClient().connect()
    yield
    # Shutdown
    try:
        # Dispose of the database engine to close all connections
        await engine.dispose()
        # Close Redis connection
        redis_client = RedisClient()
        if hasattr(redis_client, 'redis') and redis_client.redis:
            await redis_client.redis.close()
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


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
