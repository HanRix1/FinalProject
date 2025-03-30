from typing import Annotated
from fastapi import Depends, FastAPI
from sqladmin import Admin, ModelView
from auth.dependencies import get_auth_service, get_user_service
from auth.schemas import UserLoginSchema
from auth.services import AuthService, UserService
from database.base import engine, get_session
from auth.models import User
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request


class AdminAuth(AuthenticationBackend):
    def __init__(self, user_service: UserService, auth_service: AuthService) -> None:
        self.middlewares = []
        self.user_user_service = user_service
        self.auth_service = auth_service
        
    async def login(self, request: Request) -> bool:
        form = await request.form()
        user_login = UserLoginSchema(
            email=form.get("username"), 
            password=form.get("password")
        )
        user_id = await self.user_user_service.verify_user(user=user_login)
        await self.auth_service.autorize_user(request=request, user_id=user_id)
        return True

    async def logout(self, request: Request) -> bool:
        user_id = await self.auth_service.check_autorization(request=request)
        await self.auth_service.deautorize_user(request=request, user_id=user_id)
        return True
    
    async def authenticate(self, request: Request) -> bool:
        user_id = request.session.get("user_id")
        if not user_id:
            return False

        return True

class UsersAdmin(ModelView, model=User):
    column_list = [
        'id', 'email'
    ]


def create_admin(app: FastAPI):
    auth_service = get_auth_service()
    user_service = get_user_service()
    authentication_backend = AdminAuth(user_service=user_service, auth_service=auth_service)
    admin = Admin(app=app, engine=engine, authentication_backend=authentication_backend)
    admin.add_view(UsersAdmin)
    return admin