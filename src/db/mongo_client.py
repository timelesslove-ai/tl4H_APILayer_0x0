# database/mongodb.py
from motor.motor_asyncio import AsyncIOMotorClient
from motor.motor_asyncio import AsyncIOMotorDatabase
from src.config import Settings

settings = Settings()
mongo_client = AsyncIOMotorClient(
    settings.MONGO_URI,
    maxPoolSize=20,
    minPoolSize=5,
    maxIdleTimeMS=60000,
    connectTimeoutMS=5000,
)


async def get_mongo_db() -> AsyncIOMotorDatabase:
    return mongo_client[settings.MONGO_DB_NAME]