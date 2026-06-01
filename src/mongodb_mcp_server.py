"""MongoDB MCP Server for handling retail operations"""

import logging
from typing import Any, Dict, List, Optional
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import PyMongoError
from datetime import datetime
from src.config import settings
from src.utils import logger, generate_id, dict_to_mongo_doc

logger = logging.getLogger(__name__)


class MongoDBMCPServer:
    """MongoDB MCP Server for retail operations"""
    
    def __init__(self):
        """Initialize MongoDB connection"""
        self.client: Optional[MongoClient] = None
        self.db = None
        self.inventory_collection = None
        self.customers_collection = None
        self.orders_collection = None
        self.products_collection = None
        
    async def connect(self) -> bool:
        """Establish MongoDB connection"""
        try:
            self.client = MongoClient(settings.mongodb_uri)
            self.db = self.client[settings.mongodb_database]
            
            # Initialize collections
            self.inventory_collection = self.db[settings.mongodb_inventory_collection]
            self.customers_collection = self.db[settings.mongodb_customers_collection]
            self.orders_collection = self.db[settings.mongodb_orders_collection]
            self.products_collection = self.db["products"]
            
            # Create indexes for better query performance
            await self._create_indexes()
            
            # Test connection
            self.client.admin.command('ping')
            logger.info("MongoDB connection established successfully")
            return True
        except PyMongoError as e:
            logger.error(f"MongoDB connection failed: {str(e)}")
            return False
    
    async def disconnect(self) -> None:
        """Close MongoDB connection"""
        try:
            if self.client:
                self.client.close()
                logger.info("MongoDB connection closed")
        except PyMongoError as e:
            logger.error(f"Error closing MongoDB connection: {str(e)}")
    
    async def _create_indexes(self) -> None:
        """Create database indexes for better performance"""
        try:
            # Inventory indexes
            self.inventory_collection.create_index([("product_id", ASCENDING)])
            self.inventory_collection.create_index([("store_id", ASCENDING)])
            self.inventory_collection.create_index([("quantity", ASCENDING)])
            
            # Customer indexes
            self.customers_collection.create_index([("customer_id", ASCENDING)])
            self.customers_collection.create_index([("email", ASCENDING)])
            self.customers_collection.create_index([("loyalty_points", DESCENDING)])
            
            # Order indexes
            self.orders_collection.create_index([("order_id", ASCENDING)])
            self.orders_collection.create_index([("customer_id", ASCENDING)])
            self.orders_collection.create_index([("created_at", DESCENDING)])
            self.orders_collection.create_index([("status", ASCENDING)])
            
            # Product indexes
            self.products_collection.create_index([("product_id", ASCENDING)])
            self.products_collection.create_index([("sku", ASCENDING)])
            self.products_collection.create_index([("category", ASCENDING)])
            
            logger.info("Database indexes created successfully")
        except PyMongoError as e:
            logger.error(f"Error creating indexes: {str(e)}")
    
    # ============ INVENTORY OPERATIONS ============
    
    async def get_inventory_by_product(self, product_id: str, store_id: Optional[str] = None) -> List[Dict]:
        """Get inventory for a product across stores or in specific store"""
        try:
            query = {"product_id": product_id}
            if store_id:
                query["store_id"] = store_id
            
            results = list(self.inventory_collection.find(query))
            return [dict_to_mongo_doc(doc) for doc in results]
        except PyMongoError as e:
            logger.error(f"Error fetching inventory: {str(e)}")
            return []
    
    async def update_inventory(self, product_id: str, store_id: str, quantity_change: int) -> bool:
        """Update inventory quantity"""
        try:
            result = self.inventory_collection.update_one(
                {"product_id": product_id, "store_id": store_id},
                {"$inc": {"quantity": quantity_change}, "$set": {"last_counted": datetime.utcnow()}}
            )
            return result.modified_count > 0
        except PyMongoError as e:
            logger.error(f"Error updating inventory: {str(e)}")
            return False
    
    async def get_low_stock_items(self, store_id: Optional[str] = None) -> List[Dict]:
        """Get items below reorder level"""
        try:
            query = {"$expr": {"$lte": ["$quantity", "$reorder_level"]}}
            if store_id:
                query["store_id"] = store_id
            
            results = list(self.inventory_collection.find(query))
            return [dict_to_mongo_doc(doc) for doc in results]
        except PyMongoError as e:
            logger.error(f"Error fetching low stock items: {str(e)}")
            return []
    
    async def get_total_inventory_value(self) -> float:
        """Calculate total inventory value"""
        try:
            pipeline = [
                {
                    "$lookup": {
                        "from": "products",
                        "localField": "product_id",
                        "foreignField": "product_id",
                        "as": "product"
                    }
                },
                {
                    "$project": {
                        "value": {"$multiply": ["$quantity", {"$arrayElemAt": ["$product.price", 0]}]}
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total_value": {"$sum": "$value"}
                    }
                }
            ]
            
            result = list(self.inventory_collection.aggregate(pipeline))
            return result[0]["total_value"] if result else 0.0
        except PyMongoError as e:
            logger.error(f"Error calculating inventory value: {str(e)}")
            return 0.0
    
    # ============ CUSTOMER OPERATIONS ============
    
    async def create_customer(self, customer_data: Dict[str, Any]) -> bool:
        """Create new customer"""
        try:
            customer_data["customer_id"] = customer_data.get("customer_id", generate_id("cust"))
            customer_data["created_at"] = datetime.utcnow()
            customer_data["updated_at"] = datetime.utcnow()
            
            self.customers_collection.insert_one(dict_to_mongo_doc(customer_data))
            logger.info(f"Customer created: {customer_data['customer_id']}")
            return True
        except PyMongoError as e:
            logger.error(f"Error creating customer: {str(e)}")
            return False
    
    async def get_customer(self, customer_id: str) -> Optional[Dict]:
        """Retrieve customer by ID"""
        try:
            customer = self.customers_collection.find_one({"customer_id": customer_id})
            return dict_to_mongo_doc(customer) if customer else None
        except PyMongoError as e:
            logger.error(f"Error fetching customer: {str(e)}")
            return None
    
    async def get_customer_by_email(self, email: str) -> Optional[Dict]:
        """Retrieve customer by email"""
        try:
            customer = self.customers_collection.find_one({"email": email})
            return dict_to_mongo_doc(customer) if customer else None
        except PyMongoError as e:
            logger.error(f"Error fetching customer by email: {str(e)}")
            return None
    
    async def update_customer(self, customer_id: str, update_data: Dict[str, Any]) -> bool:
        """Update customer information"""
        try:
            update_data["updated_at"] = datetime.utcnow()
            result = self.customers_collection.update_one(
                {"customer_id": customer_id},
                {"$set": dict_to_mongo_doc(update_data)}
            )
            return result.modified_count > 0
        except PyMongoError as e:
            logger.error(f"Error updating customer: {str(e)}")
            return False
    
    async def get_customer_purchase_history(self, customer_id: str, limit: int = 10) -> List[Dict]:
        """Get customer purchase history"""
        try:
            orders = list(self.orders_collection.find(
                
