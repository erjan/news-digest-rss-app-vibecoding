from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from .settings import settings, to_async_database_url

_db_url, _ssl_required = to_async_database_url(settings.database_url)
_connect_args = {"ssl": True} if _ssl_required else {}
engine = create_async_engine(_db_url, connect_args=_connect_args)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession]:
    async with async_session_maker() as session:
        yield session
