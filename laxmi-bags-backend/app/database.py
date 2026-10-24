import mysql.connector
from mysql.connector import pooling
from app.config import config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabasePool:
    _pool = None

    @classmethod
    def get_pool(cls):
        if cls._pool is None:
            try:
                cls._pool = pooling.MySQLConnectionPool(
                    pool_name="laxmi_pool",
                    pool_size=10,
                    host=config.DATABASE_HOST,
                    user=config.DATABASE_USER,
                    password=config.DATABASE_PASSWORD,
                    database=config.DATABASE_NAME
                )
                logger.info("Database connection pool created successfully")
            except Exception as e:
                logger.error(f"Error creating database pool: {e}")
                raise
        return cls._pool

    @classmethod
    def get_connection(cls):
        pool = cls.get_pool()
        return pool.get_connection()

def get_db_connection():
    return DatabasePool.get_connection()