import asyncio
import time
from typing import Annotated
from uuid import UUID
import bcrypt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import APIKeyHeader
from auth.models import User
from auth.repository import UserRepository
from auth.schemas import UserLoginSchema, UserSchema, UserUpdateSchema
from auth.utils import generate_recovery_token, hash_password, decode_recovery_token


class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
        
    async def register_user(self, new_user: UserSchema) -> User:
        user = await self.user_repo.get_user_by_email(email=new_user.email)
        if user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists"
            )
        
        hashed_password = await asyncio.to_thread(hash_password, new_user.password)
        role_id = await self.user_repo.get_role_id_by_role_title(role_title="Администратор компании") # тут исправить !!! Вместо константы продумать регестрацию 
        new_user = await self.user_repo.create_new_user(
            user=new_user, 
            hashed_password=hashed_password, 
            role_id=role_id
        )

        return new_user
    
    async def verify_user(self, user: UserLoginSchema) -> User:
        db_user = await self.user_repo.get_user_by_email(email=user.email)

        if not db_user or not await asyncio.to_thread(
            bcrypt.checkpw,
            user.password.encode("utf-8"),
            db_user.password.encode("utf-8")
        ):
            raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )     
        return db_user
 
    async def soft_delete_user(self, user_id) -> str:
        db_user = await self.user_repo.get_user_by_id(user_id=user_id)

        if db_user.is_deleted:
            raise HTTPException(
                status_code=410,
                detail="User has been deleted. To revoke delete go to Email"
            )
        deleted_user_id = await self.user_repo.update_is_deleted(user_id=db_user.id, flag=True)
        token = await asyncio.to_thread(generate_recovery_token, deleted_user_id)

        return token
    
    async def modernize_user(self, user_id: UUID, user_data: UserUpdateSchema):
        db_user = await self.user_repo.get_user_by_id(user_id=user_id)

        if not db_user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        updated_user = await self.user_repo.update_user_data(user_data=user_data, user_id=user_id)
        
        return updated_user
        
    async def recover_account(self, token: str) -> UUID:
        user_id, expiration_time = await asyncio.to_thread(decode_recovery_token, token)

        if float(expiration_time) < time.time():
            raise HTTPException(
                status_code=410,
                detail="Recovery token has expired"
            )
        deleted_user_id = await self.user_repo.update_is_deleted(user_id=user_id, flag=False)

        return deleted_user_id



class AuthService:
    async def autorize_user(self, request: Request, user_id: UUID, role: str) -> None:
        session_data = request.session
        if "user_id" in session_data:
            raise HTTPException(
                status_code=401, 
                detail="User already autorize"
            )
        
        session_data["user_id"] = str(user_id)
        session_data["user_role"] = role

    async def deautorize_user(self, request: Request, user_id: str) -> None:
        session_data = request.session
        if "user_id" in session_data:
            del session_data["user_id"] 
            del session_data["user_role"]
            # Место для логгера
        else:
            # Место для логгера
            raise HTTPException(
                status_code=400,
                detail=f"User {user_id} is not currently authorized."
            )
        
    async def check_autorization(self, request: Request) -> str:
        session_data = request.session
        if "user_id" not in session_data:
            raise HTTPException(
                status_code=401, 
                detail="Unauthorized"
            )
        return session_data["user_id"]
    
