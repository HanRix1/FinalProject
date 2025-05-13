from starlette_session import SessionMiddleware
from starlette_session.backends import BackendType
from fastapi import FastAPI
from redis import Redis

from shared.settings import AuthSettings, get_settings

settings: AuthSettings = get_settings(AuthSettings)
redis_client = Redis(
    host=settings.redis_host, port=settings.redis_port
)  # хост и порт заменить на settings.host ...


def init_session_middleware(app: FastAPI):
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.secret_key,
        max_age=settings.ttl,
        cookie_name="session_id",
        backend_type=BackendType.redis,
        backend_client=redis_client,
    )
