from datetime import time, timedelta, timezone
from fastapi import Depends, FastAPI, HTTPException
from sqladmin import Admin, ModelView
from sqlalchemy import select
from wtforms import SelectMultipleField
from auth.dependencies import get_auth_service, get_user_repo, get_user_service
from auth.repository import UserRepository
from auth.schemas import UserLoginSchema
from auth.services import AuthService, UserService
from database.base import engine, get_session_ctx
from auth.models import User, Team, Department
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from events.models import Marks, Meetings, Tasks
from wtforms.widgets import ListWidget, CheckboxInput
from starlette import status
from events.repository import get_team_members_query, get_users_with_existing_meetings


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
        await self.auth_service.autorize_user(request=request, user_id=user.id, role=user.role)
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
    column_exclude_list = ["password", "role_id", "department_id"]
    can_create = False
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"
    category = "accounts"

    # def is_accessible(self, request):
    #     if request.session["user_role"] == "Администратор компании":
    #         return True
    #     else:
    #         return False    


    # async def is_accessible(self, request):
    #     user_id = request.session.get("user_id")
    #     async with get_session_ctx() as session:
    #         query = (
    #             select(User.role)
    #             .where(User.id == user_id)
    #         )
    #         role = await session.scalar(query)
    #     return 

class TeamsAdmin(ModelView, model=Team):
    column_list = ["name", "departments", "description"]
    form_excluded_columns = [Team.departments]
    name = "Team"
    name_plural = "Teams"
    category = "accounts"

class DepartmentAdmin(ModelView, model=Department):
    column_list = ["team", "name", "employees", "description"]
    name = "Department"
    name_plural = "Departmens"
    category = "accounts"

class TasksAdmin(ModelView, model=Tasks):
    column_exclude_list = ["id", "assignee_id", "department_id"]
    name = "Task"
    name_plural = "Tasks"
    category = "Events"

    async def on_model_delete(self, model: Tasks, request: Request):
        deleted_task = Marks(
            task_description=model.description,
            task_deadline=model.deadline,
            assignee_id=model.assignee_id,
            assignee_rating=None
        )
        async with self.session_maker() as session:
            async with session.begin():
                session.add(deleted_task)

        await super().on_model_delete(model, request)


class MakrsAdmin(ModelView, model=Marks):
    column_exclude_list = ["id", "assignee_id"]
    name = "Mark"
    name_plural = "Makrs"
    category = "Events" 


class MeetingsAdmin(ModelView, model=Meetings):
    column_list = ["start_at", "duration", "theme", "participants"]
    
    def is_accessible(self, request):
        self.request = request
        return super().is_accessible(request)

    async def scaffold_form(self, rules = None):
        form_class = await super().scaffold_form(None)

        user_id = self.request.session.get("user_id")

        async with self.session_maker() as session:
            stmt = await get_team_members_query(user_id=user_id)

            result = await session.execute(stmt)
            users = result.scalars().all()            

        choices = [(str(user.id), user.name) for user in users]

        form_class.participants = SelectMultipleField(
            "Participants",
            choices=choices,
            widget=ListWidget(prefix_label=False),
            option_widget=CheckboxInput()
        )

        return form_class
    
    
    async def on_model_change(self, data, model: Meetings, is_created, request):
        if is_created:
            async with self.session_maker() as session:
                stmt = await get_users_with_existing_meetings()
                result = await session.execute(stmt)
                meetings = result.all()

            t = data["duration"]
            new_begin = data["start_at"].astimezone(timezone.utc)
            new_end = new_begin + timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
            new_user_ids = data["participants"]

            for start_at, duration, user_id, name in meetings:
                if str(user_id) not in new_user_ids:
                    continue
                
                
                existing_begin = start_at
                existing_end = start_at + timedelta(hours=duration.hour, minutes=duration.minute, seconds=duration.second)
                
                if not (new_end <= existing_begin or new_begin >= existing_end):
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=(
                            f"User {name} is already booked for another meeting "
                            f"from {existing_begin.isoformat()} to {existing_end.isoformat()}."
                        )
                    )

        return await super().on_model_change(data, model, is_created, request)


async def create_admin(app: FastAPI):
    async with get_session_ctx() as session:
        auth_service = AuthService()
        user_repo = UserRepository(session=session)
        user_service = UserService(user_repo=user_repo)
        authentication_backend = AdminAuth(user_service=user_service, auth_service=auth_service)
        
    admin = Admin(app=app, engine=engine, authentication_backend=authentication_backend)
    
    views = [UsersAdmin, TeamsAdmin, DepartmentAdmin, TasksAdmin, MakrsAdmin, MeetingsAdmin]
    for view in views:
        admin.add_view(view)
    return 

