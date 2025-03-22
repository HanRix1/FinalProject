from typing import Annotated
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from auth.repository import UserRepository
from auth.services import UserService
from auth.utils import decode_jwt
from database.base import get_session




class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials | None = await super(
            JWTBearer, self
        ).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=403, 
                    detail="Invalid authentication scheme."
                )
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(
                    status_code=403, 
                    detail="Invalid token or expired token."
                )
            return decode_jwt(credentials.credentials)
        else:
            raise HTTPException(
                status_code=403, 
                detail="Invalid authorization code."
            )

    def verify_jwt(self, jwtoken: str) -> bool:
            isTokenValid: bool = False

            try:
                payload = decode_jwt(jwtoken)
            except:
                payload = None
            if payload:
                isTokenValid = True

            return isTokenValid
    
DataBaseSessionDep = Annotated[AsyncSession, Depends(get_session)]

def get_user_repo(session: DataBaseSessionDep) -> UserRepository:
    return UserRepository(session)

def get_user_service(user_repo: UserRepository = Depends(get_user_repo)) -> UserService:
    return UserService(user_repo)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
JWTBearerDep = Annotated[JWTBearer, Depends(JWTBearer())]