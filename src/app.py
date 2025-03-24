from fastapi import FastAPI
from auth.router import router as auth_router
from starlette_session import SessionMiddleware
from fastapi.openapi.utils import get_openapi

from settings import AuthSettings, get_settings


def custom_openapi(app: FastAPI):
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="My API",
        version="1.0",
        description="API, использующий авторизацию через сессии",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "SessionAuth": {
            "type": "apiKey",
            "in": "cookie",
            "name": "session_id"
        }
    }
    # openapi_schema["security"] = [{"SessionAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


def create_app():

    app = FastAPI()
    
    settings: AuthSettings = get_settings(AuthSettings)

    app.add_middleware(
        SessionMiddleware, 
        secret_key=settings.secret_key, 
        max_age=180,
        cookie_name="session_id"
    )
    
    app.include_router(auth_router)
    app.openapi = lambda: custom_openapi(app)

    return app