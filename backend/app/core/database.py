"""
MongoDB Database Configuration and Connection
"""
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from loguru import logger

from app.core.config import settings
from app.models.daily_data import DailyData
from app.models.field_config import FieldConfig
from app.models.alert import Alert
from app.models.weekly_aggregate import WeeklyAggregate
from app.models.monthly_aggregate import MonthlyAggregate
from app.models.drone import DroneStatus, FlightRecord


class Database:
    """Database connection manager"""
    client: AsyncIOMotorClient = None
    db = None


db = Database()


async def init_db():
    """Initialize database connection and Beanie ODM"""
    try:
        db.client = AsyncIOMotorClient(settings.MONGODB_URL)
        db.db = db.client[settings.MONGODB_DB_NAME]
        
        # Initialize Beanie with document models
        await init_beanie(
            database=db.db,
            document_models=[
                DailyData,
                FieldConfig,
                Alert,
                WeeklyAggregate,
                MonthlyAggregate,
                DroneStatus,
                FlightRecord,
            ]
        )
        
        logger.info(f"Connected to MongoDB: {settings.MONGODB_DB_NAME}")
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise


async def close_db():
    """Close database connection"""
    if db.client:
        db.client.close()
        logger.info("MongoDB connection closed")


def get_database():
    """Get database instance"""
    return db.db
