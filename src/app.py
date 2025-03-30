from fastapi import FastAPI
from auth.admin import create_admin
from auth.router import router as auth_router
from starlette_session import SessionMiddleware
from contextlib import asynccontextmanager
import asyncio
from settings import AuthSettings, get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    await asyncio.to_thread(create_admin, app)  
    yield


def create_app():

    app = FastAPI(lifespan=lifespan)
    
    settings: AuthSettings = get_settings(AuthSettings)

    app.add_middleware(
        SessionMiddleware, 
        secret_key=settings.secret_key, 
        max_age=180,
        cookie_name="session_id"
    )

    
    app.include_router(auth_router)

    return app