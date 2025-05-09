from fastapi import FastAPI
from contextlib import asynccontextmanager

from auth.adimn import create_admin
from auth.router import router as auth_router
from shared.custom_middleware import init_session_middleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_admin(app)
    yield


def create_app():
    app = FastAPI(title="Auth Service", lifespan=lifespan)

    init_session_middleware(app)
    app.include_router(auth_router)
    return app
