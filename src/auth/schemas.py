from pydantic import BaseModel, EmailStr, Field


class UserSchema(BaseModel):
    name: str
    email: str
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Kozhemyaka Artem Alexsandrovich",
                "email": "tvoyo_mblLo@mail.ru",
                "password": "password",
            }
        }


class UserLoginSchema(BaseModel):
    email: str
    password: str

    class Config:
        json_schema_extra = {
            "example": {"email": "tvoyo_mblLo@mail.ru", "password": "password"}
        }

class UserUpdateSchema(BaseModel):
    new_name: str