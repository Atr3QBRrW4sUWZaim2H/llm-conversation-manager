"""
Database connection management for LLM Conversation Manager.
"""
import os
import logging
from typing import Optional
from contextlib import contextmanager
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Database connection manager."""
    
    def __init__(self):
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = int(os.getenv("DB_PORT", "5432"))
        self.database = os.getenv("DB_NAME", "conversations")
        self.user = os.getenv("DB_USER", "your_user")
        self.password = os.getenv("DB_PASSWORD", "your_password")
        
    def get_connection_string(self) -> str:
        """Get PostgreSQL connection string."""
        return (
            f"host={self.host} "
            f"port={self.port} "
            f"dbname={self.database} "
            f"user={self.user} "
            f"password={self.password}"
        )
    
    def connect(self, cursor_factory=RealDictCursor):
        """Create a new database connection."""
        try:
            conn = psycopg2.connect(
                self.get_connection_string(),
                cursor_factory=cursor_factory
            )
            logger.info(f"Connected to database: {self.database}")
            return conn
        except psycopg2.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    @contextmanager
    def get_cursor(self, cursor_factory=RealDictCursor):
        """Context manager for database cursor."""
        conn = None
        cursor = None
        try:
            conn = self.connect(cursor_factory)
            cursor = conn.cursor()
            yield cursor
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    def test_connection(self) -> bool:
        """Test database connection."""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                return result[0] == 1
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False


# Global database connection instance
_db_connection = None


def get_db_connection() -> DatabaseConnection:
    """Get the global database connection instance."""
    global _db_connection
    if _db_connection is None:
        _db_connection = DatabaseConnection()
    return _db_connection


def setup_database():
    """Setup database schema."""
    db = get_db_connection()
    
    # Read and execute schema file
    schema_file = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'database_schema.sql')
    
    try:
        with open(schema_file, 'r') as f:
            schema_sql = f.read()
        
        with db.get_cursor() as cursor:
            cursor.execute(schema_sql)
            logger.info("Database schema setup completed")
            
    except Exception as e:
        logger.error(f"Failed to setup database schema: {e}")
        raise


if __name__ == "__main__":
    # Test database connection
    db = get_db_connection()
    if db.test_connection():
        print("✅ Database connection successful")
    else:
        print("❌ Database connection failed")
