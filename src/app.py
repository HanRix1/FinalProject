from fastapi import FastAPI
from auth.router import router as auth_router
from starlette_session import SessionMiddleware

from settings import AuthSettings, get_settings



def create_app():

    app = FastAPI()
    
    settings: AuthSettings = get_settings(AuthSettings)

    app.add_middleware(
        SessionMiddleware, 
        secret_key=settings.secret, 
        max_age=60,
        cookie_name="session_id"
    )
    
    app.include_router(auth_router)

    return app