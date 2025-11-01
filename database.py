"""
MongoDB connection and database operations
"""
import os
import logging
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Try to import pymongo, but don't fail if not available
try:
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, ConfigurationError
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False
    MongoClient = None
    ConnectionFailure = Exception
    ServerSelectionTimeoutError = Exception
    ConfigurationError = Exception

class Database:
    """MongoDB connection manager with graceful fallback"""
    
    def __init__(self):
        self.client = None
        self.db = None
        
        if not PYMONGO_AVAILABLE:
            logger.warning("⚠️  pymongo not installed - MongoDB features disabled")
            logger.warning("   Install with: pip install pymongo")
            logger.warning("   System will work with in-memory fallback")
            return
        
        mongo_uri = os.getenv("MONGO_URI")
        if not mongo_uri:
            logger.info("ℹ️  MONGO_URI not set - MongoDB features disabled")
            logger.info("   Set MONGO_URI in .env to enable persistence")
            return
        
        try:
            self.client = MongoClient(
                mongo_uri,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000
            )
            # Test connection
            self.client.admin.command('ping')
            
            # Extract database name from URI or use default
            db_name = self._extract_db_name(mongo_uri) or "wandersure"
            self.db = self.client[db_name]
            logger.info(f"✅ Connected to MongoDB successfully (database: {db_name})")
            
            # Create indexes
            self._create_indexes()
        except (ConnectionFailure, ServerSelectionTimeoutError, ConfigurationError) as e:
            logger.warning(f"⚠️  MongoDB connection failed: {e}")
            logger.warning("   System will work with in-memory fallback")
            self.client = None
            self.db = None
        except Exception as e:
            logger.warning(f"⚠️  Unexpected MongoDB error: {e}")
            logger.warning("   System will work with in-memory fallback")
            self.client = None
            self.db = None
    
    def _extract_db_name(self, uri: str) -> Optional[str]:
        """Extract database name from MongoDB URI"""
        try:
            # Parse URI like mongodb://host:port/dbname or mongodb+srv://user:pass@host/dbname
            if '/' in uri:
                # Get part after last /
                parts = uri.rsplit('/', 1)
                if len(parts) == 2:
                    db_part = parts[1]
                    # Remove query parameters if present
                    if '?' in db_part:
                        db_part = db_part.split('?')[0]
                    return db_part if db_part else None
        except:
            pass
        return None
    
    def is_connected(self) -> bool:
        """Check if database is connected"""
        if not self.client:
            return False
        try:
            self.client.admin.command('ping')
            return True
        except:
            return False
    
    def _create_indexes(self):
        """Create database indexes"""
        if not self.is_connected():
            return
        
        try:
            # User profiles indexes
            self.db.users.create_index("email", unique=True, sparse=True)
            self.db.users.create_index("instagram_username", unique=True, sparse=True)
            self.db.users.create_index("created_at")
            
            # Chat history indexes
            self.db.chat_history.create_index([("user_id", 1), ("created_at", -1)])
            self.db.chat_history.create_index("session_id", unique=True)
            self.db.chat_history.create_index("archived_at")
            
            # Claims cache indexes
            self.db.claims_cache.create_index([("destination", 1), ("updated_at", -1)])
            self.db.claims_cache.create_index("destination_normalized")
            
            logger.info("✅ Database indexes created")
        except Exception as e:
            logger.warning(f"Could not create indexes: {e}")
    
    def get_collection(self, name: str):
        """Get a MongoDB collection"""
        if not self.is_connected():
            return None
        return self.db[name]
    
    def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")

# Global database instance
db = Database()

