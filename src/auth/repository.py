import asyncio
import uuid
from pydantic import EmailStr
from sqlalchemy import insert, select, delete, update

from auth.schemas import UserSchema, UserUpdateSchema
from auth.models import User
from sqlalchemy.ext.asyncio import AsyncSession

from uuid import UUID

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_new_user(self, user: UserSchema, hashed_password: str) -> UUID:
        query = (
            insert(User)
            .values(name=user.name, email=user.email, password=hashed_password)
            .returning(User.id)
        )

        user_id = (await self.session.execute(query)).scalar()
        await self.session.commit()
        
        return user_id

    async def get_user_by_email(self, email: EmailStr) -> User | None:
        query = (
            select(User)
            .where(User.email == email)
        )
        user = await self.session.scalar(query)
        return user
    
    async def get_user_by_id(self, user_id: UUID) -> User | None:
        query = (
            select(User)
            .where(User.id == user_id)
        )
        user = await self.session.scalar(query)
        return user
    
    async def update_is_deleted(self, user_id: UUID, flag: bool) -> UUID | None:
        query = (
            update(User)
            .where(User.id == user_id)
            .values(is_deleted=flag)
            .returning(User.id)
        )
        
        user_id = await self.session.scalar(query)
        await self.session.commit()
        
        return user_id

    async def update_user_data(self, user_data: UserUpdateSchema, user_id: UUID) -> User:
        query = (
            update(User)
            .where(User.id == user_id)
            .values(
                name=user_data.new_name
            )
            .returning(User)
        )
        result = await self.session.execute(query)
        await self.session.commit()
        updated_user = result.scalar_one_or_none() 
        
        return updated_user