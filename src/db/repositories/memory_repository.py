# repositories/memory_repository.py
"""
Repository for memory data, which is split between PostgreSQL and MongoDB.
"""
class MemoryRepository:
    def __init__(self, pg_session: AsyncSession, mongo_db: AsyncIOMotorDatabase):
        self.pg_session = pg_session
        self.mongo_db = mongo_db
        self.memories_collection = mongo_db.memories
    
    async def get_memory(self, memory_id: UUID) -> Memory:
        # Fetch metadata from PostgreSQL
        metadata = await self.pg_session.get(MemoryMetadata, memory_id)
        
        # Fetch content from MongoDB
        content = await self.memories_collection.find_one({"_id": str(memory_id)})
        
        # Combine and return
        return Memory.construct_from_dbs(metadata, content)