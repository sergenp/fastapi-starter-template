from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings

engine = create_async_engine(settings.DATABASE_URI.unicode_string(), echo=True, future=True)  # type: ignore # noqa

async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class SessionMaker:
    async def __aenter__(self) -> AsyncSession:
        self.session = async_session_maker()
        return self.session

    async def __aexit__(self, exc, exc_val, exc_tb):
        if exc:
            await self.session.rollback()

        await self.session.close()
