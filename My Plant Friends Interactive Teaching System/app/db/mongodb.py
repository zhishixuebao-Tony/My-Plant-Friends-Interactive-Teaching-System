from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from typing import Any

class Database:
    client: Any = None
    db: Any = None

db_instance = Database()

async def connect_to_mongo():
    db_instance.client = AsyncIOMotorClient(settings.MONGODB_URL)
    db_instance.db = db_instance.client["composition_db"]
    print("✅ MongoDB 连接成功")

async def close_mongo_connection():
    if db_instance.client: db_instance.client.close()