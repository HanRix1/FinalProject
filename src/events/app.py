from fastapi import FastAPI

from events.router import router as event_router
from shared.custom_middleware import init_session_middleware


def create_app():
    app = FastAPI(title="Events Service")

    init_session_middleware(app)
    app.include_router(event_router)

    return app
