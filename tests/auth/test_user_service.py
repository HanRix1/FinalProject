import time
from unittest.mock import AsyncMock, patch
import pytest

from auth.repository import UserRepository
from auth.services import UserService
from auth.schemas import UserSchema, UserLoginSchema, UserUpdateSchema
from shared.models.auth_models import User
from fastapi import HTTPException


@pytest.fixture(scope="session")
def mock_user_repository():
    return AsyncMock(spec=UserRepository)


fake_user = User(
    id="ee95ae0c-1bdb-46ec-b6b6-ca6c4a68c5ba",
    name="Artem",
    email="example@mail.ru",
    password="$2b$12$dobSy8jwHNsXO4y6GPHUU.LPn0FhzWyD7eea72JlkQc86z..nNTGy",
    is_deleted=False,
)

deleted_fake_user = User(
    id="ee95ae0c-1bdb-46ec-b6b6-ca6c4a68c5ba",
    name="Artem",
    email="example@mail.ru",
    password="$2b$12$dobSy8jwHNsXO4y6GPHUU.LPn0FhzWyD7eea72JlkQc86z..nNTGy",
    is_deleted=True,
)

user_schema = UserSchema(name="Artem", email="example@mail.ru", password="password")

user_login_schema = UserLoginSchema(email="example@mail.ru", password="password")

user_updated_schema = UserUpdateSchema(new_name="Gosha")


class TestUserSerice:
    @pytest.fixture(autouse=True)
    def set_up(self, mock_user_repository):
        self.user_service = UserService(mock_user_repository)
        self.user_repo = mock_user_repository

    @pytest.mark.parametrize(
        "user_data, existing_user, exeption",
        [
            (user_schema, fake_user, HTTPException),
            (user_schema, None, None),
        ],
    )
    @pytest.mark.asyncio
    async def test_register_user(self, user_data, existing_user, exeption):
        self.user_repo.get_user_by_email.return_value = existing_user
        self.user_repo.create_new_user.return_value = fake_user.id

        if exeption:
            with pytest.raises(exeption):
                await self.user_service.register_user(new_user=user_data)
        else:
            result = await self.user_service.register_user(new_user=user_data)

            assert result == fake_user.id

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "user_data, existing_user, exeption",
        [
            (user_login_schema, fake_user, None),
            (user_login_schema, None, HTTPException),
        ],
    )
    async def test_verify_user(self, user_data, existing_user, exeption):
        self.user_repo.get_user_by_email.return_value = existing_user

        if exeption:
            with pytest.raises(exeption):
                await self.user_service.verify_user(user=user_data)
        else:
            result = await self.user_service.verify_user(user=user_data)

            assert result == fake_user.id

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "existing_user, exeption",
        [
            (fake_user, None),
            (deleted_fake_user, HTTPException),
        ],
    )
    async def test_soft_delete_user(self, existing_user, exeption):
        self.user_repo.get_user_by_id.return_value = existing_user
        self.user_repo.update_is_deleted.return_value = existing_user.id

        if exeption:
            with pytest.raises(exeption):
                await self.user_service.soft_delete_user(user_id=existing_user.id)
        else:
            result = await self.user_service.soft_delete_user(user_id=existing_user.id)

            assert result

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("data_to_update", "existing_user", "exception"),
        [
            (user_updated_schema, fake_user, None),
            (user_updated_schema, None, HTTPException),
        ],
    )
    async def test_edit_user(self, data_to_update, existing_user: User, exception):
        self.user_repo.get_user_by_id.return_value = existing_user
        self.user_repo.update_user_data.return_value = existing_user

        if exception:
            with pytest.raises(exception):
                await self.user_service.edit_user(
                    user_id=fake_user.id, user_data=data_to_update
                )
        else:
            result = await self.user_service.edit_user(
                user_id=existing_user.id, user_data=data_to_update
            )

            assert result == existing_user

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("expiration_time", "user_id", "exception"),
        [
            (time.time() + 200, "ee95ae0c-1bdb-46ec-b6b6-ca6c4a68c5ba", None),
            (time.time(), "ee95ae0c-1bdb-46ec-b6b6-ca6c4a68c5ba", HTTPException),
        ],
    )
    async def test_recover_account(self, expiration_time, user_id, exception):
        def mock_decode_recovery_token(token):
            return user_id, expiration_time

        # Мокаем `asyncio.to_thread`, чтобы он возвращал наши данные
        with patch("asyncio.to_thread", side_effect=lambda func, *args: func(*args)):
            with patch(
                "auth.services.decode_recovery_token",
                side_effect=mock_decode_recovery_token,
            ):
                self.user_repo.update_is_deleted.return_value = user_id

                if exception:
                    with pytest.raises(exception):
                        await self.user_service.recover_account(token="token")
                else:
                    result = await self.user_service.recover_account(token="token")
                    assert result == user_id
