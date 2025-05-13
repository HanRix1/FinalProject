from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from auth.schemas import UserSchema, UserUpdateSchema
from shared.models.auth_models import Department, User, association_table
from shared.models.events_models import Meetings, meeting_participants


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_new_user(self, user: UserSchema, hashed_password: str) -> User:
        new_user = User(
            name=user.name,
            email=user.email,
            password=hashed_password,
        )
        self.session.add(new_user)
        await self.session.commit()

        await self.session.refresh(new_user)
        return new_user

    async def get_user_by_email(self, email: str) -> User | None:
        query = select(User).where(User.email == email)
        user = await self.session.scalar(query)
        return user

    async def get_user_by_id(self, user_id: UUID) -> User | None:
        query = select(User).where(User.id == user_id)
        user = await self.session.scalar(query)
        return user

    async def update_is_deleted(self, user_id: UUID, flag: bool) -> UUID | None:
        query = (
            update(User)
            .where(User.id == user_id)
            .values(is_deleted=flag)
            .returning(User.id)
        )
        result = await self.session.execute(query)
        await self.session.commit()
        user_id = result.scalar_one_or_none()

        return user_id

    async def update_user_data(
        self, user_data: UserUpdateSchema, user_id: UUID
    ) -> User:
        query = (
            update(User)
            .where(User.id == user_id)
            .values(name=user_data.new_name)
            .returning(User)
        )
        result = await self.session.execute(query)
        await self.session.commit()
        updated_user = result.scalar_one_or_none()

        return updated_user



def get_team_members_query(user_id: str):
    team_id_subq = (
        select(Department.team_id)
        .join(Department.employees)
        .where(User.id == user_id)
        .limit(1)
        .scalar_subquery()
    )

    stmt = (
        select(User)
        .distinct()
        .select_from(User)
        .join(User.departments)
        .where(Department.team_id == team_id_subq)
    )

    return stmt

def get_users_with_existing_meetings():
    query = (
        select(
            Meetings.start_at,
            Meetings.duration,
            User.id,
            User.name,
        )
        .join(Meetings.participants)
    )
    return query
