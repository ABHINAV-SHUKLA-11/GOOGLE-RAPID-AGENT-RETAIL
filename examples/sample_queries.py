"""
MongoDB Query Manager for Retail Agent
Provides standardized database access for the MCP Server
"""

from pymongo import MongoClient
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

class InventoryQueries:
    """Core class for all retail-related MongoDB operations"""
    
    def __init__(self):
        self.client = MongoClient(os.getenv("MONGODB_URI"))
        self.db = self.client[os.getenv("MONGODB_DATABASE")]
    
    # ===== INVENTORY QUERIES =====
    
    def get_low_stock_products(self, store_id: str, threshold: int = None):
        query = {
            "store_id": store_id,
            "quantity_on_hand": {"$lt": threshold or "$reorder_point"}
        }
        return list(self.db.inventory.find(query))
    
    def check_product_inventory(self, product_id: str, store_id: str):
        return self.db.inventory.find_one({
            "product_id": product_id,
            "store_id": store_id
        })
    
    def update_inventory(self, product_id: str, store_id: str, quantity_delta: int):
        result = self.db.inventory.update_one(
            {"product_id": product_id, "store_id": store_id},
            {
                "$inc": {"quantity_on_hand": quantity_delta},
                "$set": {"last_updated": datetime.now()}
            }
        )
        return result.modified_count > 0
    
    # ===== SALES VELOCITY & ANALYTICS =====
    
    def get_sales_velocity(self, product_id: str, days: int = 30):
        cutoff_date = datetime.now() - timedelta(days=days)
        pipeline = [
            {"$match": {"product_id": product_id, "sale_date": {"$gte": cutoff_date}}},
            {"$group": {
                "_id": "$product_id",
                "total_sales": {"$sum": "$quantity"},
                "avg_daily_sales": {"$avg": {"$cond": [{"$gte": ["$quantity", 0]}, "$quantity", 0]}},
                "days_of_data": {"$sum": 1}
            }}
        ]
        result = list(self.db.sales.aggregate(pipeline))
        return result[0] if result else None
    
    def predict_stockout_date(self, product_id: str, store_id: str):
        inventory = self.check_product_inventory(product_id, store_id)
        velocity = self.get_sales_velocity(product_id)
        
        if not inventory or not velocity or velocity['avg_daily_sales'] <= 0:
            return None
        
        daily_sales = velocity['avg_daily_sales']
        days_until_stockout = inventory['quantity_on_hand'] / daily_sales
        stockout_date = datetime.now() + timedelta(days=days_until_stockout)
        
        return {
            "product_id": product_id,
            "days_until_stockout": round(days_until_stockout, 1),
            "estimated_stockout_date": stockout_date.isoformat(),
            "critical": days_until_stockout < 2
        }
    
    # ===== PURCHASE ORDERS =====
    
    def create_purchase_order(self, product_id: str, quantity: int, supplier_id: str, store_id: str):
        po = {
            "order_id": f"PO-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "product_id": product_id,
            "quantity": quantity,
            "supplier_id": supplier_id,
            "store_id": store_id,
            "status": "PENDING",
            "created_at": datetime.now()
        }
        result = self.db.purchase_orders.insert_one(po)
        return po | {"_id": str(result.inserted_id)}
    
    # ===== ALERTS & HEALTH =====
    
    def create_alert(self, store_id: str, alert_type: str, message: str, product_id: str = None):
        alert = {
            "alert_id": f"ALERT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "store_id": store_id,
            "product_id": product_id,
            "alert_type": alert_type,
            "message": message,
            "status": "OPEN",
            "created_at": datetime.now()
        }
        result = self.db.alerts.insert_one(alert)
        return alert | {"_id": str(result.inserted_id)}

    def close_alert(self, alert_id: str):
        result = self.db.alerts.update_one(
            {"alert_id": alert_id},
            {"$set": {"status": "RESOLVED", "resolved_at": datetime.now()}}
        )
        return result.modified_count > 0

    def get_db_health(self):
        try:
            self.client.admin.command('ping')
            return {"status": "HEALTHY", "collections": self.db.list_collection_names()}
        except Exception:
            return {"status": "UNHEALTHY"}