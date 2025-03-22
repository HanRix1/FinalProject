from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth.repository import UserRepository
from auth.services import UserService, AuthService
from database.base import get_session

    
DataBaseSessionDep = Annotated[AsyncSession, Depends(get_session)]

def get_user_repo(session: DataBaseSessionDep) -> UserRepository:
    return UserRepository(session)

def get_user_service(user_repo: UserRepository = Depends(get_user_repo)) -> UserService:
    return UserService(user_repo)

def get_auth_service() -> AuthService:
    return AuthService()

UserServiceDep = Annotated[UserService, Depends(get_user_service)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]