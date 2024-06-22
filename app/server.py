from fastapi import FastAPI
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from auth.router import router as auth_router
from db.connection import init_db


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


def create_app() -> FastAPI:
    app_ = FastAPI(
        title="Auth",
        description="Authentication APIs",
        version="1.0.0",
        middleware=make_middleware(),
    )
    init_routers(app_=app_)
    
    @app_.on_event("startup")
    async def startup_event():
        await init_db()
    return app_


app = create_app()