from fastapi import Depends, FastAPI
from sqladmin import Admin, ModelView
from sqlalchemy import select
from auth.dependencies import get_auth_service, get_user_repo, get_user_service
from auth.repository import UserRepository
from auth.schemas import UserLoginSchema
from auth.services import AuthService, UserService
from database.base import engine, get_session_ctx
from auth.models import Roles, User
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
        user = await self.user_user_service.verify_user(user=user_login)
        await self.auth_service.autorize_user(request=request, user_id=user.id, role=user.role.title)
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
    column_exclude_list = ["password", "role_id"]
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"
    category = "accounts"

    def is_accessible(self, request):
        if request.session["user_role"] == "Администратор компании":
            return True
        else:
            return False    


class RolesAdmin(ModelView, model=Roles):
    column_list = "__all__"
    name = "Role"
    name_plural = "Roles"
    icon = "fa-solid fa-address-card"
    category = "accounts"

    # async def is_accessible(self, request):
    #     user_id = request.session.get("user_id")
    #     async with get_session_ctx() as session:
    #         query = (
    #             select(User.role)
    #             .where(User.id == user_id)
    #         )
    #         role = await session.scalar(query)
    #     return 
        
async def create_admin(app: FastAPI):
    async with get_session_ctx() as session:
        auth_service = AuthService()
        user_repo = UserRepository(session=session)
        user_service = UserService(user_repo=user_repo)
        authentication_backend = AdminAuth(user_service=user_service, auth_service=auth_service)
        
    admin = Admin(app=app, engine=engine, authentication_backend=authentication_backend)
    
    views = [UsersAdmin, RolesAdmin]
    for view in views:
        admin.add_view(view)
    return admin