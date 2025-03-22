from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from auth.dependencies import UserServiceDep, AuthServiceDep
from auth.schemas import UserLoginSchema, UserSchema, UserUpdateSchema


router = APIRouter(
    prefix="/users",
    tags=["users"],
)

@router.post("/signup")
async def create_user(request: Request, user: UserSchema, user_service: UserServiceDep) -> dict[str, str]:
    new_user_id = await user_service.register_user(user)
    request.session["user_id"] = str(new_user_id)
    return JSONResponse({"message": "Logged in"})

@router.post("/login")
async def user_login(request: Request, user: UserLoginSchema, user_service: UserServiceDep):
    user_id = await user_service.verify_user(user)
    request.session["user_id"] = str(user_id)
    return JSONResponse({"message": "Logged in"})

@router.delete("/delete")
async def delete_user(
    request: Request, 
    auth_service: AuthServiceDep, 
    user_service: UserServiceDep
):
    user_id = await auth_service.get_current_user(request)
    # deleted_user_id = await user_service.remove_user(user_id=user_id)
    return "Sucsess"

@router.patch("/update-user")
async def update_user(
    request: Request, 
    auth_service: AuthServiceDep, 
    user_service: UserServiceDep,
    user_update_data: UserUpdateSchema
):
    user_id = await auth_service.get_current_user(request)
    updated_user = await user_service.modernize_user(user_id=user_id, user_data=user_update_data)
    return updated_user
