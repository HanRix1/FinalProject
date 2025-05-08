import asyncio
import time
from uuid import UUID
from fastapi import HTTPException, status
import bcrypt

from auth.repository import UserRepository
from auth.schemas import UserLoginSchema, UserSchema, UserUpdateSchema
from auth.utils import generate_recovery_token, hash_password, decode_recovery_token
from shared.models.auth_models import User


class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def register_user(self, new_user: UserSchema) -> User:
        user = await self.user_repo.get_user_by_email(email=new_user.email)
        if user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Email already exists"
            )

        hashed_password = await asyncio.to_thread(hash_password, new_user.password)
        new_user = await self.user_repo.create_new_user(
            user=new_user,
            hashed_password=hashed_password,
        )

        return new_user

    async def verify_user(self, user: UserLoginSchema) -> User:
        db_user = await self.user_repo.get_user_by_email(email=user.email)

        if not db_user or not await asyncio.to_thread(
            bcrypt.checkpw,
            user.password.encode("utf-8"),
            db_user.password.encode("utf-8"),
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        return db_user

    async def soft_delete_user(self, user_id) -> str:
        db_user = await self.user_repo.get_user_by_id(user_id=user_id)

        if db_user.is_deleted:
            raise HTTPException(
                status_code=410,
                detail="User has been deleted. To revoke delete go to Email",
            )
        deleted_user_id = await self.user_repo.update_is_deleted(
            user_id=db_user.id, flag=True
        )
        token = await asyncio.to_thread(generate_recovery_token, deleted_user_id)

        return token

    async def modernize_user(self, user_id: UUID, user_data: UserUpdateSchema):
        db_user = await self.user_repo.get_user_by_id(user_id=user_id)

        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        updated_user = await self.user_repo.update_user_data(
            user_data=user_data, user_id=user_id
        )

        return updated_user

    async def recover_account(self, token: str) -> UUID:
        user_id, expiration_time = await asyncio.to_thread(decode_recovery_token, token)

        if float(expiration_time) < time.time():
            raise HTTPException(status_code=410, detail="Recovery token has expired")
        deleted_user_id = await self.user_repo.update_is_deleted(
            user_id=user_id, flag=False
        )

        return deleted_user_id
