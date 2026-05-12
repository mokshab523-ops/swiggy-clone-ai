from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import logging
from config import Config

logger = logging.getLogger(__name__)

class Database:
    """MongoDB Database Connection Manager"""
    
    _instance = None
    _client = None
    _db = None
    
    def __init__(self):
        if Database._instance is not None:
            raise Exception("Database instance already exists. Use get_instance() instead.")
        self.connect()
    
    @classmethod
    def get_instance(cls):
        """Get singleton instance of Database"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def connect(self):
        """Connect to MongoDB"""
        try:
            Database._client = MongoClient(
                Config.MONGO_URI,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
                retryWrites=True
            )
            
            # Test connection
            Database._client.admin.command('ping')
            Database._db = Database._client['swiggy_clone']
            
            logger.info("✓ Connected to MongoDB successfully")
            self.create_indexes()
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"✗ Failed to connect to MongoDB: {str(e)}")
            raise
    
    @classmethod
    def get_db(cls):
        """Get database instance"""
        if cls._db is None:
            cls.get_instance()
        return cls._db
    
    @classmethod
    def get_collection(cls, collection_name):
        """Get collection from database"""
        return cls.get_db()[collection_name]
    
    @classmethod
    def close(cls):
        """Close database connection"""
        if cls._client:
            cls._client.close()
            logger.info("✓ MongoDB connection closed")
    
    @classmethod
    def create_indexes(cls):
        """Create database indexes for optimization"""
        db = cls.get_db()
        
        try:
            # Users collection indexes
            db['users'].create_index('email', unique=True, sparse=True)
            db['users'].create_index('phone', unique=True, sparse=True)
            db['users'].create_index('created_at', expireAfterSeconds=None)
            
            # Orders collection indexes
            db['orders'].create_index('user_id')
            db['orders'].create_index('restaurant_id')
            db['orders'].create_index('status')
            db['orders'].create_index('created_at')
            db['orders'].create_index('delivery_partner_id', sparse=True)
            
            # Restaurants collection indexes
            db['restaurants'].create_index('name')
            db['restaurants'].create_index('category')
            db['restaurants'].create_index('location')
            db['restaurants'].create_index('rating')
            
            # Payments collection indexes
            db['payments'].create_index('order_id')
            db['payments'].create_index('user_id')
            db['payments'].create_index('status')
            db['payments'].create_index('transaction_id', unique=True, sparse=True)
            
            # Fraud Detection indexes
            db['fraud_alerts'].create_index('user_id')
            db['fraud_alerts'].create_index('timestamp')
            db['fraud_alerts'].create_index([('timestamp', -1)], expireAfterSeconds=2592000)  # 30 days
            
            logger.info("✓ Database indexes created successfully")
            
        except Exception as e:
            logger.warning(f"⚠ Error creating indexes: {str(e)}")
    
    @classmethod
    def health_check(cls):
        """Check database health"""
        try:
            cls.get_db().command('ping')
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return False

# Initialize database connection
db = Database.get_instance()