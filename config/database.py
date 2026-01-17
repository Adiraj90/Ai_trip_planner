"""
Database configuration and connection management
"""
import mysql.connector
from mysql.connector import Error
import streamlit as st
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Manages database connections and operations"""
    
    def __init__(self):
        """Initialize database configuration from Streamlit secrets"""
        self.host = st.secrets["DB_HOST"]
        self.user = st.secrets["DB_USER"]
        self.password = st.secrets["DB_PASSWORD"]
        self.database = st.secrets["DB_NAME"]
        self.connection = None
        self.cursor = None
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                autocommit=False
            )
            
            if self.connection.is_connected():
                self.cursor = self.connection.cursor(dictionary=True)
                logger.info("Database connection established successfully")
                return True
            
        except Error as e:
            logger.error(f"Error connecting to database: {e}")
            st.error(f"Database connection failed: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection and self.connection.is_connected():
                self.connection.close()
                logger.info("Database connection closed")
        except Error as e:
            logger.error(f"Error closing database connection: {e}")
    
    def execute_query(self, query: str, params: tuple = None, fetch: bool = True):
        """
        Execute a SQL query
        
        Args:
            query: SQL query string
            params: Query parameters
            fetch: Whether to fetch results
            
        Returns:
            Query results or affected row count
        """
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            self.cursor.execute(query, params or ())
            
            if fetch:
                return self.cursor.fetchall()
            else:
                self.connection.commit()
                return self.cursor.rowcount
                
        except Error as e:
            logger.error(f"Error executing query: {e}")
            if self.connection:
                self.connection.rollback()
            raise e
    
    def execute_many(self, query: str, data: list):
        """
        Execute multiple queries with different parameters
        
        Args:
            query: SQL query string
            data: List of parameter tuples
            
        Returns:
            Number of affected rows
        """
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            self.cursor.executemany(query, data)
            self.connection.commit()
            return self.cursor.rowcount
            
        except Error as e:
            logger.error(f"Error executing multiple queries: {e}")
            if self.connection:
                self.connection.rollback()
            raise e
    
    def get_last_insert_id(self) -> Optional[int]:
        """Get the ID of the last inserted row"""
        try:
            return self.cursor.lastrowid
        except:
            return None


# Global database instance
_db_instance = None


def get_db() -> DatabaseConnection:
    """
    Get or create database connection instance
    
    Returns:
        DatabaseConnection instance
    """
    global _db_instance
    
    if _db_instance is None:
        _db_instance = DatabaseConnection()
        _db_instance.connect()
    
    return _db_instance


def test_connection() -> bool:
    """
    Test database connection
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        db = get_db()
        result = db.execute_query("SELECT 1 as test")
        return result[0]['test'] == 1
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False


if __name__ == "__main__":
    # Test the database connection
    print("Testing database connection...")
    if test_connection():
        print("✓ Database connection successful!")
    else:
        print("✗ Database connection failed!")