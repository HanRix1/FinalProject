from contextlib import asynccontextmanager
from typing import AsyncIterator
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from shared.settings import DatabaseSettings, get_settings


meta = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    },
)


class Base(DeclarativeBase):
    metadata = meta


settings: DatabaseSettings = get_settings(DatabaseSettings)
engine: AsyncEngine = create_async_engine(settings.async_url)
async_session = async_sessionmaker(bind=engine, class_=AsyncSession)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with async_session() as session:
        yield session


@asynccontextmanager
async def get_session_ctx() -> AsyncIterator[AsyncSession]:
    session_gen = get_session()
    try:
        session = await anext(session_gen)
        yield session
    finally:
        await session_gen.aclose()
