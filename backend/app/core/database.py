"""
Database configuration and session management
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Convert postgres:// to postgresql+asyncpg://
DATABASE_URL = settings.DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://')
DATABASE_IDENTITY_URL = settings.DATABASE_IDENTITY_URL.replace('postgresql://', 'postgresql+asyncpg://')

# Content Database Engine (for anonymous posts)
content_engine = create_async_engine(
    DATABASE_URL,
    echo=settings.DEBUG,
    poolclass=NullPool if settings.DEBUG else None,
)

# Identity Database Engine (for user authentication)
identity_engine = create_async_engine(
    DATABASE_IDENTITY_URL,
    echo=settings.DEBUG,
    poolclass=NullPool if settings.DEBUG else None,
)

# Session factories
ContentSessionLocal = async_sessionmaker(
    content_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

IdentitySessionLocal = async_sessionmaker(
    identity_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base classes for models
ContentBase = declarative_base()
IdentityBase = declarative_base()


async def init_db():
    """Initialize database tables"""
    try:
        async with content_engine.begin() as conn:
            await conn.run_sync(ContentBase.metadata.create_all)
        
        async with identity_engine.begin() as conn:
            await conn.run_sync(IdentityBase.metadata.create_all)
        
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


async def get_content_db() -> AsyncSession:
    """Dependency for content database sessions"""
    async with ContentSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_identity_db() -> AsyncSession:
    """Dependency for identity database sessions"""
    async with IdentitySessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
