from fastapi import FastAPI
from auth.router import router as auth_router

def create_app():

    app = FastAPI()

    app.include_router(auth_router)

    return app