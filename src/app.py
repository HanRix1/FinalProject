from fastapi import FastAPI
from auth.admin import create_admin
from auth.router import router as auth_router
from events.router import router as event_router
from starlette_session import SessionMiddleware
from contextlib import asynccontextmanager
from settings import AuthSettings, get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_admin(app)  
    yield


def create_app():

    app = FastAPI(lifespan=lifespan)
    
    settings: AuthSettings = get_settings(AuthSettings)

    app.add_middleware(
        SessionMiddleware, 
        secret_key=settings.secret_key, 
        max_age=1800,
        cookie_name="session_id"
    )

    
    app.include_router(auth_router)
    app.include_router(event_router)

    return app