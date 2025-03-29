import pytest
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from auth.models import User
from auth.repository import UserRepository
from settings import DatabaseSettings, get_settings
from models import Base
from auth.schemas import UserSchema, UserLoginSchema, UserUpdateSchema
import pytest_asyncio


user_schema = UserSchema(
    name="Artem",
    email="example@mail.ru",
    password="password"
)

user_login_schema = UserLoginSchema(
    email="example@mail.ru",
    password="password"
)

user_updated_schema = UserUpdateSchema(
    new_name="Gosha"
)



@pytest_asyncio.fixture
async def test_engine():
    settings: DatabaseSettings = get_settings(DatabaseSettings)
    
    engine: AsyncEngine = create_async_engine(settings.async_url, echo=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()

@pytest_asyncio.fixture
async def test_session(test_engine):
    async_session = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        yield session
        
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(table.delete())
        await session.commit()

@pytest.mark.usefixtures("test_session")
class TestUserRepository:

    @pytest.fixture(autouse=True)
    def setup(self, test_session):
        self.user_repo = UserRepository(test_session)
        self.session = test_session

    @pytest_asyncio.fixture
    async def test_user(self):
        user_id = await self.user_repo.create_new_user(
            user=user_schema, 
            hashed_password="$2b$12$dobSy8jwHNsXO4y6GPHUU.LPn0FhzWyD7eea72JlkQc86z..nNTGy"
        )
    
        await self.session.commit()
    
        return user_id

    @pytest.mark.asyncio
    async def test_create_new_user(self):
        hashed_pw = "$2b$12$dobSy8jwHNsXO4y6GPHUU.LPn0FhzWyD7eea72JlkQc86z..nNTGy"
        user_id = await self.user_repo.create_new_user(
            user=user_schema, 
            hashed_password=hashed_pw)
        
        db_user = await self.session.get(User, user_id)
        assert db_user is not None
        assert db_user.name == user_schema.name
        assert db_user.email == user_schema.email
        assert db_user.password == hashed_pw

    @pytest.mark.asyncio
    async def test_get_user_by_email(self, test_user):
        user = await self.user_repo.get_user_by_email(email=user_schema.email)

        assert user.email == user_schema.email

    @pytest.mark.asyncio
    async def test_get_user_by_id(self, test_user):
        user = await self.user_repo.get_user_by_id(user_id=test_user)

        assert user.id == test_user

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("flag"),
        [
            (True),
            (False),
        ]
    )
    async def test_update_is_deleted(self, test_user, flag):
        user_id = await self.user_repo.update_is_deleted(
            user_id=test_user,
            flag=flag
        )

        db_user = await self.session.get(User, user_id)

        assert db_user is not None  
        assert db_user.is_deleted == flag

    @pytest.mark.asyncio
    async def test_update_user_data(self, test_user):
        updated_user = await self.user_repo.update_user_data(
            user_data=user_updated_schema,
            user_id=test_user
        )

        db_user = await self.session.get(User, updated_user.id)
        assert db_user is not None
        assert db_user.name == updated_user.name


