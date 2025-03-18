from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from auth.schemas import UserLoginSchema, UserSchema
from auth.utils import sign_jwt
from auth.models import User
from database import get_session


router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post("/signup")
async def create_user(user: UserSchema, session: Annotated[AsyncSession, Depends(get_session)]):
    query = (
        insert(User)
        .values(fullname=user.fullname, email=user.email, password=user.password)
        .returning(User.id)
    )
    user_id = (await session.execute(query)).scalar()
    await session.commit()
    return sign_jwt(user_id)


@router.post("/login")
async def user_login(user: UserLoginSchema, session: Annotated[AsyncSession, Depends(get_session)]):
    query = select(User.id).where(
        User.email == user.email, User.password == user.password
    )

    user_id = (await session.scalars(query)).one()
    if user_id:
        return sign_jwt(user_id)
    
    return {"error": "Wrong login details!"}