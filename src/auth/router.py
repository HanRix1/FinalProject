from fastapi import APIRouter, BackgroundTasks, Request
from fastapi.responses import JSONResponse
from fastapi_mail import FastMail, MessageSchema, MessageType

from auth.dependencies import UserServiceDep
from auth.schemas import (
    UserLoginSchema,
    UserSchema,
    UserUpdateSchema,
    RecoveryTokenSchema,
)
from auth.utils import conf
from shared.dependencies import AuthServiceDep

router = APIRouter(prefix="/users")


@router.post("/signup", tags=["auth"])
async def create_user(
    request: Request,
    user: UserSchema,
    user_service: UserServiceDep,
    auth_service: AuthServiceDep,
) -> dict[str, str]:
    new_user = await user_service.register_user(user)
    user_id = new_user.id
    user_role = new_user.role
    await auth_service.authorize_user(request=request, user_id=user_id, role=user_role)

    return JSONResponse({"message": "Logged in"})


@router.post("/login", tags=["auth"])
async def user_login(
    request: Request,
    user: UserLoginSchema,
    user_service: UserServiceDep,
    auth_service: AuthServiceDep,
):
    user = await user_service.verify_user(user)
    await auth_service.authorize_user(request=request, user_id=user.id, role=user.role)
    return JSONResponse({"message": "Logged in"})


@router.delete("/logout", tags=["auth"])
async def user_logout(request: Request, auth_service: AuthServiceDep):
    user_id = await auth_service.check_authorization(request=request)
    await auth_service.deauthorize_user(request=request, user_id=user_id)


@router.delete("/delete", tags=["management"])
async def delete_user(
    request: Request,
    auth_service: AuthServiceDep,
    user_service: UserServiceDep,
    background_tasks: BackgroundTasks,
) -> JSONResponse:
    user_id = await auth_service.check_authorization(request=request)
    token = await user_service.soft_delete_user(user_id=user_id)

    await auth_service.deauthorize_user(request=request, user_id=user_id)

    message = MessageSchema(
        subject="Recovery account token",
        recipients=["HanRix1@mail.ru"],
        body=str(token),
        subtype=MessageType.plain,
    )

    fm = FastMail(conf)
    background_tasks.add_task(fm.send_message, message)

    return JSONResponse(
        content={"message": "Account was deleted. Email to recovery been sent"},
        status_code=202,
    )


@router.patch("/update-user", tags=["management"])
async def update_user(
    request: Request,
    auth_service: AuthServiceDep,
    user_service: UserServiceDep,
    user_update_data: UserUpdateSchema,
):
    user_id = await auth_service.check_authorization(request)
    updated_user = await user_service.edit_user(
        user_id=user_id, user_data=user_update_data
    )
    return updated_user


@router.post("/revoke-delete-account", tags=["management"])
async def revoke_delete(
    request: Request,
    auth_service: AuthServiceDep,
    user_service: UserServiceDep,
    token: RecoveryTokenSchema,
) -> JSONResponse:
    user_id = await user_service.recover_account(token.token)
    await auth_service.authorize_user(request=request, user_id=str(user_id))
    return JSONResponse(content={"message": "Account was recover"}, status_code=201)
