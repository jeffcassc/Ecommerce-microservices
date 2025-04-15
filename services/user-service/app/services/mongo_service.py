from pymongo import MongoClient, ASCENDING
from pymongo.errors import PyMongoError, DuplicateKeyError
from app.config import Config
import logging
from bson import ObjectId
from datetime import datetime

logger = logging.getLogger(__name__)

class MongoDBService:
    def __init__(self):
        self.client = MongoClient(Config.MONGO_URI)
        self.db = self.client[Config.MONGO_DB_NAME]
        self.users_collection = self.db[Config.MONGO_USER_COLLECTION]
        self._create_indexes()
    
    def _create_indexes(self):
        try:
            # Índices para usuarios
            self.users_collection.create_index([("email", ASCENDING)], unique=True)
            self.users_collection.create_index([("phone", ASCENDING)], unique=True)
            logger.info("MongoDB indexes created successfully")
        except PyMongoError as e:
            logger.error(f"Error creating indexes: {str(e)}")
            raise
    
    def create_user(self, user_data: dict) -> str:
        try:
            user_data['created_at'] = datetime.utcnow()
            user_data['updated_at'] = datetime.utcnow()
            user_data['status'] = "ACTIVE"
            
            result = self.users_collection.insert_one(user_data)
            return str(result.inserted_id)
        except DuplicateKeyError as e:
            logger.warning(f"Duplicate user: {str(e)}")
            raise ValueError("User with this email or phone already exists")
        except PyMongoError as e:
            logger.error(f"Error creating user: {str(e)}")
            raise
    
    def get_user(self, user_id: str) -> dict:
        try:
            user = self.users_collection.find_one({"_id": user_id})
            if not user:
                raise ValueError("User not found")
            return user
        except PyMongoError as e:
            logger.error(f"Error getting user: {str(e)}")
            raise
    
    def get_user_by_email(self, email: str) -> dict:
        try:
            return self.users_collection.find_one({"email": email})
        except PyMongoError as e:
            logger.error(f"Error getting user by email: {str(e)}")
            raise
    
    def update_user(self, user_id: str, update_data: dict) -> bool:
        try:
            update_data['updated_at'] = datetime.utcnow()
            result = self.users_collection.update_one(
                {"_id": user_id},
                {"$set": update_data}
            )
            if result.modified_count == 0:
                raise ValueError("User not found or no changes made")
            return True
        except PyMongoError as e:
            logger.error(f"Error updating user: {str(e)}")
            raise
    
    def delete_user(self, user_id: str) -> bool:
        try:
            result = self.users_collection.delete_one({"_id": user_id})
            if result.deleted_count == 0:
                raise ValueError("User not found")
            return True
        except PyMongoError as e:
            logger.error(f"Error deleting user: {str(e)}")
            raise
    
    def list_users(self, skip: int = 0, limit: int = 10) -> list:
        try:
            users = list(self.users_collection.find().skip(skip).limit(limit))
            return users
        except PyMongoError as e:
            logger.error(f"Error listing users: {str(e)}")
            raise

mongo_service = MongoDBService()