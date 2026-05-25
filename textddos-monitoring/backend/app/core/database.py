from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
from loguru import logger
from app.core.config import settings

# Global database client
client: AsyncIOMotorClient = None
database = None

async def connect_to_mongo():
    """Connect to MongoDB"""
    global client, database
    try:
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        database = client[settings.DATABASE_NAME]

        # Test connection
        await client.admin.command('ping')
        logger.info(f"Connected to MongoDB: {settings.DATABASE_NAME}")
        return True
    except ConnectionFailure as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error connecting to MongoDB: {e}")
        return False

async def close_mongo_connection():
    """Close MongoDB connection"""
    global client
    if client:
        client.close()
        logger.info("MongoDB connection closed")

async def get_database():
    """Get database instance"""
    if database is None:
        await connect_to_mongo()
    return database

async def get_collection(collection_name: str):
    """Get collection instance"""
    db = await get_database()
    return db[collection_name]

# Collections
async def get_flows_collection():
    return await get_collection("flows")

async def get_alerts_collection():
    return await get_collection("alerts")

async def get_rules_collection():
    return await get_collection("rules")

async def get_stats_collection():
    return await get_collection("stats")
