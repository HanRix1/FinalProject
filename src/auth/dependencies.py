from typing import Annotated
from fastapi import Depends

from auth.repository import UserRepository
from auth.services import UserService
from shared.dependencies import DataBaseSessionDep


def get_user_repo(session: DataBaseSessionDep) -> UserRepository:
    return UserRepository(session)


def get_user_service(user_repo: UserRepository = Depends(get_user_repo)) -> UserService:
    return UserService(user_repo)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
