from pydantic import BaseModel, EmailStr, Field, ConfigDict, ValidationError
from typing import Annotated
from fastapi import Query


class UserSchema(BaseModel):
    name: Annotated[str, Field(min_length=2, max_length=20)]
    email: Annotated[EmailStr, Field()]
    password: Annotated[str, Field(min_length=4, max_length=100)]

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "name": "Kozhemyaka Artem Alexsandrovich",
            "email": "tvoyo_mblLo@mail.ru",
            "password": "password",
        }
    })


class UserLoginSchema(BaseModel):
    email: Annotated[EmailStr, Field()]
    password: Annotated[str, Field(min_length=4, max_length=100)]

    model_config = ConfigDict(json_schema_extra={
        "example": {"email": "tvoyo_mblLo@mail.ru", "password": "password"}
    })


class UserUpdateSchema(BaseModel):
    new_name: Annotated[str, Query(min_length=2, max_length=20)]


class RecoveryTokenSchema(BaseModel):
    token: Annotated[str, Query(min_length=32, max_length=128)]
