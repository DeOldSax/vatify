from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from core.config import settings

engine = create_async_engine(str(settings.DATABASE_URL), future=True, pool_pre_ping=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False, autoflush=False, autocommit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
