from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.future import select
from config.settings import settings
from RBAC.models import Role

engine = create_async_engine(
    settings.database_url,
    echo=False,
    future=True
)

SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)

Base = declarative_base()

async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def initialize_roles():
    """
    Fetch roles from the database and store them in a global dictionary on server startup.
    """
    db = next(get_db())
    result = await db.execute(select(Role))
    roles = result.scalars().all()
    settings.roles = [
        {
            "id": role.id,
            "name": role.name,
            "description": role.description,
            "scope": role.scope,
        }
        for role in roles
    ]
    db.close()