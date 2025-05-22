"""
FastAPI application entry point.
Configures the API, mounts routers, and initializes middleware.
"""


#IMPORTS


import os
from functools import lru_cache
from uuid import UUID

from fastapi import AsyncIOMotorClient, AsyncSession, Depends, FastAPI, Router
from motor.motor_asyncio import AsyncIOMotorClient
import aiohttp
from sqlalchemy.ext.asyncio import create_async_engine

from src.config import Settings
from src.database import get_db
from src.exceptions import (BadRequest, Forbidden, HTTPException,
                            InternalServerError, NotFound, Unauthorized)
from src.pagination import (CursorPage, CursorPageParams, Page, PageParams,
                            cursor_paginate, paginate)

app = FastAPI()
router = Router()

@lru_cache()
def get_settings() -> Settings:
    """Create cached settings instance"""
    return Settings()


#### Set App environment
ENV = os.getenv("APP_ENV", "development")
settings = get_settings()
####

#### Access settings anywhere in your application
DB_URI = settings.SQLALCHEMY_DATABASE_URI
MAX_UPLOAD_SIZE_MB = settings.MAX_UPLOAD_SIZE_MB
####

# PostgreSQL connection pool
async_engine = create_async_engine(
    settings.POSTGRES_URI,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    pool_use_lifo=True,  # Last In First Out - reduces number of open connections
)

# MongoDB connection pool
mongo_client = AsyncIOMotorClient(
    settings.MONGO_URI,
    maxPoolSize=20,
    minPoolSize=5,
    maxIdleTimeMS=60000,
    connectTimeoutMS=5000,
)


# In FastAPI route
@router.get("/memories/{memory_id}")
async def get_memory(memory_id: UUID, db: AsyncSession = Depends(get_db)):
    memory = await db.get(Memory, memory_id)
    return memory

# With context manager
async def some_function():
    async with get_db_context() as db:
        # Work with database
        result = await db.execute(...)
    
    # Transaction context manager
    async with get_db_context() as db:
        async with transaction(db):
            # Changes automatically committed if no exception
            await db.add(new_object)