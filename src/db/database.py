"""
Database connection management.
Handles database session creation, migrations, and connection pooling.
"""
"""
Database connection management.
Handles database session creation, migrations, and connection pooling.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Callable, Optional

from sqlalchemy import event, inspect
from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                    async_sessionmaker, create_async_engine)
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool, QueuePool

from src.config import Settings

# Configure logger
logger = logging.getLogger(__name__)

settings = Settings()

# Engine configuration
if settings.DEBUG:
    # Use Echo SQL in debug mode
    engine_args = {
        "echo": True,
        "pool_pre_ping": True,
        "pool_size": 5,
        "max_overflow": 10,
        "poolclass": QueuePool,
    }
else:
    # Production settings
    engine_args = {
        "echo": False,
        "pool_pre_ping": True,
        "pool_size": 20,
        "max_overflow": 20,
        "poolclass": QueuePool,
        "pool_timeout": 30,  # 30 seconds
        "pool_recycle": 1800,  # 30 minutes
    }

# Create engines for async and sync operations
async_engine = create_async_engine(
    str(settings.SQLALCHEMY_DATABASE_URI), 
    **engine_args
)

# Create session factories
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database sessions"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_db_context() -> AsyncGenerator[AsyncSession, None]:
    """Context manager for getting async database sessions"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise


class DatabaseHelper:
    """Helper class for common database operations"""
    
    @staticmethod
    async def check_connection() -> bool:
        """Check if database connection is working"""
        try:
            async with async_engine.connect() as conn:
                await conn.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            return False
    
    @staticmethod
    async def get_db_info() -> dict:
        """Get database information"""
        async with async_engine.connect() as conn:
            info = {
                "dialect": async_engine.dialect.name,
                "driver": async_engine.dialect.driver,
                "pool_size": async_engine.pool.size(),
                "connections_in_use": async_engine.pool.checkedin(),
            }
            
            # Get PostgreSQL version
            if async_engine.dialect.name == "postgresql":
                result = await conn.execute("SELECT version();")
                version = await result.scalar()
                info["version"] = version
            
            return info
    
    @staticmethod
    async def execute_raw_sql(sql: str, params: Optional[dict] = None) -> list:
        """Execute raw SQL query"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(sql, params or {})
            return result.all()


# Database event listeners
@event.listens_for(async_engine.sync_engine, "connect")
def on_connect(dbapi_connection, connection_record):
    """Event fired when a connection is created"""
    logger.debug(f"Database connection established: {connection_record}")


@event.listens_for(async_engine.sync_engine, "checkout")
def on_checkout(dbapi_connection, connection_record, connection_proxy):
    """Event fired when a connection is checked out from the pool"""
    logger.debug(f"Database connection checkout: {connection_record}")


@event.listens_for(async_engine.sync_engine, "checkin")
def on_checkin(dbapi_connection, connection_record):
    """Event fired when a connection is checked back into the pool"""
    logger.debug(f"Database connection checkin: {connection_record}")


# Handle database initialization and shutdown
class DatabaseLifecycle:
    """Manage database lifecycle - startup and shutdown"""
    
    @staticmethod
    async def startup():
        """Tasks to run on application startup"""
        logger.info("Initializing database connection")
        if await DatabaseHelper.check_connection():
            logger.info("Database connection established successfully")
        else:
            logger.critical("Failed to establish database connection")
            raise Exception("Database connection failed")
    
    @staticmethod
    async def shutdown():
        """Tasks to run on application shutdown"""
        logger.info("Closing database connections")
        await async_engine.dispose()
        logger.info("Database connections closed")


# Transaction management
@asynccontextmanager
async def transaction(session: AsyncSession) -> AsyncGenerator[AsyncSession, None]:
    """Context manager for database transactions with automatic commit/rollback"""
    transaction = await session.begin()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await transaction.commit()