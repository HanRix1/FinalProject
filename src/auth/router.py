from typing import Annotated
from fastapi import APIRouter, Depends, Query

from auth.dependencies import JWTBearerDep, UserServiceDep, JWTBearer
from auth.schemas import UserLoginSchema, UserSchema, UserUpdateSchema
from auth.utils import decode_jwt, sign_jwt
import asyncio

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

@router.post("/signup")
async def create_user(user: UserSchema, user_service: UserServiceDep) -> dict[str, str]:
    new_user_id = await user_service.register_user(user)
    jwt = await asyncio.to_thread(sign_jwt, new_user_id)
    return jwt

@router.post("/login")
async def user_login(user: UserLoginSchema, user_service: UserServiceDep):
    user_id = await user_service.verify_user(user)
    jwt = await asyncio.to_thread(sign_jwt, user_id)
    return jwt

@router.delete("/delete")
async def delete_user(jwt_bearer: JWTBearerDep, user_service: UserServiceDep):
    user_id = jwt_bearer["user_id"]
    deleted_user_id = await user_service.remove_user(user_id=user_id)
    return deleted_user_id

@router.patch("/update-user")
async def update_user(
    user_update_data: Annotated[UserUpdateSchema, Query()],
    jwt_bearer: JWTBearerDep, 
    user_service: UserServiceDep
):
    user_id = jwt_bearer["user_id"]
    updated_user = await user_service.modernize_user(user_id=user_id, user_data=user_update_data)
    return updated_user
