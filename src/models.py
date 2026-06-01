"""Data models for MongoDB Retail Agent"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class OrderStatus(str, Enum):
    """Order status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class Product(BaseModel):
    """Product model"""
    product_id: str = Field(..., description="Unique product identifier")
    name: str = Field(..., description="Product name")
    category: str = Field(..., description="Product category")
    price: float = Field(..., description="Current price in USD", gt=0)
    cost: float = Field(..., description="Cost price in USD", gt=0)
    sku: str = Field(..., description="Stock Keeping Unit")
    description: Optional[str] = None
    image_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "product_id": "prod_001",
                "name": "Nike Air Max 90",
                "category": "Footwear",
                "price": 129.99,
                "cost": 70.00,
                "sku": "NIKE-AM90-001",
                "description": "Classic Nike Air Max 90 sneaker"
            }
        }


class Inventory(BaseModel):
    """Inventory model"""
    inventory_id: str = Field(..., description="Unique inventory identifier")
    product_id: str = Field(..., description="Product ID")
    store_id: str = Field(..., description="Store location ID")
    quantity: int = Field(..., description="Available quantity", ge=0)
    reorder_level: int = Field(..., description="Minimum stock level", ge=0)
    reorder_quantity: int = Field(..., description="Quantity to order when stock is low", gt=0)
    last_counted: datetime = Field(default_factory=datetime.utcnow)
    supplier_id: Optional[str] = None
    lead_time_days: int = Field(default=7, description="Days to receive new stock")

    class Config:
        json_schema_extra = {
            "example": {
                "inventory_id": "inv_001",
                "product_id": "prod_001",
                "store_id": "store_001",
                "quantity": 45,
                "reorder_level": 10,
                "reorder_quantity": 100,
                "lead_time_days": 5
            }
        }


class Customer(BaseModel):
    """Customer model"""
    customer_id: str = Field(..., description="Unique customer identifier")
    first_name: str = Field(..., description="Customer first name")
    last_name: str = Field(..., description="Customer last name")
    email: str = Field(..., description="Customer email address")
    phone: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    loyalty_points: int = Field(default=0, description="Accumulated loyalty points", ge=0)
    total_spent: float = Field(default=0.0, description="Total amount spent", ge=0)
    purchase_count: int = Field(default=0, description="Total number of purchases", ge=0)
    average_order_value: float = Field(default=0.0, ge=0)
    last_purchase_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_vip: bool = Field(default=False, description="VIP customer status")

    class Config:
        json_schema_extra = {
            "example": {
                "customer_id": "cust_001",
                "first_name": "John",
                "last_name": "Doe",
                "email": "john@example.com",
                "phone": "+1-555-0123",
                "city": "New York",
                "state": "NY",
                "country": "USA",
                "loyalty_points": 500,
                "total_spent": 2500.00,
                "is_vip": True
            }
        }


class Order(BaseModel):
    """Order model"""
    order_id: str = Field(..., description="Unique order identifier")
    customer_id: str = Field(..., description="Customer ID")
    store_id: str = Field(..., description="Store location ID")
    status: OrderStatus = Field(default=OrderStatus.PENDING)
    items: List[Dict[str, Any]] = Field(..., description="List of ordered items")
    subtotal: float = Field(..., description="Subtotal before tax", ge=0)
    tax: float = Field(..., description="Tax amount", ge=0)
    shipping: float = Field(default=0.0, description="Shipping cost", ge=0)
    total: float = Field(..., description="Total order amount", ge=0)
    discount: float = Field(default=0.0, description="Discount applied", ge=0)
    payment_method: str = Field(..., description="Payment method used")
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    estimated_delivery: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "order_id": "ord_001",
                "customer_id": "cust_001",
                "store_id": "store_001",
                "status": "processing",
                "items": [
                    {"product_id": "prod_001", "quantity": 2, "price": 129.99}
                ],
                "subtotal": 259.98,
                "tax": 20.80,
                "total": 280.78,
                "payment_method": "credit_card"
            }
        }


class AgentQuery(BaseModel):
    """Agent query request model"""
    query: str = Field(..., description="Natural language query for the agent")
    store_id: Optional[str] = None
    customer_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "query": "What is our current inventory for Nike Air Max shoes?",
                "store_id": "store_001",
                "context": {"filter": "active"}
            }
        }


class AgentResponse(BaseModel):
    """Agent response model"""
    query: str = Field(..., description="Original query")
    answer: str = Field(..., description="Agent's response")
    actions_taken: List[str] = Field(default_factory=list, description="Actions performed")
    data: Optional[Dict[str, Any]] = None
    confidence_score: float = Field(default=0.95, ge=0, le=1)
    execution_time_ms: float = Field(..., description="Time taken to process query")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "query": "What is our current inventory?",
                "answer": "Current inventory: 45 units of Nike Air Max across all stores.",
                "actions_taken": ["queried_inventory", "aggregated_results"],
                "confidence_score": 0.98,
                "execution_time_ms": 1250.5
            }
        }


class PricingUpdate(BaseModel):
    """Pricing update model"""
    product_id: str = Field(..., description="Product ID")
    new_price: float = Field(..., description="New price in USD", gt=0)
    reason: str = Field(..., description="Reason for price change")
    effective_date: Optional[datetime] = None
    store_id: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "product_id": "prod_001",
                "new_price": 99.99,
                "reason": "seasonal_discount",
                "effective_date": "2026-06-01"
            }
        }


class AnalyticsData(BaseModel):
    """Analytics data model"""
    period: str = Field(..., description="Analysis period (daily, weekly, monthly)")
    total_revenue: float = Field(..., description="Total revenue", ge=0)
    total_orders: int = Field(..., description="Total number of orders", ge=0)
    average_order_value: float = Field(..., description="Average order value", ge=0)
    top_products: List[Dict[str, Any]] = Field(default_factory=list)
    customer_metrics: Dict[str, Any] = Field(default_factory=dict)
    inventory_health: Dict[str, Any] = Field(default_factory=dict)
    generated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "period": "weekly",
                "total_revenue": 15000.00,
                "total_orders": 120,
                "average_order_value": 125.00,
                "top_products": [
                    {"product_id": "prod_001", "name": "Nike Air Max", "sales": 25}
                ]
            }
        }
