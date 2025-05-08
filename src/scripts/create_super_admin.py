import asyncio
import sys
from getpass import getpass
from pydantic import ValidationError
from sqlalchemy import select

from auth.schemas import UserSchema
from auth.utils import hash_password
from shared.models.auth_models import User, UsersRoles
from shared.database.base import get_session_ctx


async def create_superadmin():
    print("Создание супер-администратора...")

    email = input("Email: ")
    username = input("Username: ")
    password = getpass("Password: ")

    try:
        user_schema = UserSchema(name=username, email=email, password=password)
    except ValidationError as e:
        print(e)
        sys.exit(1)

    confirm_password = getpass("Confirm Password: ")

    if password != confirm_password:
        print("Пароли не совпадают!")
        sys.exit(1)

    async with get_session_ctx() as session:
        result = await session.execute(
            select(User).where(User.role == UsersRoles.SUPERADMIN)
        )
        if result.scalars().first():
            print("Супер-администратор уже существует!")
            sys.exit(1)

        hashed_password = await asyncio.to_thread(hash_password, user_schema.password)

        user = User(
            name=user_schema.name,
            email=user_schema.email,
            password=hashed_password,
            role=UsersRoles.SUPERADMIN,
        )
        session.add(user)
        await session.commit()

    print(f"Супер-админ {username} успешно создан!")


if __name__ == "__main__":
    asyncio.run(create_superadmin())
