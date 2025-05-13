from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database.base import get_session
from shared.services import AuthService


def get_auth_service() -> AuthService:
    return AuthService()


DataBaseSessionDep = Annotated[AsyncSession, Depends(get_session)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
